<script setup lang="ts">
import { computed, ref } from "vue";

const props = defineProps<{
    pkId: string;
    profileId: string;
    alt: string;
    cacheKey?: string | null;
}>();

const hasError = ref(false);
const imageSrc = computed(() => {
    const params = new URLSearchParams({ profile_id: props.profileId });
    if (props.cacheKey) {
        params.set("img_v", props.cacheKey);
    }
    return `/api/image/${props.pkId}?${params.toString()}`;
});
</script>

<template>
    <div
        class="rounded-full overflow-hidden bg-slate-800 shrink-0 flex items-center justify-center"
    >
        <img
            v-if="!hasError"
            :src="imageSrc"
            :alt="props.alt"
            class="w-full h-full object-cover"
            loading="lazy"
            @error="hasError = true"
        />
        <!-- Fallback avatar when image is unavailable -->
        <span v-else class="text-slate-500 text-xl select-none">👤</span>
    </div>
</template>
