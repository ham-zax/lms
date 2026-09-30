import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

import QuizBlock from '@/components/QuizBlock.vue'

vi.mock('@/components/Quiz.vue', () => ({
	default: {
		name: 'QuizStub',
		props: ['quizName', 'publicFMGE', 'day1Mock', 'day4Mock', 'day3Mock'],
		template: '<div />',
	},
}))

vi.stubGlobal('__', (value: string) => value)

const mountForGuest = (quiz: string) =>
	mount(QuizBlock, {
		props: { quiz },
		global: {
			provide: { $user: { data: null } },
			mocks: { __: (value: string) => value },
		},
	})

describe('FMGE course quiz lessons', () => {
	it.each([
		['fmge-psm-day-1-mock', false],
		['fmge-psm-day-1-section-2', false],
		['fmge-psm-day-4-mock', false],
		['fmge-psm-day-4-section-2', false],
		['fmge-psm-mock-1-section-1', false],
		['day-3-psm-section-1', true],
		['day-3-psm-section-4', true],
	])('opens %s with the public mock flow', (quizName, day3Mock) => {
		const wrapper = mountForGuest(quizName)
		const quiz = wrapper.findComponent({ name: 'QuizStub' })
		expect(quiz.exists()).toBe(true)
		expect(quiz.props()).toMatchObject({
			quizName,
			publicFMGE: true,
			day1Mock: ['fmge-psm-day-1-mock', 'fmge-psm-day-1-section-2'].includes(quizName),
			day4Mock: ['fmge-psm-day-4-mock', 'fmge-psm-day-4-section-2'].includes(quizName),
			day3Mock,
		})
	})

	it('keeps other course quizzes behind login', () => {
		const wrapper = mountForGuest('another-course-quiz')
		expect(wrapper.findComponent({ name: 'QuizStub' }).exists()).toBe(false)
		expect(wrapper.text()).toContain('Please login to access the quiz.')
	})
})
