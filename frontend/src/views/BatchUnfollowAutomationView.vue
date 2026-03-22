<script setup lang="ts">
import { computed, ref } from "vue";

const props = defineProps<{
    profileId: string;
}>();

const emit = defineEmits<{
    backToAutomation: [];
}>();

const targetInput = ref("");
const protectedAccountsInput = ref("");
const maxUnfollowCount = ref(50);
const requireMutualHistoryCheck = ref(true);
const skipRecentFollows = ref(true);

const placeholder = [
    "old_brand_collab",
    "https://www.instagram.com/archive.second/",
    "62841752014",
].join("\n");

const protectedPlaceholder = [
    "best_friend_main",
    "https://www.instagram.com/best_friend_backup/",
    "team_account",
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

const parsedTargets = computed(() => parseUniqueEntries(targetInput.value));
const protectedAccounts = computed(() =>
    parseUniqueEntries(protectedAccountsInput.value),
);
const estimatedUnfollow = computed(() => {
    const protectedCount = protectedAccounts.value.length;
    const candidateCount = Math.max(
        parsedTargets.value.length - protectedCount,
        0,
    );
    return Math.min(candidateCount, maxUnfollowCount.value);
});

function goBack() {
    emit("backToAutomation");
}
</script>

<template>
    <section class="space-y-6 fade-in">
        <header
            class="rounded-3xl border border-white/10 buf-header p-6 md:p-8 relative overflow-hidden"
        >
            <div
                class="absolute right-2 top-8 h-40 w-40 rounded-full bg-rose-400/20 blur-3xl pointer-events-none"
            />
            <div
                class="absolute left-10 bottom-0 h-24 w-28 rounded-full bg-amber-400/20 blur-2xl pointer-events-none"
            />

            <button
                class="btn-ghost rounded-lg px-3 py-1.5 text-xs mb-5 inline-flex items-center gap-1.5 relative z-10"
                @click="goBack"
            >
                ← Back to Automation
            </button>

            <div class="relative z-10">
                <p
                    class="text-xs uppercase tracking-[0.22em] text-rose-100/90 font-semibold"
                >
                    Automation: Batch Unfollow
                </p>
                <h2
                    class="text-2xl md:text-3xl font-display font-bold text-white mt-2"
                >
                    Clear Non-Reciprocal Accounts Without Touching Protected
                    Ones
                </h2>
                <p
                    class="text-sm text-slate-100/85 mt-3 max-w-3xl leading-relaxed"
                >
                    This workflow prepares an unfollow queue from accounts that
                    do not follow back, then requires confirmation before
                    execution. Protected accounts are never selected even if
                    they match the unfollow logic.
                </p>
                <p class="text-xs text-rose-100/80 mt-4">
                    Active profile: {{ props.profileId }}
                </p>
            </div>
        </header>

        <div class="grid xl:grid-cols-[1.1fr,0.9fr] gap-6">
            <section class="space-y-6">
                <div
                    class="rounded-2xl border border-white/10 bg-[#16213a]/95 p-5 md:p-6 shadow-2xl shadow-black/30"
                >
                    <div class="flex items-center justify-between gap-3 mb-3">
                        <h3 class="text-lg font-semibold text-slate-100">
                            Unfollow Candidates
                        </h3>
                        <span
                            class="text-xs px-2.5 py-1 rounded-full border border-rose-300/30 bg-rose-300/10 text-rose-200"
                        >
                            {{ parsedTargets.length }} queued
                        </span>
                    </div>
                    <p class="text-sm text-slate-400">
                        Paste usernames, links, or IDs to review against the
                        not-following-back rule.
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
                            Never Unfollow List
                        </h3>
                        <span
                            class="text-xs px-2.5 py-1 rounded-full border border-amber-300/30 bg-amber-300/10 text-amber-200"
                        >
                            {{ protectedAccounts.length }} protected
                        </span>
                    </div>
                    <p class="text-sm text-slate-400">
                        Add friends, personal backups, partner accounts, or any
                        relationship you want excluded from automated unfollow
                        selection. Usernames and full Instagram profile links
                        are both supported.
                    </p>
                    <p class="text-xs text-slate-500 mt-2">
                        Protected entries can be pasted directly from Instagram
                        profile URLs.
                    </p>
                    <textarea
                        v-model="protectedAccountsInput"
                        rows="7"
                        class="input-dark mt-4"
                        :placeholder="protectedPlaceholder"
                    />
                </div>
            </section>

            <section
                class="rounded-2xl border border-white/10 bg-[#16213a]/95 p-5 md:p-6 shadow-2xl shadow-black/30"
            >
                <h3 class="text-lg font-semibold text-slate-100">
                    Unfollow Guardrails
                </h3>
                <p class="text-sm text-slate-400 mt-1">
                    Tune the queue before background execution is enabled.
                </p>

                <div class="space-y-5 mt-5">
                    <label class="block">
                        <span class="text-sm font-medium text-slate-200"
                            >Max Users Per Batch</span
                        >
                        <input
                            v-model.number="maxUnfollowCount"
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
                            >Require mutual-history check</span
                        >
                        <input
                            v-model="requireMutualHistoryCheck"
                            type="checkbox"
                            class="h-4 w-4 accent-rose-400"
                        />
                    </label>

                    <label
                        class="flex items-center justify-between rounded-xl border border-white/10 bg-white/[0.03] px-3 py-2.5"
                    >
                        <span class="text-sm text-slate-200"
                            >Skip recently followed accounts</span
                        >
                        <input
                            v-model="skipRecentFollows"
                            type="checkbox"
                            class="h-4 w-4 accent-rose-400"
                        />
                    </label>
                </div>

                <div
                    class="mt-6 rounded-xl buf-summary border border-rose-300/25 p-4"
                >
                    <p class="text-xs uppercase tracking-wide text-rose-100/85">
                        Preview
                    </p>
                    <p class="text-sm text-slate-100 mt-1">
                        Accounts detected as
                        <strong>not following back</strong> will be staged for
                        confirmation.
                    </p>
                    <p class="text-sm text-slate-300 mt-1">
                        Protected accounts excluded:
                        <strong class="text-amber-200">{{
                            protectedAccounts.length
                        }}</strong>
                    </p>
                    <p class="text-sm text-slate-300 mt-1">
                        Estimated ready to unfollow:
                        <strong class="text-rose-200">{{
                            estimatedUnfollow
                        }}</strong>
                        of {{ parsedTargets.length }} candidates
                    </p>
                </div>

                <div class="mt-6 grid sm:grid-cols-2 gap-3">
                    <button
                        class="btn-danger rounded-xl px-4 py-2.5 text-sm font-semibold opacity-80 cursor-not-allowed"
                        disabled
                    >
                        Confirm Batch Unfollow
                    </button>
                    <button
                        class="btn-ghost rounded-xl px-4 py-2.5 text-sm font-semibold opacity-80 cursor-not-allowed"
                        disabled
                    >
                        Start Background Task
                    </button>
                </div>

                <p class="text-xs text-amber-300/90 mt-3">
                    Backend integration pending: UI only, execution
                    intentionally disabled.
                </p>
            </section>
        </div>
    </section>
</template>

<style scoped>
.buf-header {
    background:
        linear-gradient(
            125deg,
            rgba(68, 24, 41, 0.95) 0%,
            rgba(98, 31, 63, 0.9) 52%,
            rgba(102, 49, 20, 0.84) 100%
        ),
        radial-gradient(
            circle at 20% 22%,
            rgba(251, 113, 133, 0.24),
            transparent 36%
        ),
        radial-gradient(
            circle at 82% 68%,
            rgba(251, 191, 36, 0.18),
            transparent 38%
        );
}

.buf-summary {
    background: linear-gradient(
        135deg,
        rgba(95, 29, 55, 0.55) 0%,
        rgba(120, 53, 15, 0.28) 100%
    );
    box-shadow: inset 0 0 0 1px rgba(253, 164, 175, 0.12);
}
</style>
