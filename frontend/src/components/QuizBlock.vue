<template>
	<Quiz
		v-if="user.data || publicFMGE"
		:quizName="quiz"
		:publicFMGE="publicFMGE"
		:day1Mock="day1Mock"
		:day4Mock="day4Mock"
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
const day1Mock = computed(() => ['fmge-psm-day-1-mock', 'fmge-psm-day-1-section-2'].includes(props.quiz))
const day4Mock = computed(() => ['fmge-psm-day-4-mock', 'fmge-psm-day-4-section-2'].includes(props.quiz))
const day3Mock = computed(() => /^day-3-psm-section-[1-4]$/.test(props.quiz))
const publicFMGE = computed(
	() => day1Mock.value || day4Mock.value || day3Mock.value || props.quiz === 'fmge-psm-mock-1-section-1'
)

const redirectToLogin = () => {
	window.location.href = `/login`
}
</script>
