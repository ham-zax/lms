"""Day 1 API regressions, using mocked documents without touching site data."""

import inspect
import json
import unittest
from contextlib import ExitStack
from unittest.mock import Mock, patch

import frappe

from lms.fmge import day1_mock, day4_mock, public_quiz
from lms.fmge.day1_course import COURSE as DAY1_COURSE
from lms.fmge.day4_course import COURSE as DAY4_COURSE
from lms.fmge.importer import _load_bank


class TestDay1Mock(unittest.TestCase):
	course = DAY1_COURSE
	endpoint = day1_mock

	def setUp(self):
		self.bank = _load_bank(self.course.bank_file)
		self.questions = {}
		self.rows = []
		for item in self.bank["questions"]:
			name = item["id"]
			question = frappe._dict(
				name=name,
				question=item["stem"],
				type="Choices",
				fmge_bank_id=self.course.bank_id,
				fmge_tier=item["tier"],
				fmge_difficulty=item["difficulty"],
				fmge_source=item["source"],
				fmge_explanation=item["explanation"],
			)
			for i, option in enumerate(item["options"], 1):
				question[f"option_{i}"] = option
				question[f"is_correct_{i}"] = int(item["correct_option"] == "ABCD"[i - 1])
			self.questions[name] = question
			self.rows.append(frappe._dict(name=f"row-{name}", question=name, marks=1))
		self.quiz = frappe._dict(
			name=self.course.quiz_name,
			title=self.bank["title"],
			course=self.course.course_name,
			duration=str(self.course.question_count),
			total_marks=self.course.question_count,
			passing_percentage=50,
			shuffle_questions=0,
			limit_questions_to=0,
			questions=self.rows,
		)
		self.stack = ExitStack()
		self.addCleanup(self.stack.close)
		self.stack.enter_context(patch.object(public_quiz, "_", side_effect=lambda text: text))
		self.stack.enter_context(patch.object(frappe, "throw", side_effect=frappe.ValidationError))
		self.stack.enter_context(patch.object(frappe, "get_doc", side_effect=self._get_doc))
		self.db = Mock()
		self.stack.enter_context(patch.object(frappe, "db", new=self.db))
		self.db.get_value.side_effect = lambda doctype, filters, field: (
			self.course.quiz_name
			if doctype == "LMS Quiz" and filters == {"fmge_bank_id": self.course.bank_id}
			else 1
			if doctype == "LMS Course"
			else None
		)

	def _get_doc(self, doctype, name):
		return self.quiz if doctype == "LMS Quiz" else self.questions[name]

	def test_guest_payload_has_all_questions_without_keys_or_explanations(self):
		payload = inspect.unwrap(getattr(self.endpoint, f"get_public_day{self.course.day}_quiz"))()
		self.assertEqual(payload["quiz"]["name"], self.course.quiz_name)
		self.assertEqual(len(payload["questions_by_name"]), self.course.question_count)
		for question in payload["questions_by_name"].values():
			self.assertFalse(any("correct" in key or "explanation" in key for key in question))

	def test_grading_uses_day1_keys_and_day1_source_links(self):
		answers = [
			{"question_name": name, "answer": [public_quiz._correct_answer(question)]}
			for name, question in self.questions.items()
		]
		result = inspect.unwrap(getattr(self.endpoint, f"submit_public_day{self.course.day}_quiz"))(
			json.dumps(answers)
		)
		self.assertEqual(result["score"], self.course.question_count)
		self.assertEqual(result["percentage"], 100)
		self.assertEqual(len(result["review"]), self.course.question_count)
		for review in result["review"]:
			self.assertEqual(review["source_document"], f"Day {self.course.day} PSM notes")
			self.assertTrue(review["source_url"].startswith(self.course.source_pdf_url + "#page="))

	def test_unanswered_attempt_scores_zero(self):
		result = inspect.unwrap(getattr(self.endpoint, f"submit_public_day{self.course.day}_quiz"))("[]")
		self.assertEqual(result["score"], 0)
		self.assertEqual(result["score_out_of"], self.course.question_count)

	def test_unpublished_course_is_unavailable(self):
		self.db.get_value.side_effect = lambda doctype, *args: (
			self.course.quiz_name if doctype == "LMS Quiz" else 0
		)
		with self.assertRaises(frappe.ValidationError):
			inspect.unwrap(getattr(self.endpoint, f"get_public_day{self.course.day}_quiz"))()

	def test_other_bank_question_is_rejected(self):
		self.questions[self.rows[0].question].fmge_bank_id = "fmge-psm-block-1"
		with self.assertRaises(frappe.ValidationError):
			inspect.unwrap(getattr(self.endpoint, f"get_public_day{self.course.day}_quiz"))()

	def test_invalid_duplicate_and_foreign_answers_are_rejected(self):
		submit = inspect.unwrap(getattr(self.endpoint, f"submit_public_day{self.course.day}_quiz"))
		answer = {"question_name": self.rows[0].question, "answer": ["not an option"]}
		for payload in [
			"not json",
			"{}",
			json.dumps([answer]),
			json.dumps(
				[
					{"question_name": self.rows[0].question, "answer": []},
					{"question_name": self.rows[0].question, "answer": []},
				]
			),
			json.dumps([{"question_name": "PSM-B1-Q001", "answer": []}]),
		]:
			with self.subTest(payload=payload), self.assertRaises(frappe.ValidationError):
				submit(payload)

	def test_practice_feedback_uses_correct_pdf(self):
		name = self.rows[0].question
		result = inspect.unwrap(getattr(self.endpoint, f"check_public_day{self.course.day}_answer"))(
			name, self.questions[name].option_1
		)
		self.assertTrue(result["source_url"].startswith(self.course.source_pdf_url))
		with self.assertRaises(frappe.ValidationError):
			inspect.unwrap(getattr(self.endpoint, f"check_public_day{self.course.day}_answer"))(
				"PSM-B1-Q001", "A"
			)


class TestDay4Mock(TestDay1Mock):
	course = DAY4_COURSE
	endpoint = day4_mock
