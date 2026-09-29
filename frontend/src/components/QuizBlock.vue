<template>
	<Quiz
		v-if="user.data || publicFMGE"
		:quizName="quiz"
		:publicFMGE="publicFMGE"
		:day3Mock="day3Mock"
	></Quiz>
	<div v-else class="border rounded-md text-center py-20">
		<div>
			{{ __('Please login to access the quiz.') }}
		</div>
		<Button @click="redirectToLogin()" class="mt-2">
			<span>
				{{ __('Login') }}
			</span>
		</Button>
	</div>
</template>
<script setup>
import { computed, inject } from 'vue'
import { Button } from 'frappe-ui'
import Quiz from '@/components/Quiz.vue'

const user = inject('$user')
const props = defineProps({
	quiz: {
		type: String,
		required: true,
	},
})
const day3Mock = computed(() => props.quiz === 'fmge-psm-day-3-compact-mock')
const publicFMGE = computed(
	() => day3Mock.value || props.quiz === 'fmge-psm-mock-1-section-1'
)

const redirectToLogin = () => {
	window.location.href = `/login`
}
</script>
