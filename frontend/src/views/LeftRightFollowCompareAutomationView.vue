<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from "vue";
import { useRouter } from "vue-router";
import {
    cancelAutomationAction,
    confirmAutomationAction,
    getAutomationAction,
    prepareLeftRightCompare,
} from "../services/api";
import {
    clearAutomationJob,
    recoverAutomationJobForType,
    registerAutomationJob,
    updateAutomationJob,
} from "../services/automationJobRegistry";
import type {
    AutomationAction,
    AutomationActionResult,
    LeftRightCompareActionConfig,
    LeftRightCompareResult,
} from "../types/automation";

const props = defineProps<{
    profileId: string;
    profileUsername?: string | null;
}>();

const emit = defineEmits<{
    backToAutomation: [];
}>();

const router = useRouter();

type Phase =
    | "idle"
    | "preparing"
    | "staged"
    | "confirming"
    | "running"
    | "completed"
    | "error";

const phase = ref<Phase>("idle");
const actionError = ref<string | null>(null);
const stagedResult = ref<AutomationActionResult | null>(null);
const currentAction = ref<AutomationAction | null>(null);
const activeActionLock = ref<AutomationAction | null>(null);
let pollTimeout: ReturnType<typeof setTimeout> | null = null;

const leftInput = ref("");
const rightInput = ref("");
const maxLeftCount = ref(50);
const maxRightCount = ref(500);

const leftPlaceholder = [
    "alpha.user",
    "https://www.instagram.com/team.left/",
    "21948590123",
].join("\n");

const rightPlaceholder = [
    "target_user_1",
    "https://www.instagram.com/target_user_2/",
    "54321098765",
].join("\n");

function parseUniqueEntries(raw: string): string[] {
    return Array.from(
        new Set(
            raw
                .split(/[\n,]/)
                .map((token) => token.trim())
                .filter(Boolean),
        ),
    );
}

const leftTargets = computed(() => parseUniqueEntries(leftInput.value));
const rightTargetsInput = computed(() => parseUniqueEntries(rightInput.value));
const hasTargets = computed(
    () => leftTargets.value.length > 0 && rightTargetsInput.value.length > 0,
);

const hasConflictingAction = computed(
    () =>
        !!activeActionLock.value &&
        ["staged", "queued", "running"].includes(activeActionLock.value.status),
);

const prepareBlockReason = computed(() => {
    if (!activeActionLock.value || !hasConflictingAction.value) {
        return null;
    }
    return `Another compare action is already ${activeActionLock.value.status}. Action: ${activeActionLock.value.action_id}`;
});

const runningProgress = computed(() => {
    if (!currentAction.value || !currentAction.value.total_items) return 0;
    return Math.round(
        (currentAction.value.completed_items /
            currentAction.value.total_items) *
            100,
    );
});

const activeActionForResult = computed(
    () => currentAction.value ?? activeActionLock.value,
);

const comparisonResult = computed<LeftRightCompareResult | null>(() => {
    const action = activeActionForResult.value;
    if (!action || !action.config) {
        return null;
    }
    const config = action.config as LeftRightCompareActionConfig;
    return config.comparison_result ?? null;
});

const comparisonRows = computed(() => comparisonResult.value?.left_rows ?? []);
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

const currentActionId = computed(
    () =>
        currentAction.value?.action_id ||
        activeActionLock.value?.action_id ||
        stagedResult.value?.action_id ||
        "",
);

const canOpenResultsWorkspace = computed(() => !!currentActionId.value);

async function openResultsWorkspace() {
    if (!currentActionId.value) {
        return;
    }
    await router.push({
        name: "automation-left-right-compare-results",
        params: { actionId: currentActionId.value },
    });
}

async function openHistoryWorkspace() {
    await router.push({
        name: "automation-left-right-compare-history",
    });
}

async function prepare() {
    if (!hasTargets.value || hasConflictingAction.value) return;
    phase.value = "preparing";
    actionError.value = null;
    try {
        const result = await prepareLeftRightCompare({
            left_targets: leftTargets.value,
            right_targets: rightTargetsInput.value,
            max_left_count: maxLeftCount.value,
            max_right_count: maxRightCount.value,
        });
        stagedResult.value = result;
        const action = await getAutomationAction(result.action_id);
        registerAutomationJob(action);
        activeActionLock.value = action;
        currentAction.value = action;
        phase.value = "staged";
    } catch (err: unknown) {
        actionError.value =
            err instanceof Error
                ? err.message
                : "Failed to prepare left-right comparison";
        phase.value = "error";
    }
}

async function confirm() {
    if (!stagedResult.value) return;
    phase.value = "confirming";
    actionError.value = null;
    try {
        const action = await confirmAutomationAction(
            stagedResult.value.action_id,
        );
        registerAutomationJob(action);
        activeActionLock.value = action;
        currentAction.value = action;
        phase.value = "running";
        schedulePoll(action.action_id);
        await openResultsWorkspace();
    } catch (err: unknown) {
        actionError.value =
            err instanceof Error ? err.message : "Failed to confirm comparison";
        phase.value = "error";
    }
}

function schedulePoll(actionId: string) {
    if (pollTimeout) clearTimeout(pollTimeout);
    pollTimeout = setTimeout(() => poll(actionId), 2500);
}

async function poll(actionId: string) {
    try {
        const action = await getAutomationAction(actionId);
        currentAction.value = action;

        if (["staged", "queued", "running"].includes(action.status)) {
            updateAutomationJob(action.action_id, action.status);
            activeActionLock.value = action;
        }

        if (action.status === "completed" || action.status === "partial") {
            clearAutomationJob(action.action_id);
            if (activeActionLock.value?.action_id === action.action_id) {
                activeActionLock.value = null;
            }
            phase.value = "completed";
        } else if (action.status === "error" || action.status === "cancelled") {
            clearAutomationJob(action.action_id);
            if (activeActionLock.value?.action_id === action.action_id) {
                activeActionLock.value = null;
            }
            actionError.value = action.error ?? "Action ended unexpectedly";
            phase.value = "error";
        } else {
            schedulePoll(actionId);
        }
    } catch {
        schedulePoll(actionId);
    }
}

async function cancel() {
    const actionId =
        stagedResult.value?.action_id ?? currentAction.value?.action_id;
    if (!actionId) return;
    if (pollTimeout) {
        clearTimeout(pollTimeout);
        pollTimeout = null;
    }

    try {
        await cancelAutomationAction(actionId);
    } catch {
        // best effort
    }

    clearAutomationJob(actionId);
    if (activeActionLock.value?.action_id === actionId) {
        activeActionLock.value = null;
    }
    reset();
}

function reset() {
    if (pollTimeout) {
        clearTimeout(pollTimeout);
        pollTimeout = null;
    }
    phase.value = "idle";
    actionError.value = null;
    stagedResult.value = null;
    currentAction.value = null;
}

async function recoverExistingAction() {
    try {
        const action = await recoverAutomationJobForType(
            props.profileId,
            "left_right_compare",
        );
        if (!action) {
            return;
        }

        activeActionLock.value = action;
        currentAction.value = action;
        if (action.status === "staged") {
            phase.value = "staged";
            stagedResult.value = {
                action_id: action.action_id,
                action_type: action.action_type,
                status: action.status,
                selected_count: action.total_items,
                excluded_count: action.skipped_items,
                selected_items: [],
                excluded_items: [],
            };
            return;
        }
        if (action.status === "queued" || action.status === "running") {
            phase.value = "running";
            schedulePoll(action.action_id);
            return;
        }
        if (action.status === "completed" || action.status === "partial") {
            phase.value = "completed";
            return;
        }
        if (action.status === "error" || action.status === "cancelled") {
            phase.value = "error";
            actionError.value = action.error ?? "Action ended unexpectedly";
        }
    } catch {
        // Keep UI interactive on transient backend errors.
    }
}

function goBack() {
    emit("backToAutomation");
}

onMounted(() => {
    void recoverExistingAction();
});

onUnmounted(() => {
    if (pollTimeout) clearTimeout(pollTimeout);
});
</script>

<template>
    <section class="space-y-6 fade-in">
        <header
            class="rounded-3xl border border-white/10 lrc-header p-6 md:p-8 relative overflow-hidden"
        >
            <div
                class="absolute -right-6 top-4 h-40 w-40 rounded-full bg-amber-400/20 blur-3xl pointer-events-none"
            />
            <div
                class="absolute left-6 -bottom-6 h-28 w-28 rounded-full bg-cyan-400/25 blur-2xl pointer-events-none"
            />

            <button
                class="btn-ghost rounded-lg px-3 py-1.5 text-xs mb-5 inline-flex items-center gap-1.5 relative z-10"
                @click="goBack"
            >
                ← Back to Automation
            </button>

            <div class="relative z-10">
                <p
                    class="text-xs uppercase tracking-[0.22em] text-amber-100/90 font-semibold"
                >
                    Automation: Left-Right Compare
                </p>
                <h2
                    class="text-2xl md:text-3xl font-display font-bold text-white mt-2"
                >
                    Compare Setup, Then Open the Full Results Workspace
                </h2>
                <p
                    class="text-sm text-slate-100/85 mt-3 max-w-3xl leading-relaxed"
                >
                    Prepare and run the comparison here. Graph and table
                    exploration now live in a dedicated full-width view so the
                    input workflow stays clean.
                </p>
                <p class="text-xs text-amber-100/80 mt-4">
                    Active profile:
                    {{
                        props.profileUsername
                            ? "@" + props.profileUsername
                            : props.profileId
                    }}
                </p>
            </div>
        </header>

        <div class="grid xl:grid-cols-[1.25fr,0.75fr] gap-6">
            <section class="space-y-5">
                <div
                    class="rounded-2xl border border-white/10 bg-[#16213a]/95 p-5 md:p-6 shadow-2xl shadow-black/30"
                >
                    <div class="flex items-center justify-between gap-2 mb-3">
                        <h3 class="text-lg font-semibold text-slate-100">
                            Input Sets
                        </h3>
                        <span
                            class="text-xs px-2.5 py-1 rounded-full border border-amber-300/30 bg-amber-300/10 text-amber-200"
                        >
                            Left {{ leftTargets.length }} • Right
                            {{ rightTargetsInput.length }}
                        </span>
                    </div>

                    <div class="grid md:grid-cols-2 gap-4">
                        <div>
                            <p class="text-sm font-medium text-slate-200">
                                Left set
                            </p>
                            <p class="text-xs text-slate-500 mt-1">
                                Accounts being checked (follower owners).
                            </p>
                            <textarea
                                v-model="leftInput"
                                rows="9"
                                class="input-dark mt-2"
                                :placeholder="leftPlaceholder"
                                :disabled="phase !== 'idle'"
                            />
                        </div>
                        <div>
                            <p class="text-sm font-medium text-slate-200">
                                Right set
                            </p>
                            <p class="text-xs text-slate-500 mt-1">
                                Accounts tested as followers of each left
                                profile.
                            </p>
                            <textarea
                                v-model="rightInput"
                                rows="9"
                                class="input-dark mt-2"
                                :placeholder="rightPlaceholder"
                                :disabled="phase !== 'idle'"
                            />
                        </div>
                    </div>

                    <div class="grid md:grid-cols-2 gap-3 mt-4">
                        <label class="space-y-1">
                            <span
                                class="text-xs uppercase tracking-wide text-slate-400"
                                >Max left</span
                            >
                            <input
                                v-model.number="maxLeftCount"
                                type="number"
                                min="1"
                                max="50"
                                class="input-dark"
                                :disabled="phase !== 'idle'"
                            />
                        </label>
                        <label class="space-y-1">
                            <span
                                class="text-xs uppercase tracking-wide text-slate-400"
                                >Max right</span
                            >
                            <input
                                v-model.number="maxRightCount"
                                type="number"
                                min="1"
                                max="500"
                                class="input-dark"
                                :disabled="phase !== 'idle'"
                            />
                        </label>
                    </div>
                </div>

                <div
                    class="rounded-2xl border border-white/10 bg-[#131f36] p-5"
                >
                    <div class="flex flex-wrap gap-3 items-center">
                        <button
                            class="btn-violet rounded-xl px-5 py-2.5 text-sm font-semibold"
                            :disabled="
                                !hasTargets ||
                                phase !== 'idle' ||
                                hasConflictingAction
                            "
                            @click="prepare"
                        >
                            <span v-if="phase === 'preparing'">Preparing…</span>
                            <span v-else>Stage Comparison</span>
                        </button>

                        <button
                            class="btn-ghost rounded-xl px-5 py-2.5 text-sm font-medium"
                            :disabled="phase !== 'staged'"
                            @click="confirm"
                        >
                            <span v-if="phase === 'confirming'"
                                >Confirming…</span
                            >
                            <span v-else>Confirm & Run</span>
                        </button>

                        <button
                            class="btn-danger rounded-xl px-5 py-2.5 text-sm font-medium"
                            :disabled="
                                !['staged', 'running', 'confirming'].includes(
                                    phase,
                                )
                            "
                            @click="cancel"
                        >
                            Cancel
                        </button>

                        <button
                            class="btn-ghost rounded-xl px-4 py-2 text-xs"
                            :disabled="
                                phase === 'running' || phase === 'confirming'
                            "
                            @click="reset"
                        >
                            Reset
                        </button>

                        <button
                            class="rounded-xl px-5 py-2.5 text-sm font-medium border transition-colors"
                            :class="
                                canOpenResultsWorkspace
                                    ? 'border-cyan-400/40 bg-cyan-400/10 text-cyan-200 hover:bg-cyan-400/20'
                                    : 'border-white/10 bg-white/5 text-slate-500 cursor-not-allowed'
                            "
                            :disabled="!canOpenResultsWorkspace"
                            @click="openResultsWorkspace"
                        >
                            Open Full Results View
                        </button>

                        <button
                            class="btn-ghost rounded-xl px-5 py-2.5 text-sm font-medium"
                            @click="openHistoryWorkspace"
                        >
                            Open Compare History
                        </button>
                    </div>

                    <p
                        v-if="prepareBlockReason"
                        class="text-xs text-amber-300 mt-3"
                    >
                        {{ prepareBlockReason }}
                    </p>
                    <p v-if="actionError" class="text-xs text-rose-300 mt-3">
                        {{ actionError }}
                    </p>
                </div>
            </section>

            <section class="space-y-5">
                <div
                    class="rounded-2xl border border-white/10 bg-[#16213a]/95 p-5 md:p-6"
                >
                    <h3 class="text-lg font-semibold text-slate-100">
                        Run Status
                    </h3>
                    <p class="text-sm text-slate-400 mt-2">
                        Phase:
                        <strong class="text-slate-200">{{ phase }}</strong>
                    </p>
                    <p
                        v-if="currentActionId"
                        class="text-xs text-slate-500 mt-2"
                    >
                        Action: {{ currentActionId }}
                    </p>

                    <div
                        v-if="phase === 'staged' && stagedResult"
                        class="mt-4 grid grid-cols-2 gap-3 text-sm"
                    >
                        <div
                            class="rounded-xl bg-white/5 border border-white/10 p-3"
                        >
                            <p class="text-xs text-slate-400">Left selected</p>
                            <p class="text-xl font-semibold text-cyan-200">
                                {{ stagedResult.selected_count }}
                            </p>
                        </div>
                        <div
                            class="rounded-xl bg-white/5 border border-white/10 p-3"
                        >
                            <p class="text-xs text-slate-400">Right selected</p>
                            <p class="text-xl font-semibold text-amber-200">
                                {{ stagedResult.right_selected_count || 0 }}
                            </p>
                        </div>
                    </div>

                    <div v-if="phase === 'running'" class="mt-4 space-y-2">
                        <div
                            class="h-2 rounded-full bg-slate-800 overflow-hidden"
                        >
                            <div
                                class="h-full bg-gradient-to-r from-cyan-500 to-amber-500"
                                :style="{ width: `${runningProgress}%` }"
                            />
                        </div>
                        <p class="text-xs text-slate-400">
                            {{ currentAction?.completed_items || 0 }} /
                            {{ currentAction?.total_items || 0 }} left profiles
                            processed
                        </p>
                    </div>
                </div>

                <div
                    class="rounded-2xl border border-white/10 bg-[#16213a]/95 p-5 md:p-6"
                >
                    <h3 class="text-lg font-semibold text-slate-100">
                        Result Snapshot
                    </h3>
                    <div class="grid grid-cols-2 gap-3 mt-4">
                        <div
                            class="rounded-xl border border-emerald-400/25 bg-emerald-500/10 p-3"
                        >
                            <p class="text-xs text-emerald-200/90">
                                Coverage Score
                            </p>
                            <p class="text-2xl font-semibold text-emerald-200">
                                {{ coveragePercent }}%
                            </p>
                        </div>
                        <div
                            class="rounded-xl border border-rose-400/25 bg-rose-500/10 p-3"
                        >
                            <p class="text-xs text-rose-200/90">
                                Missing Links
                            </p>
                            <p class="text-2xl font-semibold text-rose-200">
                                {{ comparisonTotals.missing_total }}
                            </p>
                        </div>
                        <div
                            class="rounded-xl border border-cyan-400/25 bg-cyan-500/10 p-3"
                        >
                            <p class="text-xs text-cyan-200/90">
                                Confirmed Follows
                            </p>
                            <p class="text-2xl font-semibold text-cyan-200">
                                {{ comparisonTotals.follows_total }}
                            </p>
                        </div>
                        <div
                            class="rounded-xl border border-amber-400/25 bg-amber-500/10 p-3"
                        >
                            <p class="text-xs text-amber-200/90">Rows Ready</p>
                            <p class="text-2xl font-semibold text-amber-200">
                                {{ comparisonRows.length }}
                            </p>
                        </div>
                    </div>

                    <div
                        class="mt-4 rounded-xl border border-cyan-400/20 bg-cyan-500/8 px-4 py-3 text-sm text-cyan-100"
                    >
                        Open the full results view to inspect the dedicated
                        hit/miss graph and the spacious matrix explorer.
                    </div>
                </div>
            </section>
        </div>
    </section>
</template>

<style scoped>
.lrc-header {
    background:
        linear-gradient(
            115deg,
            rgba(22, 36, 72, 0.95) 0%,
            rgba(20, 53, 95, 0.92) 55%,
            rgba(70, 50, 22, 0.9) 100%
        ),
        radial-gradient(
            circle at 16% 22%,
            rgba(56, 189, 248, 0.22),
            transparent 42%
        ),
        radial-gradient(
            circle at 82% 70%,
            rgba(251, 191, 36, 0.2),
            transparent 45%
        );
}
</style>
