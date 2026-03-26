<script setup lang="ts">
import {
    computed,
    onActivated,
    onDeactivated,
    onMounted,
    onUnmounted,
    ref,
    watch,
} from "vue";
import { useRoute, useRouter } from "vue-router";
import { getAutomationAction, listAutomationActions } from "../services/api";
import type {
    AutomationAction,
    LeftRightCompareActionConfig,
    LeftRightCompareResult,
} from "../types/automation";

const props = defineProps<{
    profileId: string;
    profileUsername?: string | null;
}>();

const route = useRoute();
const router = useRouter();

const currentAction = ref<AutomationAction | null>(null);
const loadError = ref<string | null>(null);
const loading = ref(false);
let pollTimeout: ReturnType<typeof setTimeout> | null = null;

const matrixFilter = ref<"all" | "missing" | "following">("all");
const graphRelationMode = ref<"both" | "missing" | "following">("both");
const compactMatrixMode = ref(false);
const showUniversallyMissingOnly = ref(false);
const rightPage = ref(1);
const rightPageSize = ref(25);
const graphLeftLimit = ref(16);
const graphRightLimit = ref(80);

const actionId = computed(() => {
    const value = route.params.actionId;
    return typeof value === "string" ? value : "";
});

const isResultsRouteActive = computed(
    () => route.name === "automation-left-right-compare-results",
);

const comparisonResult = computed<LeftRightCompareResult | null>(() => {
    const action = currentAction.value;
    if (!action?.config) {
        return null;
    }
    const config = action.config as LeftRightCompareActionConfig;
    return config.comparison_result ?? null;
});

const comparisonRows = computed(() => comparisonResult.value?.left_rows ?? []);
const comparisonRightTargets = computed(
    () => comparisonResult.value?.right_targets ?? [],
);
const comparisonTotals = computed(
    () =>
        comparisonResult.value?.totals ?? {
            left_total: 0,
            right_total: 0,
            relations_total: 0,
            follows_total: 0,
            missing_total: 0,
            unresolved_total: 0,
        },
);

const coveragePercent = computed(() => {
    const totals = comparisonTotals.value;
    if (!totals.relations_total) return 0;
    return Math.round((totals.follows_total / totals.relations_total) * 100);
});

const isActionInProgress = computed(() =>
    ["queued", "running"].includes(currentAction.value?.status || ""),
);

const actionProgressPercent = computed(() => {
    const action = currentAction.value;
    if (!action?.total_items) {
        return action?.status === "queued" ? 0 : 0;
    }
    return Math.round((action.completed_items / action.total_items) * 100);
});

function targetIdentityKey(target: {
    identity_key: string | null;
    normalized_user_id?: string | null;
    normalized_username?: string | null;
    raw_input?: string | null;
}): string {
    return String(
        target.identity_key ||
            target.normalized_user_id ||
            target.normalized_username ||
            target.raw_input ||
            "",
    );
}

const connectionMap = computed(() => {
    const map = new Map<
        string,
        Map<string, { is_following: boolean; resolved: boolean }>
    >();
    for (const row of comparisonRows.value) {
        const rowMap = new Map<
            string,
            { is_following: boolean; resolved: boolean }
        >();
        for (const c of row.connections) {
            const key = String(
                c.right_identity_key ||
                    c.right_user_id ||
                    c.right_display ||
                    "",
            );
            if (!key) continue;
            rowMap.set(key, {
                is_following: !!c.is_following,
                resolved: !!c.resolved,
            });
        }
        map.set(row.left_item_id, rowMap);
    }
    return map;
});

const sortedRows = computed(() =>
    [...comparisonRows.value].sort((a, b) => b.missing_count - a.missing_count),
);

function matrixCellStatus(leftItemId: string, rightIdentityKey: string | null) {
    const key = String(rightIdentityKey || "");
    if (!key) {
        return "missing";
    }
    const rowMap = connectionMap.value.get(leftItemId);
    const entry = rowMap?.get(key);
    if (!entry) {
        return "missing";
    }
    if (!entry.resolved) {
        return "missing";
    }
    return entry.is_following ? "following" : "missing";
}

const universallyMissingRightKeySet = computed(() => {
    const keySet = new Set<string>();
    if (!comparisonRows.value.length || !comparisonRightTargets.value.length) {
        return keySet;
    }

    for (const target of comparisonRightTargets.value) {
        const key = targetIdentityKey(target);
        if (!key) continue;
        const allMissing = comparisonRows.value.every(
            (row) => matrixCellStatus(row.left_item_id, key) === "missing",
        );
        if (allMissing) {
            keySet.add(key);
        }
    }

    return keySet;
});

const universallyMissingCount = computed(
    () => universallyMissingRightKeySet.value.size,
);

const filteredRightTargets = computed(() => {
    if (!showUniversallyMissingOnly.value) {
        return comparisonRightTargets.value;
    }

    const missingSet = universallyMissingRightKeySet.value;
    return comparisonRightTargets.value.filter((target) =>
        missingSet.has(targetIdentityKey(target)),
    );
});

const effectiveRightPageSize = computed(() =>
    compactMatrixMode.value ? 60 : rightPageSize.value,
);

const rightPages = computed(() =>
    Math.max(
        1,
        Math.ceil(
            filteredRightTargets.value.length / effectiveRightPageSize.value,
        ),
    ),
);

const pagedRightTargets = computed(() => {
    const start = (rightPage.value - 1) * effectiveRightPageSize.value;
    return filteredRightTargets.value.slice(
        start,
        start + effectiveRightPageSize.value,
    );
});

const compactModeRecommended = computed(
    () => comparisonRightTargets.value.length >= 250,
);

function shouldDisplayCell(status: "following" | "missing") {
    if (matrixFilter.value === "all") return true;
    return matrixFilter.value === status;
}

watch([filteredRightTargets, effectiveRightPageSize], () => {
    if (rightPage.value > rightPages.value) {
        rightPage.value = rightPages.value;
    }
    if (rightPage.value < 1) {
        rightPage.value = 1;
    }
});

const graphRows = computed(() =>
    sortedRows.value.slice(0, graphLeftLimit.value),
);
const graphTargets = computed(() =>
    filteredRightTargets.value.slice(0, graphRightLimit.value),
);

const graphHeight = computed(() =>
    Math.max(
        420,
        Math.max(graphRows.value.length, graphTargets.value.length) * 38 + 100,
    ),
);

function nodeY(index: number, total: number, height: number) {
    if (total <= 1) return height / 2;
    return 56 + (index * (height - 112)) / (total - 1);
}

const graphLeftNodes = computed(() =>
    graphRows.value.map((row, index) => ({
        id: row.left_item_id,
        label:
            row.left_display ||
            row.left_raw_input ||
            row.left_user_id ||
            "left",
        y: nodeY(index, graphRows.value.length, graphHeight.value),
    })),
);

const graphRightNodes = computed(() =>
    graphTargets.value.map((target, index) => ({
        id: targetIdentityKey(target) || String(index),
        identity_key: targetIdentityKey(target),
        label:
            target.display_username ||
            target.normalized_username ||
            target.normalized_user_id ||
            target.raw_input,
        y: nodeY(index, graphTargets.value.length, graphHeight.value),
    })),
);

const graphEdges = computed(() => {
    const leftIndex = new Map(
        graphLeftNodes.value.map((node) => [node.id, node]),
    );
    const rightIndex = new Map(
        graphRightNodes.value.map((node) => [node.identity_key, node]),
    );
    const edges: {
        x1: number;
        y1: number;
        x2: number;
        y2: number;
        kind: "following" | "missing";
    }[] = [];

    for (const row of graphRows.value) {
        const leftNode = leftIndex.get(row.left_item_id);
        if (!leftNode) continue;

        for (const c of row.connections) {
            const kind = c.is_following ? "following" : "missing";
            if (
                graphRelationMode.value !== "both" &&
                graphRelationMode.value !== kind
            ) {
                continue;
            }
            const key = String(
                c.right_identity_key ||
                    c.right_user_id ||
                    c.right_display ||
                    "",
            );
            const rightNode = rightIndex.get(key);
            if (!rightNode) continue;
            edges.push({
                x1: 260,
                y1: leftNode.y,
                x2: 920,
                y2: rightNode.y,
                kind,
            });
        }
    }

    return edges;
});

async function loadActionById(candidateActionId: string) {
    loading.value = true;
    loadError.value = null;
    try {
        const action = await getAutomationAction(candidateActionId);
        currentAction.value = action;
        if (["queued", "running"].includes(action.status)) {
            schedulePoll(action.action_id);
        }
    } catch (err: unknown) {
        loadError.value =
            err instanceof Error
                ? err.message
                : "Failed to load compare result";
    } finally {
        loading.value = false;
    }
}

async function loadLatestAction() {
    loading.value = true;
    loadError.value = null;
    try {
        const response = await listAutomationActions();
        const latest = response.actions
            .filter((action) => action.action_type === "left_right_compare")
            .sort(
                (a, b) =>
                    Date.parse(b.update_date || b.create_date) -
                    Date.parse(a.update_date || a.create_date),
            )[0];

        if (!latest) {
            currentAction.value = null;
            return;
        }

        currentAction.value = latest;
        if (isResultsRouteActive.value && !actionId.value) {
            await router.replace({
                name: "automation-left-right-compare-results",
                params: { actionId: latest.action_id },
            });
        }
        if (["queued", "running"].includes(latest.status)) {
            schedulePoll(latest.action_id);
        }
    } catch (err: unknown) {
        loadError.value =
            err instanceof Error
                ? err.message
                : "Failed to load compare result";
    } finally {
        loading.value = false;
    }
}

function schedulePoll(candidateActionId: string) {
    if (!isResultsRouteActive.value) return;
    if (pollTimeout) clearTimeout(pollTimeout);
    pollTimeout = setTimeout(() => poll(candidateActionId), 2500);
}

async function poll(candidateActionId: string) {
    try {
        const action = await getAutomationAction(candidateActionId);
        currentAction.value = action;
        if (["queued", "running"].includes(action.status)) {
            schedulePoll(candidateActionId);
        }
    } catch {
        schedulePoll(candidateActionId);
    }
}

function goBack() {
    if (pollTimeout) {
        clearTimeout(pollTimeout);
        pollTimeout = null;
    }
    void router.push({ name: "automation-left-right-compare" });
}

function openHistory() {
    void router.push({ name: "automation-left-right-compare-history" });
}

function clearPollTimer() {
    if (!pollTimeout) return;
    clearTimeout(pollTimeout);
    pollTimeout = null;
}

function exportResultJson() {
    const payload = comparisonResult.value;
    if (!payload) return;
    const blob = new Blob([JSON.stringify(payload, null, 2)], {
        type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `left_right_compare_${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
}

function exportResultCsv() {
    const rows = comparisonRows.value;
    const rights = comparisonRightTargets.value;
    if (!rows.length || !rights.length) return;

    const headers = [
        "left_profile",
        ...rights.map((r) => r.display_username || r.raw_input),
    ];
    const lines = [
        headers.map((h) => `"${String(h).replace(/"/g, '""')}"`).join(","),
    ];

    for (const row of rows) {
        const values: string[] = [
            row.left_display || row.left_raw_input || row.left_user_id || "",
        ];
        for (const right of rights) {
            const status = matrixCellStatus(
                row.left_item_id,
                targetIdentityKey(right),
            );
            values.push(status === "following" ? "1" : "0");
        }
        lines.push(
            values.map((v) => `"${String(v).replace(/"/g, '""')}"`).join(","),
        );
    }

    const blob = new Blob([lines.join("\n")], {
        type: "text/csv;charset=utf-8;",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `left_right_compare_${Date.now()}.csv`;
    a.click();
    URL.revokeObjectURL(url);
}

watch(
    actionId,
    (value) => {
        clearPollTimer();
        if (!isResultsRouteActive.value) {
            return;
        }
        if (value) {
            void loadActionById(value);
            return;
        }
        void loadLatestAction();
    },
    { immediate: true },
);

onMounted(() => {
    if (!isResultsRouteActive.value) {
        return;
    }
    if (!actionId.value) {
        void loadLatestAction();
    }
});

onActivated(() => {
    if (!isResultsRouteActive.value) {
        return;
    }
    if (actionId.value) {
        void loadActionById(actionId.value);
        return;
    }
    void loadLatestAction();
});

onDeactivated(() => {
    clearPollTimer();
});

onUnmounted(() => {
    clearPollTimer();
});
</script>

<template>
    <section class="space-y-6 fade-in">
        <header
            class="rounded-3xl border border-white/10 lrc-results-header p-6 md:p-8 relative overflow-hidden"
        >
            <div
                class="absolute -right-10 top-0 h-48 w-48 rounded-full bg-cyan-400/15 blur-3xl pointer-events-none"
            />
            <div
                class="absolute left-4 bottom-0 h-32 w-32 rounded-full bg-rose-400/15 blur-2xl pointer-events-none"
            />

            <button
                class="btn-ghost rounded-lg px-3 py-1.5 text-xs mb-5 inline-flex items-center gap-1.5 relative z-10"
                @click="goBack"
            >
                ← Back to Compare Setup
            </button>

            <div
                class="relative z-10 flex flex-wrap items-start justify-between gap-4"
            >
                <div>
                    <p
                        class="text-xs uppercase tracking-[0.22em] text-cyan-100/90 font-semibold"
                    >
                        Compare Results Workspace
                    </p>
                    <h2
                        class="text-2xl md:text-4xl font-display font-bold text-white mt-2"
                    >
                        Full-Space Hit/Miss Explorer
                    </h2>
                    <p
                        class="text-sm text-slate-100/85 mt-3 max-w-3xl leading-relaxed"
                    >
                        Inspect followers and non-followers across the full
                        result grid without sharing space with the input
                        controls.
                    </p>
                    <p class="text-xs text-cyan-100/80 mt-4">
                        Active profile:
                        {{
                            props.profileUsername
                                ? "@" + props.profileUsername
                                : props.profileId
                        }}
                    </p>
                </div>

                <div class="flex gap-2 flex-wrap">
                    <button
                        class="btn-ghost rounded-lg px-3 py-1.5 text-xs"
                        @click="openHistory"
                    >
                        Open History
                    </button>
                    <button
                        class="btn-ghost rounded-lg px-3 py-1.5 text-xs"
                        :disabled="!comparisonRows.length"
                        @click="exportResultJson"
                    >
                        Export JSON
                    </button>
                    <button
                        class="btn-ghost rounded-lg px-3 py-1.5 text-xs"
                        :disabled="!comparisonRows.length"
                        @click="exportResultCsv"
                    >
                        Export CSV
                    </button>
                </div>
            </div>
        </header>

        <div
            v-if="loadError"
            class="rounded-2xl border border-rose-400/25 bg-rose-500/10 text-rose-200 px-4 py-3 text-sm"
        >
            {{ loadError }}
        </div>

        <div
            v-else-if="loading && !currentAction"
            class="rounded-2xl border border-white/10 bg-[#121d33] px-4 py-6 text-sm text-slate-300"
        >
            Loading compare results…
        </div>

        <div
            v-else-if="!currentAction"
            class="rounded-2xl border border-white/10 bg-[#121d33] px-4 py-6 text-sm text-slate-300"
        >
            No left-right compare result is available yet.
        </div>

        <template v-else>
            <section class="grid xl:grid-cols-[0.9fr,1.1fr,1.1fr,1fr] gap-4">
                <div
                    class="rounded-2xl border border-emerald-400/25 bg-emerald-500/10 p-4"
                >
                    <p class="text-xs text-emerald-200/90">Coverage Score</p>
                    <p class="text-3xl font-semibold text-emerald-200 mt-2">
                        {{ coveragePercent }}%
                    </p>
                </div>
                <div
                    class="rounded-2xl border border-rose-400/25 bg-rose-500/10 p-4"
                >
                    <p class="text-xs text-rose-200/90">Missing Links</p>
                    <p class="text-3xl font-semibold text-rose-200 mt-2">
                        {{ comparisonTotals.missing_total }}
                    </p>
                </div>
                <div
                    class="rounded-2xl border border-cyan-400/25 bg-cyan-500/10 p-4"
                >
                    <p class="text-xs text-cyan-200/90">Confirmed Follows</p>
                    <p class="text-3xl font-semibold text-cyan-200 mt-2">
                        {{ comparisonTotals.follows_total }}
                    </p>
                </div>
                <div
                    class="rounded-2xl border border-amber-400/25 bg-amber-500/10 p-4"
                >
                    <p class="text-xs text-amber-200/90">Action Status</p>
                    <p class="text-3xl font-semibold text-amber-200 mt-2">
                        {{ currentAction.status }}
                    </p>
                </div>
            </section>

            <section
                v-if="isActionInProgress"
                class="rounded-2xl border border-cyan-400/25 bg-cyan-500/10 p-5 md:p-6"
            >
                <div class="flex items-center justify-between gap-3 flex-wrap">
                    <h3 class="text-sm font-semibold text-cyan-100">
                        Scan In Progress
                    </h3>
                    <p class="text-xs text-cyan-200/90">
                        {{ currentAction.completed_items }} /
                        {{ currentAction.total_items || 0 }} left profiles
                        processed
                    </p>
                </div>

                <div
                    class="mt-3 h-2.5 rounded-full bg-slate-900/70 overflow-hidden"
                >
                    <div
                        class="h-full bg-gradient-to-r from-cyan-500 to-emerald-400"
                        :style="{ width: `${actionProgressPercent}%` }"
                    />
                </div>

                <p class="text-xs text-cyan-100/85 mt-2">
                    {{ actionProgressPercent }}% complete
                    <span v-if="currentAction.status === 'queued'">
                        • waiting for worker to start</span
                    >
                    <span v-else> • currently scanning follower lists</span>
                </p>
            </section>

            <section
                class="rounded-2xl border border-white/10 bg-[#121d33] p-5 md:p-6 space-y-4"
            >
                <div class="flex items-center justify-between flex-wrap gap-3">
                    <h3 class="text-lg font-semibold text-slate-100">
                        Directional Node Graph
                    </h3>
                    <div
                        class="flex items-center gap-2 flex-wrap text-xs text-slate-300"
                    >
                        <select
                            v-model="graphRelationMode"
                            class="input-dark-select text-xs"
                        >
                            <option value="both">Hits + Misses</option>
                            <option value="following">Hits only</option>
                            <option value="missing">Misses only</option>
                        </select>
                        <label
                            >Left nodes
                            <input
                                v-model.number="graphLeftLimit"
                                type="number"
                                min="4"
                                max="50"
                                class="input-dark ml-2 w-20"
                            />
                        </label>
                        <label
                            >Right nodes
                            <input
                                v-model.number="graphRightLimit"
                                type="number"
                                min="10"
                                max="250"
                                class="input-dark ml-2 w-20"
                            />
                        </label>
                    </div>
                </div>

                <p class="text-xs text-slate-400">
                    Cyan solid edges are followers. Rose dashed edges are
                    non-followers. Use the mode switch to isolate hits, misses,
                    or both.
                </p>

                <div
                    class="w-full overflow-x-auto rounded-xl border border-white/10 bg-[#0e172d] p-3"
                >
                    <svg
                        :viewBox="`0 0 1180 ${graphHeight}`"
                        class="w-full min-w-[980px]"
                    >
                        <g>
                            <line
                                v-for="(edge, idx) in graphEdges"
                                :key="`edge-${idx}`"
                                :x1="edge.x1"
                                :y1="edge.y1"
                                :x2="edge.x2"
                                :y2="edge.y2"
                                :stroke="
                                    edge.kind === 'following'
                                        ? 'rgba(45, 212, 191, 0.55)'
                                        : 'rgba(251, 113, 133, 0.28)'
                                "
                                :stroke-width="
                                    edge.kind === 'following' ? 1.6 : 1.1
                                "
                                :stroke-dasharray="
                                    edge.kind === 'missing' ? '5 6' : undefined
                                "
                            />
                        </g>

                        <g>
                            <circle
                                v-for="node in graphLeftNodes"
                                :key="`l-${node.id}`"
                                cx="230"
                                :cy="node.y"
                                r="9"
                                fill="#22d3ee"
                            />
                            <text
                                v-for="node in graphLeftNodes"
                                :key="`lt-${node.id}`"
                                x="30"
                                :y="node.y + 4"
                                fill="#dbeafe"
                                font-size="13"
                            >
                                {{ node.label }}
                            </text>
                        </g>

                        <g>
                            <circle
                                v-for="node in graphRightNodes"
                                :key="`r-${node.id}`"
                                cx="950"
                                :cy="node.y"
                                r="9"
                                fill="#f59e0b"
                            />
                            <text
                                v-for="node in graphRightNodes"
                                :key="`rt-${node.id}`"
                                x="970"
                                :y="node.y + 4"
                                fill="#fde68a"
                                font-size="13"
                            >
                                {{ node.label }}
                            </text>
                        </g>

                        <text x="140" y="28" fill="#7dd3fc" font-size="12">
                            Left set
                        </text>
                        <text x="926" y="28" fill="#fcd34d" font-size="12">
                            Right set
                        </text>
                    </svg>
                </div>
            </section>

            <section
                class="rounded-2xl border border-white/10 bg-[#121d33] p-5 md:p-6 space-y-4"
            >
                <div class="flex items-center justify-between flex-wrap gap-3">
                    <h3 class="text-lg font-semibold text-slate-100">
                        Matrix View
                    </h3>
                    <div class="flex items-center gap-2 flex-wrap">
                        <select
                            v-model="matrixFilter"
                            class="input-dark-select text-xs"
                        >
                            <option value="all">All cells</option>
                            <option value="missing">Misses only</option>
                            <option value="following">Hits only</option>
                        </select>
                        <button
                            class="rounded-lg px-3 py-1.5 text-xs border transition-colors"
                            :class="
                                compactMatrixMode
                                    ? 'border-cyan-400/40 bg-cyan-400/15 text-cyan-200'
                                    : 'border-white/15 bg-white/5 text-slate-300 hover:bg-white/10'
                            "
                            @click="compactMatrixMode = !compactMatrixMode"
                        >
                            {{
                                compactMatrixMode
                                    ? "Compact: On"
                                    : "Compact: Off"
                            }}
                        </button>
                        <button
                            class="rounded-lg px-3 py-1.5 text-xs border transition-colors"
                            :class="
                                showUniversallyMissingOnly
                                    ? 'border-rose-400/40 bg-rose-400/15 text-rose-200'
                                    : 'border-white/15 bg-white/5 text-slate-300 hover:bg-white/10'
                            "
                            @click="
                                showUniversallyMissingOnly =
                                    !showUniversallyMissingOnly
                            "
                        >
                            {{
                                showUniversallyMissingOnly
                                    ? "Universal Missing: On"
                                    : "Universal Missing: Off"
                            }}
                        </button>
                        <button
                            class="btn-ghost rounded-lg px-3 py-1.5 text-xs"
                            :disabled="rightPage <= 1"
                            @click="rightPage = Math.max(1, rightPage - 1)"
                        >
                            Prev
                        </button>
                        <span class="text-xs text-slate-400"
                            >{{ rightPage }} / {{ rightPages }}</span
                        >
                        <button
                            class="btn-ghost rounded-lg px-3 py-1.5 text-xs"
                            :disabled="rightPage >= rightPages"
                            @click="
                                rightPage = Math.min(rightPages, rightPage + 1)
                            "
                        >
                            Next
                        </button>
                    </div>
                </div>

                <div
                    class="flex items-center justify-between gap-3 flex-wrap text-xs"
                >
                    <p class="text-slate-400">
                        Showing {{ pagedRightTargets.length }} of
                        {{ filteredRightTargets.length }} right targets
                        <span v-if="compactMatrixMode" class="text-cyan-300">
                            • compact density enabled</span
                        >
                    </p>
                    <p class="text-rose-300">
                        Universally missing targets:
                        {{ universallyMissingCount }}
                    </p>
                </div>

                <p
                    v-if="compactModeRecommended && !compactMatrixMode"
                    class="text-xs rounded-lg border border-cyan-400/30 bg-cyan-500/10 text-cyan-200 px-3 py-2"
                >
                    Right-side set is large. Enable Compact mode for faster
                    scanning.
                </p>

                <div class="overflow-auto rounded-xl border border-white/10">
                    <table
                        class="w-full min-w-[1280px]"
                        :class="compactMatrixMode ? 'text-[10px]' : 'text-xs'"
                    >
                        <thead class="bg-white/5">
                            <tr>
                                <th
                                    class="text-left sticky left-0 bg-[#17233e] z-10"
                                    :class="
                                        compactMatrixMode
                                            ? 'px-2 py-1.5'
                                            : 'px-3 py-2'
                                    "
                                >
                                    Left \ Right
                                </th>
                                <th
                                    v-for="target in pagedRightTargets"
                                    :key="`h-${targetIdentityKey(target)}`"
                                    class="text-left text-amber-200"
                                    :class="
                                        compactMatrixMode
                                            ? 'px-1 py-1.5'
                                            : 'px-2 py-2'
                                    "
                                >
                                    <span v-if="compactMatrixMode">{{
                                        (
                                            target.display_username ||
                                            target.raw_input
                                        ).slice(0, 14)
                                    }}</span>
                                    <span v-else>{{
                                        target.display_username ||
                                        target.raw_input
                                    }}</span>
                                </th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr
                                v-for="row in sortedRows"
                                :key="row.left_item_id"
                                class="border-t border-white/5"
                            >
                                <td
                                    class="sticky left-0 bg-[#17233e] z-10 text-cyan-100"
                                    :class="
                                        compactMatrixMode
                                            ? 'px-2 py-1.5'
                                            : 'px-3 py-2'
                                    "
                                >
                                    <div class="font-medium">
                                        <span v-if="compactMatrixMode">{{
                                            (
                                                row.left_display ||
                                                row.left_raw_input ||
                                                row.left_user_id ||
                                                ""
                                            ).slice(0, 18)
                                        }}</span>
                                        <span v-else>{{
                                            row.left_display ||
                                            row.left_raw_input ||
                                            row.left_user_id
                                        }}</span>
                                    </div>
                                    <div
                                        v-if="!compactMatrixMode"
                                        class="text-[11px] text-slate-400"
                                    >
                                        miss {{ row.missing_count }} • hit
                                        {{ row.follows_count }}
                                    </div>
                                </td>
                                <td
                                    v-for="target in pagedRightTargets"
                                    :key="`c-${row.left_item_id}-${targetIdentityKey(target)}`"
                                    :class="
                                        compactMatrixMode
                                            ? 'px-1 py-1'
                                            : 'px-2 py-2'
                                    "
                                >
                                    <div
                                        v-if="
                                            shouldDisplayCell(
                                                matrixCellStatus(
                                                    row.left_item_id,
                                                    targetIdentityKey(target),
                                                ),
                                            )
                                        "
                                        class="rounded border"
                                        :class="
                                            matrixCellStatus(
                                                row.left_item_id,
                                                targetIdentityKey(target),
                                            ) === 'following'
                                                ? compactMatrixMode
                                                    ? 'h-3 border-emerald-400/45 bg-emerald-500/35'
                                                    : 'h-5 bg-emerald-500/20 border-emerald-400/30'
                                                : compactMatrixMode
                                                  ? 'h-3 border-rose-400/35 bg-rose-500/25'
                                                  : 'h-5 bg-rose-500/15 border-rose-400/25'
                                        "
                                    />
                                    <div
                                        v-else
                                        :class="
                                            compactMatrixMode
                                                ? 'h-3 rounded border border-transparent'
                                                : 'h-5 rounded border border-transparent'
                                        "
                                    />
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </section>
        </template>
    </section>
</template>

<style scoped>
.lrc-results-header {
    background:
        linear-gradient(
            115deg,
            rgba(17, 30, 58, 0.96) 0%,
            rgba(18, 44, 88, 0.94) 55%,
            rgba(63, 24, 40, 0.92) 100%
        ),
        radial-gradient(
            circle at 18% 18%,
            rgba(56, 189, 248, 0.22),
            transparent 38%
        ),
        radial-gradient(
            circle at 84% 76%,
            rgba(244, 114, 182, 0.18),
            transparent 44%
        );
}
</style>
