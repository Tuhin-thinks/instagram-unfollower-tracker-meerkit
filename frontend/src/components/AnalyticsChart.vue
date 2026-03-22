<script setup lang="ts">
import { ref, onMounted, computed, watch, nextTick } from "vue";
import { useQuery } from "@tanstack/vue-query";
import * as api from "../services/api";
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    LineController,
    Title,
    Tooltip,
    Legend,
    Filler,
} from "chart.js";

ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    LineController,
    Title,
    Tooltip,
    Legend,
    Filler,
);

interface DailyAnalytics {
    date: string;
    new_followers: number;
    unfollowers: number;
    total_followers: number;
}

const props = defineProps<{
    profileId: string;
}>();

const DAY_OPTIONS = [7, 14, 30] as const;
type DayOption = (typeof DAY_OPTIONS)[number];

const selectedDays = ref<DayOption>(30);

const chartCanvas = ref<HTMLCanvasElement | null>(null);
let chartInstance: ChartJS | null = null;

const {
    data: analytics,
    isLoading,
    refetch,
} = useQuery({
    queryKey: computed(() => [
        "analytics",
        props.profileId,
        selectedDays.value,
    ]),
    queryFn: () => api.getAnalytics(selectedDays.value),
    staleTime: Infinity,
    refetchOnWindowFocus: false,
});

async function setDays(days: DayOption) {
    selectedDays.value = days;
    await refetch();
}

const chartData = computed(() => {
    if (!analytics.value || !Array.isArray(analytics.value)) {
        return null;
    }

    // Sort by date ascending for the chart
    const sortedData = [...analytics.value].sort(
        (a: DailyAnalytics, b: DailyAnalytics) =>
            new Date(a.date).getTime() - new Date(b.date).getTime(),
    );

    const labels = sortedData.map((item: DailyAnalytics) => {
        const date = new Date(item.date);
        return date.toLocaleDateString("en-US", {
            month: "short",
            day: "numeric",
        });
    });

    const newFollowersData = sortedData.map(
        (item: DailyAnalytics) => item.new_followers,
    );
    const unfollowersData = sortedData.map(
        (item: DailyAnalytics) => item.unfollowers,
    );
    const totalFollowersData = sortedData.map(
        (item: DailyAnalytics) => item.total_followers,
    );

    return {
        labels,
        datasets: [
            {
                label: "New Followers",
                data: newFollowersData,
                borderColor: "#10b981",
                backgroundColor: "rgba(16, 185, 129, 0.05)",
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: "#10b981",
                pointBorderColor: "#059669",
                pointRadius: 4,
                pointHoverRadius: 6,
                pointBorderWidth: 2,
            },
            {
                label: "Unfollowers",
                data: unfollowersData,
                borderColor: "#ef4444",
                backgroundColor: "rgba(239, 68, 68, 0.05)",
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: "#ef4444",
                pointBorderColor: "#dc2626",
                pointRadius: 4,
                pointHoverRadius: 6,
                pointBorderWidth: 2,
            },
            {
                label: "Total Followers",
                data: totalFollowersData,
                borderColor: "#6366f1",
                backgroundColor: "rgba(99, 102, 241, 0.05)",
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: "#6366f1",
                pointBorderColor: "#4f46e5",
                pointRadius: 4,
                pointHoverRadius: 6,
                pointBorderWidth: 2,
            },
        ],
    };
});

onMounted(() => {
    // If data is already loaded, render immediately
    if (chartData.value && !isLoading.value) {
        setTimeout(() => {
            renderChart();
        }, 100);
    }
});

const renderChart = () => {
    if (!chartCanvas.value) {
        console.warn("❌ Canvas element not found");
        return;
    }

    if (!chartData.value) {
        console.warn("❌ Chart data is not available");
        return;
    }

    // Destroy previous chart instance if it exists
    if (chartInstance) {
        chartInstance.destroy();
        chartInstance = null;
    }

    const ctx = chartCanvas.value.getContext("2d");
    if (!ctx) {
        console.error("❌ Failed to get 2D context from canvas");
        return;
    }

    try {
        chartInstance = new ChartJS(ctx, {
            type: "line",
            data: chartData.value,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: "index",
                    intersect: false,
                },
                plugins: {
                    filler: {
                        propagate: true,
                    },
                    legend: {
                        position: "top" as const,
                        labels: {
                            color: "#cbd5e1",
                            font: {
                                size: 12,
                                weight: 500 as any,
                            },
                            padding: 16,
                            usePointStyle: true,
                        },
                    },
                    title: {
                        display: false,
                    },
                    tooltip: {
                        backgroundColor: "rgba(30, 41, 59, 0.9)",
                        titleColor: "#f1f5f9",
                        bodyColor: "#cbd5e1",
                        borderColor: "rgba(148, 163, 184, 0.2)",
                        borderWidth: 1,
                        padding: 12,
                        displayColors: true,
                        callbacks: {
                            label: function (context: any) {
                                let label = context.dataset.label || "";
                                if (label) {
                                    label += ": ";
                                }
                                if (context.parsed.y !== null) {
                                    label += context.parsed.y.toLocaleString();
                                }
                                return label;
                            },
                        },
                    },
                },
                scales: {
                    x: {
                        display: true,
                        grid: {
                            color: "rgba(148, 163, 184, 0.1)",
                            drawOnChartArea: true,
                            drawTicks: true,
                        },
                        ticks: {
                            color: "#94a3b8",
                            font: {
                                size: 11,
                            },
                        },
                    },
                    y: {
                        display: true,
                        grid: {
                            color: "rgba(148, 163, 184, 0.1)",
                            drawOnChartArea: true,
                            drawTicks: true,
                        },
                        ticks: {
                            color: "#94a3b8",
                            font: {
                                size: 11,
                            },
                            callback: function (value: any) {
                                return value.toLocaleString();
                            },
                        },
                    },
                },
            },
        });
        console.log("✅ Analytics chart rendered successfully");
    } catch (error) {
        console.error("❌ Error rendering chart:", error);
    }
};

// Watch for chartData changes and render when available
watch(
    () => chartData.value,
    async (newChartData) => {
        if (newChartData) {
            await nextTick();
            renderChart();
        }
    },
    { deep: true },
);

// Also watch isLoading to ensure we try rendering after loading completes
watch(isLoading, async (loading) => {
    if (!loading && chartData.value) {
        await nextTick();
        renderChart();
    }
});
</script>

<template>
    <div class="w-full">
        <!-- Loading state -->
        <div
            v-if="isLoading"
            class="h-96 bg-[#16213a] rounded-xl border border-white/[0.07] flex items-center justify-center"
        >
            <div class="text-center">
                <div
                    class="inline-block w-8 h-8 border-3 border-indigo-600 border-t-transparent rounded-full animate-spin mb-3"
                />
                <p class="text-slate-400 text-sm">Loading analytics...</p>
            </div>
        </div>

        <!-- Chart container -->
        <div
            v-else-if="chartData"
            class="bg-[#16213a] rounded-xl border border-white/[0.07] p-6"
        >
            <!-- Day filter buttons -->
            <div class="flex items-center gap-2 mb-5">
                <span class="text-xs text-slate-500 mr-1">Last</span>
                <button
                    v-for="d in DAY_OPTIONS"
                    :key="d"
                    @click="setDays(d)"
                    :class="[
                        'px-3 py-1 text-xs font-medium rounded-full border transition-colors',
                        selectedDays === d
                            ? 'bg-violet-600 border-violet-500 text-white'
                            : 'bg-transparent border-white/10 text-slate-400 hover:border-violet-500/50 hover:text-slate-200',
                    ]"
                >
                    {{ d }}d
                </button>
            </div>
            <div class="w-full" style="height: 400px; position: relative">
                <canvas
                    ref="chartCanvas"
                    width="800"
                    height="400"
                    style="max-width: 100%; height: 100%; display: block"
                ></canvas>
            </div>
        </div>

        <!-- Empty state -->
        <div
            v-else
            class="text-center py-16 text-slate-500 bg-[#16213a] rounded-xl border border-white/[0.07]"
        >
            <p class="text-2xl mb-2">📊</p>
            <p class="font-medium text-slate-400">
                No analytics data available
            </p>
            <p class="text-sm mt-1">
                Complete at least one scan to see analytics.
            </p>
        </div>
    </div>
</template>
