import json
from unittest.mock import patch

import frappe

from lms.fmge.importer import install_psm_block_1
from lms.fmge.public_quiz import check_public_answer, get_public_quiz, submit_public_quiz
from lms.lms.doctype.lms_question.lms_question import QUESTION_CORRECTNESS_FIELDS
from lms.lms.test_helpers import BaseTestUtils
from lms.lms.utils import get_editorjs_blocks, get_lms_route, get_quiz_with_questions


class TestFMGEMockInstaller(BaseTestUtils):
	def test_native_course_placement_is_safe_and_reusable(self):
		suffix = frappe.generate_hash(length=8)
		bank = {
			"bank_id": f"fmge-test-{suffix}",
			"title": f"FMGE Test Mock {suffix}",
			"expected_questions": 1,
			"duration_minutes": 1,
			"questions": [
				{
					"id": f"fmge-test-question-{suffix}",
					"stem": "Which option is correct?",
					"options": ["First", "Second", "Third", "Fourth"],
					"correct_option": "A",
					"tier": 1,
					"difficulty": "direct",
					"source": "pp.15, 18 | E2 | Table.",
					"explanation": "First is keyed in the notes.",
				}
			],
		}
		unrelated = frappe.get_doc(
			{"doctype": "LMS Quiz", "title": bank["title"], "passing_percentage": 100}
		).insert()
		self.cleanup_items.append(("LMS Quiz", unrelated.name))

		with patch("lms.fmge.importer._load_bank", return_value=bank):
			first = install_psm_block_1()
			second = install_psm_block_1()

		question = frappe.db.get_value(
			"LMS Question", {"fmge_question_id": bank["questions"][0]["id"]}, "name"
		)
		self.cleanup_items.extend(
			[
				("LMS Question", question),
				("LMS Quiz", first["quiz"]),
				("LMS Course", first["course"]),
				("Course Chapter", frappe.db.get_value("Course Lesson", first["lesson"], "chapter")),
				("Course Lesson", first["lesson"]),
			]
		)

		self.assertNotEqual(first["quiz"], unrelated.name)
		self.assertEqual(frappe.db.get_value("LMS Quiz", unrelated.name, "fmge_bank_id"), None)
		self.assertEqual(first["quiz"], second["quiz"])
		self.assertEqual(first["course"], second["course"])
		self.assertEqual(first["lesson"], second["lesson"])
		self.assertEqual(frappe.db.count("LMS Question", {"fmge_bank_id": bank["bank_id"]}), 1)
		self.assertEqual(frappe.db.get_value("LMS Course", first["course"], "published"), 1)
		self.assertIn(
			get_lms_route("fmge/mock"),
			frappe.db.get_value("LMS Course", first["course"], "description"),
		)

		lesson = frappe.get_doc("Course Lesson", first["lesson"])
		self.assertEqual(get_editorjs_blocks(lesson.content)[0]["data"]["quiz"], first["quiz"])
		self.assertEqual(frappe.db.get_value("LMS Quiz", first["quiz"], "lesson"), lesson.name)

		student = self._create_user(f"fmge-student-{suffix}@example.com", "FMGE", "Student", ["LMS Student"])
		frappe.session.user = student.name
		try:
			with self.assertRaises(frappe.PermissionError):
				get_quiz_with_questions(first["quiz"])
		finally:
			frappe.session.user = "Administrator"

		prior_submissions = frappe.db.count("LMS Quiz Submission")
		with patch("lms.fmge.public_quiz.PUBLIC_BANK_ID", bank["bank_id"]):
			frappe.session.user = "Guest"
			try:
				public = get_public_quiz()
				self.assertEqual(len(public["questions_by_name"]), 1)
				public_question = next(iter(public["questions_by_name"].values()))
				for field in QUESTION_CORRECTNESS_FIELDS:
					self.assertNotIn(field, public_question)
				self.assertNotIn("fmge_explanation", public_question)
				self.assertEqual(public_question["fmge_tier"], 1)
				result = submit_public_quiz(json.dumps([{"question_name": question, "answer": ["First"]}]))
				self.assertEqual(result["score"], 1)
				self.assertEqual(result["review"][0]["correct_answer"], "First")
				self.assertEqual(result["review"][0]["source_pages"], "15, 18")
				self.assertEqual(result["review"][0]["tier"], 1)
				self.assertEqual(result["review"][0]["source_detail"], "Table")
				self.assertTrue(result["review"][0]["source_url"].endswith("#page=15"))

				feedback = check_public_answer(question, "Second")
				self.assertFalse(feedback["is_correct"])
				self.assertEqual(feedback["correct_answer"], "First")
				self.assertEqual(feedback["explanation"], "First is keyed in the notes.")
				self.assertTrue(check_public_answer(question, "First")["is_correct"])
				with self.assertRaises(frappe.ValidationError):
					check_public_answer(question, "Not an option")
				with self.assertRaises(frappe.ValidationError):
					check_public_answer("another-quiz", "First")
				with self.assertRaises(frappe.ValidationError):
					submit_public_quiz(json.dumps([{"question_name": "another-quiz", "answer": ["First"]}]))
			finally:
				frappe.session.user = "Administrator"
		self.assertEqual(frappe.db.count("LMS Quiz Submission"), prior_submissions)

		self._create_enrollment(student.name, first["course"])
		frappe.session.user = student.name
		try:
			questions = get_quiz_with_questions(first["quiz"])["questions_by_name"]
			self.assertEqual(len(questions), 1)
			question = next(iter(questions.values()))
			self.assertNotIn("fmge_explanation", question)
			for field in QUESTION_CORRECTNESS_FIELDS:
				self.assertNotIn(field, question)
		finally:
			frappe.session.user = "Administrator"
