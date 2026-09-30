"""Day 1 API regressions, using mocked documents without touching site data."""

import inspect
import json
import unittest
from contextlib import ExitStack
from unittest.mock import Mock, patch

import frappe

from lms.fmge import course, day1_mock, day4_mock, public_quiz
from lms.fmge.day1_course import COURSE as DAY1_COURSE
from lms.fmge.day4_course import COURSE as DAY4_COURSE
from lms.fmge.importer import _load_bank


class TestDay1Mock(unittest.TestCase):
	course = DAY1_COURSE
	endpoint = day1_mock
	section = 1

	def setUp(self):
		self.section_data = self.course.section(self.section)
		self.bank = _load_bank(self.section_data["bank_file"])
		self.question_count = len(self.bank["questions"])
		self.questions = {}
		self.rows = []
		for item in self.bank["questions"]:
			name = item["id"]
			question = frappe._dict(
				name=name,
				question=item["stem"],
				type="Choices",
				fmge_bank_id=self.section_data["bank_id"],
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
			name=self.section_data["quiz_name"],
			title=self.bank["title"],
			course=self.course.course_name,
			duration=str(self.question_count),
			total_marks=self.question_count,
			passing_percentage=50,
			shuffle_questions=0,
			limit_questions_to=0,
			questions=self.rows,
		)
		self.stack = ExitStack()
		self.addCleanup(self.stack.close)
		self.stack.enter_context(patch.object(public_quiz, "_", side_effect=lambda text: text))
		self.stack.enter_context(patch.object(course, "_", side_effect=lambda text: text))
		self.stack.enter_context(patch.object(frappe, "throw", side_effect=frappe.ValidationError))
		self.stack.enter_context(patch.object(frappe, "get_doc", side_effect=self._get_doc))
		self.db = Mock()
		self.stack.enter_context(patch.object(frappe, "db", new=self.db))
		self.db.get_value.side_effect = lambda doctype, filters, field: (
			self.section_data["quiz_name"]
			if doctype == "LMS Quiz" and filters == {"fmge_bank_id": self.section_data["bank_id"]}
			else 1
			if doctype == "LMS Course"
			else None
		)

	def _get_doc(self, doctype, name):
		return self.quiz if doctype == "LMS Quiz" else self.questions[name]

	def test_guest_payload_has_all_questions_without_keys_or_explanations(self):
		payload = inspect.unwrap(getattr(self.endpoint, f"get_public_day{self.course.day}_quiz"))(
			section=self.section
		)
		self.assertEqual(payload["quiz"]["name"], self.section_data["quiz_name"])
		self.assertEqual(len(payload["questions_by_name"]), self.question_count)
		for question in payload["questions_by_name"].values():
			self.assertFalse(any("correct" in key or "explanation" in key for key in question))

	def test_grading_uses_day1_keys_and_day1_source_links(self):
		answers = [
			{"question_name": name, "answer": [public_quiz._correct_answer(question)]}
			for name, question in self.questions.items()
		]
		result = inspect.unwrap(getattr(self.endpoint, f"submit_public_day{self.course.day}_quiz"))(
			json.dumps(answers), section=self.section
		)
		self.assertEqual(result["score"], self.question_count)
		self.assertEqual(result["percentage"], 100)
		self.assertEqual(len(result["review"]), self.question_count)
		for review in result["review"]:
			self.assertEqual(review["source_document"], f"Day {self.course.day} PSM notes")
			self.assertTrue(review["source_url"].startswith(self.course.source_pdf_url + "#page="))

	def test_unanswered_attempt_scores_zero(self):
		result = inspect.unwrap(getattr(self.endpoint, f"submit_public_day{self.course.day}_quiz"))(
			"[]", section=self.section
		)
		self.assertEqual(result["score"], 0)
		self.assertEqual(result["score_out_of"], self.question_count)

	def test_unpublished_course_is_unavailable(self):
		self.db.get_value.side_effect = lambda doctype, *args: (
			self.section_data["quiz_name"] if doctype == "LMS Quiz" else 0
		)
		with self.assertRaises(frappe.ValidationError):
			inspect.unwrap(getattr(self.endpoint, f"get_public_day{self.course.day}_quiz"))(
				section=self.section
			)

	def test_other_bank_question_is_rejected(self):
		self.questions[self.rows[0].question].fmge_bank_id = "fmge-psm-block-1"
		with self.assertRaises(frappe.ValidationError):
			inspect.unwrap(getattr(self.endpoint, f"get_public_day{self.course.day}_quiz"))(
				section=self.section
			)

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
				submit(payload, section=self.section)

	def test_practice_feedback_uses_correct_pdf(self):
		name = self.rows[0].question
		result = inspect.unwrap(getattr(self.endpoint, f"check_public_day{self.course.day}_answer"))(
			name, self.questions[name].option_1, section=self.section
		)
		self.assertTrue(result["source_url"].startswith(self.course.source_pdf_url))
		with self.assertRaises(frappe.ValidationError):
			inspect.unwrap(getattr(self.endpoint, f"check_public_day{self.course.day}_answer"))(
				"PSM-B1-Q001", "A", section=self.section
			)

	def test_invalid_section_is_rejected_by_every_endpoint(self):
		get = inspect.unwrap(getattr(self.endpoint, f"get_public_day{self.course.day}_quiz"))
		submit = inspect.unwrap(getattr(self.endpoint, f"submit_public_day{self.course.day}_quiz"))
		check = inspect.unwrap(getattr(self.endpoint, f"check_public_day{self.course.day}_answer"))
		for invalid in (0, self.course.section_count + 1, -1, "another-bank", "1.0", None, True):
			for operation in (
				lambda: get(section=invalid),
				lambda: submit("[]", section=invalid),
				lambda: check("anything", "A", section=invalid),
			):
				with self.subTest(section=invalid), self.assertRaises(frappe.ValidationError):
					operation()

	def test_answers_from_the_other_section_are_rejected(self):
		other = self.course.section(2 if self.section == 1 else 1)
		foreign = _load_bank(other["bank_file"])["questions"][0]["id"]
		submit = inspect.unwrap(getattr(self.endpoint, f"submit_public_day{self.course.day}_quiz"))
		with self.assertRaises(frappe.ValidationError):
			submit(json.dumps([{"question_name": foreign, "answer": []}]), section=self.section)


class TestDay1Section2Mock(TestDay1Mock):
	section = 2


class TestDay4Mock(TestDay1Mock):
	course = DAY4_COURSE
	endpoint = day4_mock


class TestDay4Section2Mock(TestDay4Mock):
	section = 2


class TestPSMSections(unittest.TestCase):
	def setUp(self):
		self.course = course.PSMCourse(day=1)
		self.stack = ExitStack()
		self.addCleanup(self.stack.close)
		self.stack.enter_context(patch.object(course, "_", side_effect=lambda text: text))
		self.stack.enter_context(patch.object(frappe, "throw", side_effect=frappe.ValidationError))
		self.banks = {}
		for number in (1, 2):
			section = self.course.section(number)
			self.banks[section["bank_file"]] = {
				"bank_id": section["bank_id"],
				"title": section["quiz_title"],
				"expected_questions": 1,
				"duration_minutes": 1,
				"questions": [{"id": f"PSM-D1-Q{number:03}"}],
			}
		self.stack.enter_context(patch.object(course, "_load_bank", side_effect=self.banks.__getitem__))

	def test_counts_and_links_follow_banks(self):
		self.assertEqual(self.course.question_count, 1)
		self.assertEqual(self.course.total_question_count, 2)
		self.assertIn("?section=2", self.course.description)
		self.assertEqual(len(self.course._source_sections()), 2)

	def test_overlapping_questions_are_rejected(self):
		self.banks["psm_day1_section_2.json"]["questions"][0]["id"] = "PSM-D1-Q001"
		with self.assertRaises(frappe.ValidationError):
			self.course._source_sections()

	def test_oversized_section_is_rejected(self):
		bank = self.banks["psm_day1.json"]
		bank.update(expected_questions=51, duration_minutes=51)
		bank["questions"] = [{"id": f"PSM-D1-Q{n:03}"} for n in range(51)]
		with self.assertRaises(frappe.ValidationError):
			self.course._source_sections()

	def test_append_second_lesson_once_preserving_first(self):
		chapter = frappe._dict(
			name="chapter", course=self.course.course_name, lessons=[frappe._dict(lesson="first")]
		)
		chapter.append = Mock(side_effect=lambda field, row: chapter.lessons.append(frappe._dict(row)))
		chapter.save = Mock()
		section = self.course.section(2)
		quiz = frappe._dict(name=section["quiz_name"], lesson=None, course=None)
		lesson = frappe._dict(name="second", course=chapter.course, insert=Mock())
		self.stack.enter_context(patch.object(frappe, "new_doc", return_value=lesson))
		self.stack.enter_context(patch.object(frappe, "get_doc", return_value=lesson))
		self.course._lesson(quiz, chapter, section)
		quiz.lesson = lesson.name
		quiz.course = chapter.course
		self.assertIs(self.course._lesson(quiz, chapter, section), lesson)
		self.assertEqual([row.lesson for row in chapter.lessons], ["first", "second"])
		lesson.insert.assert_called_once()
		chapter.append.assert_called_once()

	def test_second_lesson_cannot_replace_an_unexpected_layout(self):
		chapter = frappe._dict(name="chapter", course=self.course.course_name, lessons=[])
		section = self.course.section(2)
		quiz = frappe._dict(name=section["quiz_name"], lesson=None, course=None)
		with self.assertRaises(frappe.ValidationError):
			self.course._lesson(quiz, chapter, section)
