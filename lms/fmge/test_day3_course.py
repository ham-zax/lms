"""Day 3 installer regressions that do not touch a real LMS site."""

import json
import unittest
from contextlib import ExitStack
from types import SimpleNamespace
from unittest.mock import Mock, patch

import frappe

from lms.fmge import course, day3_course
from lms.fmge.day3_course import COMPACT_QUIZ_NAME, COURSE


class TestDay3Sections(unittest.TestCase):
	def test_four_fixed_sections(self):
		self.assertEqual(COURSE.section_numbers, (1, 2, 3, 4))
		self.assertEqual(
			[COURSE.section(n)["quiz_name"] for n in COURSE.section_numbers],
			[f"day-3-psm-section-{n}" for n in range(1, 5)],
		)
		self.assertEqual(COURSE.section(3)["mock_url"], f"{COURSE.mock_url}?section=3")
		self.assertEqual(COURSE.total_question_count, 129)


class TestDay3CompactLesson(unittest.TestCase):
	def setUp(self):
		self.stack = ExitStack()
		self.addCleanup(self.stack.close)
		self.stack.enter_context(patch.object(day3_course, "_", side_effect=lambda text: text))
		self.stack.enter_context(patch.object(course, "_", side_effect=lambda text: text))
		self.stack.enter_context(patch.object(frappe, "throw", side_effect=frappe.ValidationError))
		self.chapter = SimpleNamespace(
			name="chapter",
			course=COURSE.course_name,
			lessons=[SimpleNamespace(lesson="compact")],
			set=Mock(),
			save=Mock(),
			reload=Mock(),
		)
		content = json.dumps({"blocks": [{"type": "quiz", "data": {"quiz": COMPACT_QUIZ_NAME}}]})
		self.lesson = SimpleNamespace(
			name="compact", content=content, body=None, instructor_content=None, chapter="chapter"
		)
		self.stack.enter_context(patch.object(frappe, "get_doc", return_value=self.lesson))
		self.db = SimpleNamespace(count=Mock(return_value=0), set_value=Mock())
		self.stack.enter_context(patch.object(frappe, "db", new=self.db))
		self.delete = self.stack.enter_context(patch.object(frappe, "delete_doc"))

	def test_unused_compact_lesson_is_removed(self):
		COURSE._prepare_chapter(self.chapter, [])
		self.chapter.set.assert_called_once_with("lessons", [])
		self.db.set_value.assert_called_once_with(
			"LMS Quiz", COMPACT_QUIZ_NAME, {"course": None, "lesson": None}
		)
		self.delete.assert_called_once_with("Course Lesson", "compact", ignore_permissions=True)

	def test_compact_lesson_with_learner_work_is_kept(self):
		self.db.count.return_value = 1
		with self.assertRaises(frappe.ValidationError):
			COURSE._prepare_chapter(self.chapter, [])
		self.delete.assert_not_called()

	def test_other_layouts_are_left_alone(self):
		self.lesson.content = json.dumps({"blocks": [{"type": "quiz", "data": {"quiz": "other"}}]})
		COURSE._prepare_chapter(self.chapter, [])
		self.chapter.set.assert_not_called()
		self.delete.assert_not_called()


if __name__ == "__main__":
	unittest.main()
