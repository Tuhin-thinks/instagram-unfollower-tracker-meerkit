<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { listAutomationActions } from "../services/api";
import type {
    AutomationAction,
    LeftRightCompareActionConfig,
    LeftRightCompareResult,
} from "../types/automation";

const props = defineProps<{
    profileId: string;
    profileUsername?: string | null;
}>();

const router = useRouter();

const actions = ref<AutomationAction[]>([]);
const loading = ref(false);
const loadError = ref<string | null>(null);
const selectedStatus = ref<"all" | AutomationAction["status"]>("all");

const statusOptions: Array<{
    label: string;
    value: "all" | AutomationAction["status"];
}> = [
    { label: "All", value: "all" },
    { label: "Completed", value: "completed" },
    { label: "Partial", value: "partial" },
    { label: "Running", value: "running" },
    { label: "Queued", value: "queued" },
    { label: "Error", value: "error" },
    { label: "Cancelled", value: "cancelled" },
    { label: "Staged", value: "staged" },
];

const filteredActions = computed(() => {
    if (selectedStatus.value === "all") {
        return actions.value;
    }
    return actions.value.filter(
        (action) => action.status === selectedStatus.value,
    );
});

function getComparisonResult(
    action: AutomationAction,
): LeftRightCompareResult | null {
    const config = action.config as LeftRightCompareActionConfig | null;
    return config?.comparison_result ?? null;
}

function formatDate(value: string | null | undefined): string {
    if (!value) return "-";
    const d = new Date(value);
    if (Number.isNaN(d.getTime())) return value;
    return d.toLocaleString();
}

function statusBadgeClass(status: string): string {
    if (status === "completed")
        return "border-emerald-400/30 bg-emerald-500/10 text-emerald-200";
    if (status === "partial")
        return "border-amber-400/30 bg-amber-500/10 text-amber-200";
    if (status === "running" || status === "queued")
        return "border-cyan-400/30 bg-cyan-500/10 text-cyan-200";
    if (status === "error" || status === "cancelled")
        return "border-rose-400/30 bg-rose-500/10 text-rose-200";
    return "border-slate-400/30 bg-slate-500/10 text-slate-200";
}

async function loadHistory() {
    loading.value = true;
    loadError.value = null;
    try {
        const response = await listAutomationActions({
            action_type: "left_right_compare",
            limit: 200,
        });
        actions.value = response.actions.sort(
            (a, b) =>
                Date.parse(b.update_date || b.create_date) -
                Date.parse(a.update_date || a.create_date),
        );
    } catch (err: unknown) {
        loadError.value =
            err instanceof Error
                ? err.message
                : "Failed to load compare history";
    } finally {
        loading.value = false;
    }
}

function openSetup() {
    void router.push({ name: "automation-left-right-compare" });
}

function openResult(actionId: string) {
    void router.push({
        name: "automation-left-right-compare-results",
        params: { actionId },
    });
}

onMounted(() => {
    void loadHistory();
});
</script>

<template>
    <section class="space-y-6 fade-in">
        <header
            class="rounded-3xl border border-white/10 lrc-results-header p-6 md:p-8 relative overflow-hidden"
        >
            <button
                class="btn-ghost rounded-lg px-3 py-1.5 text-xs mb-5 inline-flex items-center gap-1.5 relative z-10"
                @click="openSetup"
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
                        Left-Right Compare
                    </p>
                    <h2
                        class="text-2xl md:text-4xl font-display font-bold text-white mt-2"
                    >
                        Comparison History
                    </h2>
                    <p
                        class="text-sm text-slate-100/85 mt-3 max-w-3xl leading-relaxed"
                    >
                        Past compare runs are preserved in the backend database.
                        Open any run to inspect its full graph and matrix.
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

                <div class="flex items-center gap-2">
                    <label class="text-xs text-slate-300">Status</label>
                    <select
                        v-model="selectedStatus"
                        class="input-dark-select text-xs"
                    >
                        <option
                            v-for="option in statusOptions"
                            :key="option.value"
                            :value="option.value"
                        >
                            {{ option.label }}
                        </option>
                    </select>
                    <button
                        class="btn-ghost rounded-lg px-3 py-1.5 text-xs"
                        @click="loadHistory"
                    >
                        Refresh
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
            v-else-if="loading"
            class="rounded-2xl border border-white/10 bg-[#121d33] px-4 py-6 text-sm text-slate-300"
        >
            Loading comparison history...
        </div>

        <div
            v-else-if="!filteredActions.length"
            class="rounded-2xl border border-white/10 bg-[#121d33] px-4 py-6 text-sm text-slate-300"
        >
            No comparison runs found for the selected filter.
        </div>

        <section v-else class="space-y-3">
            <article
                v-for="action in filteredActions"
                :key="action.action_id"
                class="rounded-2xl border border-white/10 bg-[#121d33] p-4 md:p-5"
            >
                <div class="flex items-start justify-between gap-3 flex-wrap">
                    <div>
                        <p class="text-xs text-slate-400">Action ID</p>
                        <p class="text-sm font-mono text-slate-200 break-all">
                            {{ action.action_id }}
                        </p>
                        <p class="text-xs text-slate-400 mt-1">
                            Created: {{ formatDate(action.create_date) }} •
                            Updated: {{ formatDate(action.update_date) }}
                        </p>
                    </div>

                    <div class="flex items-center gap-2">
                        <span
                            class="px-2.5 py-1 rounded-full text-xs border"
                            :class="statusBadgeClass(action.status)"
                        >
                            {{ action.status }}
                        </span>
                        <button
                            class="btn-violet rounded-lg px-3 py-1.5 text-xs"
                            @click="openResult(action.action_id)"
                        >
                            Open Result
                        </button>
                    </div>
                </div>

                <div class="grid grid-cols-2 md:grid-cols-5 gap-3 mt-4 text-xs">
                    <div
                        class="rounded-lg bg-white/5 border border-white/10 px-3 py-2"
                    >
                        <p class="text-slate-400">Total left</p>
                        <p class="text-slate-100 font-semibold">
                            {{
                                getComparisonResult(action)?.totals
                                    .left_total ?? action.total_items
                            }}
                        </p>
                    </div>
                    <div
                        class="rounded-lg bg-white/5 border border-white/10 px-3 py-2"
                    >
                        <p class="text-slate-400">Total right</p>
                        <p class="text-slate-100 font-semibold">
                            {{
                                getComparisonResult(action)?.totals
                                    .right_total ?? 0
                            }}
                        </p>
                    </div>
                    <div
                        class="rounded-lg bg-white/5 border border-white/10 px-3 py-2"
                    >
                        <p class="text-slate-400">Follows</p>
                        <p class="text-emerald-200 font-semibold">
                            {{
                                getComparisonResult(action)?.totals
                                    .follows_total ?? 0
                            }}
                        </p>
                    </div>
                    <div
                        class="rounded-lg bg-white/5 border border-white/10 px-3 py-2"
                    >
                        <p class="text-slate-400">Missing</p>
                        <p class="text-rose-200 font-semibold">
                            {{
                                getComparisonResult(action)?.totals
                                    .missing_total ?? 0
                            }}
                        </p>
                    </div>
                    <div
                        class="rounded-lg bg-white/5 border border-white/10 px-3 py-2"
                    >
                        <p class="text-slate-400">Processed</p>
                        <p class="text-cyan-200 font-semibold">
                            {{ action.completed_items }} /
                            {{ action.total_items }}
                        </p>
                    </div>
                </div>
            </article>
        </section>
    </section>
</template>
