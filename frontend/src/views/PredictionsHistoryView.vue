<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { RouterLink } from "vue-router";
import PredictionStatusBadge from "../components/prediction/PredictionStatusBadge.vue";
import ProbabilityChip from "../components/prediction/ProbabilityChip.vue";
import * as api from "../services/api";
import { extractApiErrorMessage } from "../services/targetAccessErrors";
import type { PredictionRecord } from "../types/prediction";

const props = defineProps<{
    profileId: string;
    profileUsername?: string | null;
}>();

const router = useRouter();
const predictionHistory = ref<PredictionRecord[]>([]);
const loading = ref(false);
const historyError = ref("");
const hasMore = ref(true);
const offset = ref(0);
const pageSize = 10;

function openBulkPredictions() {
    void router.push({ name: "predictions" });
}

async function loadPredictionHistory(reset = false) {
    if (loading.value) {
        return;
    }
    loading.value = true;
    historyError.value = "";

    if (reset) {
        offset.value = 0;
        hasMore.value = true;
        predictionHistory.value = [];
    }

    try {
        const items = await api.getPredictionHistory({
            limit: pageSize,
            offset: offset.value,
        });
        if (reset) {
            predictionHistory.value = items;
        } else {
            predictionHistory.value = [...predictionHistory.value, ...items];
        }
        offset.value += items.length;
        hasMore.value = items.length === pageSize;
    } catch (error: unknown) {
        historyError.value =
            extractApiErrorMessage(error) ||
            "Could not load prediction history right now.";
    } finally {
        loading.value = false;
    }
}

onMounted(() => {
    void loadPredictionHistory(true);
});
</script>

<template>
    <section class="space-y-6 fade-in">
        <header
            class="rounded-3xl border border-white/10 lrc-results-header p-6 md:p-8 relative overflow-hidden"
        >
            <button
                class="btn-ghost rounded-lg px-3 py-1.5 text-xs mb-5 inline-flex items-center gap-1.5 relative z-10"
                @click="openBulkPredictions"
            >
                ← Back to Bulk Predictions
            </button>

            <div
                class="relative z-10 flex flex-wrap items-start justify-between gap-4"
            >
                <div>
                    <p
                        class="text-xs uppercase tracking-[0.22em] text-cyan-100/90 font-semibold"
                    >
                        Follow-Back Predictions
                    </p>
                    <h2
                        class="text-2xl md:text-4xl font-display font-bold text-white mt-2"
                    >
                        Prediction History
                    </h2>
                    <p
                        class="text-sm text-slate-100/85 mt-3 max-w-3xl leading-relaxed"
                    >
                        Review past prediction runs without interrupting your
                        active bulk prediction workflow.
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

                <button
                    class="btn-ghost rounded-lg px-3 py-1.5 text-xs"
                    :disabled="loading"
                    @click="loadPredictionHistory(true)"
                >
                    Refresh
                </button>
            </div>
        </header>

        <div
            v-if="historyError"
            class="rounded-2xl border border-rose-400/25 bg-rose-500/10 text-rose-200 px-4 py-3 text-sm"
        >
            {{ historyError }}
        </div>

        <div
            v-else-if="loading && !predictionHistory.length"
            class="rounded-2xl border border-white/10 bg-[#121d33] px-4 py-6 text-sm text-slate-300"
        >
            Loading prediction history...
        </div>

        <div
            v-else-if="!predictionHistory.length"
            class="rounded-2xl border border-white/10 bg-[#121d33] px-4 py-6 text-sm text-slate-300"
        >
            No prediction history found yet.
        </div>

        <section
            v-else
            class="rounded-2xl border border-white/10 bg-[#121d33] overflow-hidden"
        >
            <div class="divide-y divide-white/[0.07]">
                <div
                    v-for="entry in predictionHistory"
                    :key="entry.prediction_id"
                    class="px-4 py-3 grid lg:grid-cols-[1.3fr,0.8fr,1fr,1fr] gap-3 items-start"
                >
                    <div>
                        <p class="font-semibold text-sm text-slate-100">
                            @{{ entry.target_username || "unknown" }}
                        </p>
                        <p class="text-[11px] text-slate-500 mt-1 break-all">
                            {{ entry.target_profile_id }}
                        </p>
                        <p class="text-[11px] text-slate-500 mt-1">
                            {{ new Date(entry.requested_at).toLocaleString() }}
                        </p>
                    </div>

                    <div>
                        <PredictionStatusBadge :status="entry.status" />
                    </div>

                    <div>
                        <ProbabilityChip
                            :probability="entry.probability"
                            :confidence="entry.confidence"
                        />
                    </div>

                    <div class="lg:justify-self-end">
                        <RouterLink
                            v-if="entry.target_username"
                            :to="{
                                name: 'discovery',
                                params: { username: entry.target_username },
                            }"
                            class="text-xs text-cyan-400 hover:text-cyan-300 font-medium"
                        >
                            Open discovery
                        </RouterLink>
                    </div>
                </div>
            </div>

            <div class="px-4 py-3 border-t border-white/[0.07] bg-white/[0.02]">
                <button
                    v-if="hasMore"
                    class="btn-ghost px-4 py-2 rounded-lg text-sm font-semibold"
                    :disabled="loading"
                    @click="loadPredictionHistory(false)"
                >
                    {{ loading ? "Loading..." : "Load 10 more" }}
                </button>
                <p v-else class="text-xs text-slate-400">
                    End of prediction history.
                </p>
            </div>
        </section>
    </section>
</template>
