<script setup lang="ts">
const props = defineProps<{
    profileId: string;
    profileUsername?: string | null;
}>();

const emit = defineEmits<{
    openIntelligentBatchFollow: [];
    openBatchUnfollow: [];
}>();

const automationCards = [
    {
        key: "follow",
        icon: "🧠",
        status: "Ready",
        title: "Intelligent Batch Follow Users",
        description:
            "Predict follow potential at scale. Users above 80% probability are auto-selected for a confirm step before execution.",
        tags: ["Probability Filters", "Queued Workers", "Manual Confirm"],
        accentClass: "text-cyan-200",
        iconClass: "bg-cyan-400/15 border-cyan-300/30 text-cyan-200",
    },
    {
        key: "unfollow",
        icon: "🧹",
        status: "Ready",
        title: "Batch Unfollow Users",
        description:
            "Stage non-following accounts for unfollow confirmation while preserving protected accounts on a never-unfollow list.",
        tags: ["Not Following Back", "Protected List", "Manual Confirm"],
        accentClass: "text-rose-200",
        iconClass: "bg-rose-400/15 border-rose-300/30 text-rose-200",
    },
] as const;

function openCard(cardKey: string) {
    if (cardKey === "unfollow") {
        emit("openBatchUnfollow");
        return;
    }

    emit("openIntelligentBatchFollow");
}
</script>

<template>
    <section class="space-y-6 fade-in">
        <header
            class="automation-hero rounded-3xl p-6 md:p-8 border border-white/10 shadow-2xl shadow-black/30 overflow-hidden relative"
        >
            <div
                class="absolute -top-24 -right-10 w-64 h-64 rounded-full bg-cyan-400/20 blur-3xl pointer-events-none"
            />
            <div
                class="absolute -bottom-24 left-10 w-72 h-72 rounded-full bg-emerald-400/15 blur-3xl pointer-events-none"
            />

            <div class="relative z-10">
                <p
                    class="text-xs uppercase tracking-[0.22em] text-cyan-200/90 font-semibold"
                >
                    Automation Studio
                </p>
                <h2
                    class="text-2xl md:text-3xl font-display font-bold text-white mt-2"
                >
                    Set Smart Behaviors Once.
                    <span class="text-gradient"
                        >Let the App Handle Repetitive Work.</span
                    >
                </h2>
                <p
                    class="text-sm md:text-base text-slate-200/85 mt-3 max-w-3xl leading-relaxed"
                >
                    Build long-running follower workflows that execute on
                    backend worker threads while keeping approvals and
                    exclusions visible in one place.
                </p>

                <div
                    class="mt-5 inline-flex items-center gap-2 rounded-xl border border-cyan-300/25 bg-cyan-300/10 px-3 py-1.5 text-xs text-cyan-100"
                >
                    <span
                        class="h-2 w-2 rounded-full bg-cyan-300 animate-pulse"
                    />
                    Active profile:
                    {{ props.profileUsername ? '@' + props.profileUsername : props.profileId }}
                </div>
            </div>
        </header>

        <div class="grid sm:grid-cols-2 xl:grid-cols-3 gap-5">
            <article
                v-for="card in automationCards"
                :key="card.key"
                class="automation-card group rounded-2xl border border-white/10 bg-[#172544]/85 p-5 md:p-6 cursor-pointer relative overflow-hidden"
                role="button"
                tabindex="0"
                @click="openCard(card.key)"
                @keydown.enter="openCard(card.key)"
                @keydown.space.prevent="openCard(card.key)"
            >
                <div
                    class="absolute inset-0 automation-card-glow pointer-events-none"
                />

                <div class="relative z-10">
                    <div class="flex items-center justify-between gap-3">
                        <div
                            :class="card.iconClass"
                            class="inline-flex h-12 w-12 items-center justify-center rounded-xl border text-xl"
                        >
                            {{ card.icon }}
                        </div>
                        <span
                            class="text-[11px] font-semibold uppercase tracking-wide px-2 py-1 rounded-full bg-emerald-400/15 text-emerald-300 border border-emerald-400/25"
                        >
                            {{ card.status }}
                        </span>
                    </div>

                    <h3 class="text-lg font-semibold text-slate-100 mt-4">
                        {{ card.title }}
                    </h3>
                    <p class="text-sm text-slate-300/90 mt-2 leading-relaxed">
                        {{ card.description }}
                    </p>

                    <div class="mt-5 flex flex-wrap gap-2">
                        <span
                            v-for="tag in card.tags"
                            :key="tag"
                            class="automation-tag"
                            >{{ tag }}</span
                        >
                    </div>

                    <div
                        :class="card.accentClass"
                        class="mt-5 text-sm font-semibold inline-flex items-center gap-1.5"
                    >
                        Configure automation
                        <span
                            class="transition-transform duration-300 group-hover:translate-x-1"
                            >→</span
                        >
                    </div>
                </div>
            </article>
        </div>
    </section>
</template>

<style scoped>
.automation-hero {
    background:
        linear-gradient(
            120deg,
            rgba(22, 38, 76, 0.96) 0%,
            rgba(16, 47, 92, 0.92) 54%,
            rgba(18, 74, 86, 0.9) 100%
        ),
        radial-gradient(
            circle at 14% 25%,
            rgba(34, 211, 238, 0.18),
            transparent 40%
        ),
        radial-gradient(
            circle at 86% 78%,
            rgba(74, 222, 128, 0.2),
            transparent 44%
        );
}

.automation-card {
    box-shadow: 0 14px 36px rgba(0, 0, 0, 0.3);
    transition:
        transform 0.25s ease,
        border-color 0.25s ease,
        box-shadow 0.25s ease;
}

.automation-card:hover,
.automation-card:focus-visible {
    transform: translateY(-3px);
    border-color: rgba(56, 189, 248, 0.45);
    box-shadow: 0 18px 44px rgba(8, 47, 73, 0.45);
    outline: none;
}

.automation-card-glow {
    background:
        radial-gradient(
            circle at 100% 0%,
            rgba(34, 211, 238, 0.14),
            transparent 48%
        ),
        radial-gradient(
            circle at 0% 100%,
            rgba(74, 222, 128, 0.12),
            transparent 52%
        );
    opacity: 0;
    transition: opacity 0.24s ease;
}

.automation-card:hover .automation-card-glow,
.automation-card:focus-visible .automation-card-glow {
    opacity: 1;
}

.automation-tag {
    font-size: 0.7rem;
    letter-spacing: 0.02em;
    color: rgb(186 230 253);
    border: 1px solid rgba(125, 211, 252, 0.25);
    background: rgba(56, 189, 248, 0.08);
    padding: 0.24rem 0.55rem;
    border-radius: 999px;
}
</style>
