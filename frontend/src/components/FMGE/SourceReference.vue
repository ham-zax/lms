<template>
	<div
		v-if="item.source_pages || item.source_url"
		class="flex items-start gap-2 text-sm leading-5 text-ink-gray-7"
	>
		<!-- Icon beside the text, not wrapping onto its own line on a phone. -->
		<span class="lucide-book-open mt-0.5 size-4 shrink-0 text-ink-gray-5" />
		<div class="min-w-0">
			<span>
				{{ item.source_document }}
				<template v-if="item.source_pages">
					·
					<span class="whitespace-nowrap">{{
						(isPageRange ? __('pages {0}') : __('page {0}')).format(
							item.source_pages
						)
					}}</span>
				</template>
				<span v-if="item.source_detail" class="text-ink-gray-5">
					({{ item.source_detail }})
				</span>
			</span>
			<a
				v-if="item.source_url"
				:href="item.source_url"
				target="_blank"
				rel="noopener"
				class="ms-1 whitespace-nowrap font-medium text-ink-blue-link underline underline-offset-2"
			>
				{{ __('Open in notes') }}
			</a>
		</div>
	</div>
</template>
<script setup>
import { computed } from 'vue'

const props = defineProps({
	// A practice or review row from lms.fmge.public_quiz.
	item: {
		type: Object,
		required: true,
	},
})

const isPageRange = computed(() => /[–,-]/.test(props.item.source_pages || ''))
</script>
