<script setup lang="ts">
import { computed, ref } from "vue";

const props = defineProps<{
    profileId: string;
}>();

const emit = defineEmits<{
    backToAutomation: [];
}>();

const targetInput = ref("");
const doNotFollowInput = ref("");
const minProbability = ref(80);
const maxFollowCount = ref(40);
const includePrivateAccounts = ref(false);
const respectRecentInteractions = ref(true);

const placeholder = [
    "andrea.design",
    "https://www.instagram.com/sam.creates/",
    "57934512056",
].join("\n");

const doNotFollowPlaceholder = [
    "close_friend_alt",
    "https://www.instagram.com/brand_do_not_touch/",
    "client_account",
].join("\n");

function parseUniqueEntries(raw: string) {
    return Array.from(
        new Set(
            raw
                .split(/[\n,]/)
                .map((token) => token.trim())
                .filter(Boolean),
        ),
    );
}

const parsedTargets = computed(() => {
    return parseUniqueEntries(targetInput.value);
});

const doNotFollowAccounts = computed(() =>
    parseUniqueEntries(doNotFollowInput.value),
);

const estimatedSelected = computed(() => {
    const ratio = Math.min(
        Math.max((100 - minProbability.value) / 100, 0.08),
        0.35,
    );
    const candidateCount = Math.max(
        parsedTargets.value.length - doNotFollowAccounts.value.length,
        0,
    );
    return Math.min(maxFollowCount.value, Math.round(candidateCount * ratio));
});

function goBack() {
    emit("backToAutomation");
}
</script>

<template>
    <section class="space-y-6 fade-in">
        <header
            class="rounded-3xl border border-white/10 ibf-header p-6 md:p-8 relative overflow-hidden"
        >
            <div
                class="absolute right-4 top-4 h-32 w-32 rounded-full bg-cyan-400/20 blur-3xl pointer-events-none"
            />
            <div
                class="absolute left-8 bottom-0 h-24 w-24 rounded-full bg-orange-400/20 blur-2xl pointer-events-none"
            />

            <button
                class="btn-ghost rounded-lg px-3 py-1.5 text-xs mb-5 inline-flex items-center gap-1.5 relative z-10"
                @click="goBack"
            >
                ← Back to Automation
            </button>

            <div class="relative z-10">
                <p
                    class="text-xs uppercase tracking-[0.22em] text-cyan-100/90 font-semibold"
                >
                    Automation: Intelligent Batch Follow
                </p>
                <h2
                    class="text-2xl md:text-3xl font-display font-bold text-white mt-2"
                >
                    Build Your Follow Queue with Confidence
                </h2>
                <p
                    class="text-sm text-slate-100/85 mt-3 max-w-3xl leading-relaxed"
                >
                    The workflow will score each target and auto-select accounts
                    above the probability threshold. Selected users are staged
                    for a final <strong>Confirm Batch Follow</strong> action.
                </p>
                <p class="text-xs text-cyan-100/80 mt-4">
                    Active profile: {{ props.profileId }}
                </p>
            </div>
        </header>

        <div class="grid xl:grid-cols-[1.15fr,0.85fr] gap-6">
            <section class="space-y-6">
                <div
                    class="rounded-2xl border border-white/10 bg-[#16213a]/95 p-5 md:p-6 shadow-2xl shadow-black/30"
                >
                    <div class="flex items-center justify-between gap-3 mb-3">
                        <h3 class="text-lg font-semibold text-slate-100">
                            Target Input
                        </h3>
                        <span
                            class="text-xs px-2.5 py-1 rounded-full border border-cyan-300/30 bg-cyan-300/10 text-cyan-200"
                        >
                            {{ parsedTargets.length }} unique targets
                        </span>
                    </div>

                    <p class="text-sm text-slate-400">
                        Paste usernames, profile links, or numeric user IDs. One
                        per line or comma-separated.
                    </p>
                    <p class="text-xs text-slate-500 mt-2">
                        Accepted formats: <strong>@username</strong>, full
                        Instagram profile link, or numeric ID.
                    </p>
                    <textarea
                        v-model="targetInput"
                        rows="10"
                        class="input-dark mt-4"
                        :placeholder="placeholder"
                    />
                </div>

                <div
                    class="rounded-2xl border border-white/10 bg-[#16213a]/95 p-5 md:p-6 shadow-2xl shadow-black/30"
                >
                    <div class="flex items-center justify-between gap-3 mb-3">
                        <h3 class="text-lg font-semibold text-slate-100">
                            Do Not Follow List
                        </h3>
                        <span
                            class="text-xs px-2.5 py-1 rounded-full border border-amber-300/30 bg-amber-300/10 text-amber-200"
                        >
                            {{ doNotFollowAccounts.length }} excluded
                        </span>
                    </div>

                    <p class="text-sm text-slate-400">
                        Add accounts that must never be auto-selected for
                        follow, even if they pass the probability threshold. Use
                        either usernames or full Instagram profile links.
                    </p>
                    <p class="text-xs text-slate-500 mt-2">
                        Safekeeping entries can be pasted exactly as copied from
                        Instagram links.
                    </p>
                    <textarea
                        v-model="doNotFollowInput"
                        rows="7"
                        class="input-dark mt-4"
                        :placeholder="doNotFollowPlaceholder"
                    />
                </div>
            </section>

            <section
                class="rounded-2xl border border-white/10 bg-[#16213a]/95 p-5 md:p-6 shadow-2xl shadow-black/30"
            >
                <h3 class="text-lg font-semibold text-slate-100">
                    Selection Strategy
                </h3>
                <p class="text-sm text-slate-400 mt-1">
                    Configure auto-selection controls before follow execution.
                </p>

                <div class="space-y-5 mt-5">
                    <label class="block">
                        <span class="text-sm font-medium text-slate-200"
                            >Minimum Probability (%)</span
                        >
                        <div class="mt-2 flex items-center gap-3">
                            <input
                                v-model.number="minProbability"
                                type="range"
                                min="50"
                                max="95"
                                step="1"
                                class="w-full accent-cyan-400"
                            />
                            <span
                                class="w-12 text-right text-sm font-semibold text-cyan-300"
                                >{{ minProbability }}%</span
                            >
                        </div>
                    </label>

                    <label class="block">
                        <span class="text-sm font-medium text-slate-200"
                            >Max Users Per Batch</span
                        >
                        <input
                            v-model.number="maxFollowCount"
                            type="number"
                            min="1"
                            max="500"
                            class="input-dark mt-2"
                        />
                    </label>

                    <label
                        class="flex items-center justify-between rounded-xl border border-white/10 bg-white/[0.03] px-3 py-2.5"
                    >
                        <span class="text-sm text-slate-200"
                            >Include private accounts</span
                        >
                        <input
                            v-model="includePrivateAccounts"
                            type="checkbox"
                            class="h-4 w-4 accent-cyan-400"
                        />
                    </label>

                    <label
                        class="flex items-center justify-between rounded-xl border border-white/10 bg-white/[0.03] px-3 py-2.5"
                    >
                        <span class="text-sm text-slate-200"
                            >Respect recent interactions</span
                        >
                        <input
                            v-model="respectRecentInteractions"
                            type="checkbox"
                            class="h-4 w-4 accent-cyan-400"
                        />
                    </label>
                </div>

                <div
                    class="mt-6 rounded-xl ibf-summary border border-cyan-300/25 p-4"
                >
                    <p class="text-xs uppercase tracking-wide text-cyan-100/80">
                        Preview
                    </p>
                    <p class="text-sm text-slate-100 mt-1">
                        Users scoring at least
                        <strong>{{ minProbability }}%</strong> will be
                        auto-selected for confirmation.
                    </p>
                    <p class="text-sm text-slate-300 mt-1">
                        Accounts excluded from follow:
                        <strong class="text-amber-200">{{
                            doNotFollowAccounts.length
                        }}</strong>
                    </p>
                    <p class="text-sm text-slate-300 mt-1">
                        Estimated selected:
                        <strong class="text-emerald-300">{{
                            estimatedSelected
                        }}</strong>
                        of {{ parsedTargets.length }} targets
                    </p>
                </div>

                <div class="mt-6 grid sm:grid-cols-2 gap-3">
                    <button
                        class="btn-violet rounded-xl px-4 py-2.5 text-sm font-semibold opacity-80 cursor-not-allowed"
                        disabled
                    >
                        Confirm Batch Follow
                    </button>
                    <button
                        class="btn-ghost rounded-xl px-4 py-2.5 text-sm font-semibold opacity-80 cursor-not-allowed"
                        disabled
                    >
                        Start Background Task
                    </button>
                </div>

                <p class="text-xs text-amber-300/90 mt-3">
                    Backend integration pending: buttons are intentionally
                    disabled for now.
                </p>
            </section>
        </div>
    </section>
</template>

<style scoped>
.ibf-header {
    background:
        linear-gradient(
            125deg,
            rgba(12, 38, 74, 0.95) 0%,
            rgba(7, 70, 76, 0.9) 54%,
            rgba(83, 52, 22, 0.82) 100%
        ),
        radial-gradient(
            circle at 20% 22%,
            rgba(56, 189, 248, 0.24),
            transparent 36%
        ),
        radial-gradient(
            circle at 84% 66%,
            rgba(251, 191, 36, 0.2),
            transparent 40%
        );
}

.ibf-summary {
    background: linear-gradient(
        135deg,
        rgba(14, 56, 84, 0.55) 0%,
        rgba(18, 82, 77, 0.38) 100%
    );
    box-shadow: inset 0 0 0 1px rgba(125, 211, 252, 0.12);
}
</style>
