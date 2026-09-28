<template>
	<PageHeader v-if="!fromLesson && !publicFMGE" :breadcrumbs="breadcrumbs" />
	<div
		class="md:w-7/12 md:mx-auto mx-4 py-10"
		:class="{ 'pt-4 md:w-full': fromLesson }"
	>
		<Quiz
			:quizName="quizID"
			:publicFMGE="publicFMGE"
			:learnerName="learnerName"
		/>
	</div>
</template>
<script setup>
import Quiz from '@/components/Quiz.vue'
import { createResource, usePageMeta } from 'frappe-ui'
import PageHeader from '@/components/Layouts/PageHeader.vue'
import { computed, inject, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { sessionStore } from '../stores/session'

const { brand } = sessionStore()
const user = inject('$user')
const router = useRouter()
const fromLesson = ref(false)

onMounted(() => {
	if (!user.data && !props.publicFMGE) {
		router.push({ name: 'Courses' })
	}

	if (new URLSearchParams(window.location.search).get('fromLesson')) {
		fromLesson.value = true
	}
})

const props = defineProps({
	quizID: {
		type: String,
		required: true,
	},
	publicFMGE: {
		type: Boolean,
		default: false,
	},
	learnerName: {
		type: String,
		default: '',
	},
})

const title = createResource({
	url: 'frappe.client.get_value',
	params: {
		doctype: 'LMS Quiz',
		fieldname: 'title',
		filters: {
			name: props.quizID,
		},
	},
	auto: !props.publicFMGE,
})

const breadcrumbs = computed(() => {
	return [
		{
			label: __('Quizzes'),
			route: { name: 'Quizzes' },
		},
		{
			label: title.data?.title,
			route: { name: 'QuizForm', params: { quizID: props.quizID } },
		},
		{ label: __('Test Quiz') },
	]
})

usePageMeta(() => {
	return {
		title: props.publicFMGE
			? props.learnerName
				? __("{0}'s PSM Mock").format(props.learnerName)
				: __('FMGE PSM Mock')
			: `${title.data?.title}`,
		icon: brand.favicon,
	}
})
</script>
