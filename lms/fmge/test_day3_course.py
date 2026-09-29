"""Small installer regressions that do not touch a real LMS site."""

import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from lms.fmge.day3_course import QUIZ_NAME, _pool_quiz


class TestDay3PoolQuiz(unittest.TestCase):
	def test_new_pool_keeps_stable_name_when_display_title_changes(self):
		quiz = Mock()
		quiz.name = None
		quiz.is_new.return_value = True
		quiz.questions = []
		quiz.insert.side_effect = lambda **kwargs: setattr(quiz, "name", kwargs["set_name"])
		section = SimpleNamespace(
			questions=[
				SimpleNamespace(question="question-1", question_detail="<p>Question</p>")
			]
		)
		with (
			patch("lms.fmge.day3_course.frappe.db", new=SimpleNamespace(get_value=lambda *args: None)),
			patch("lms.fmge.day3_course.frappe.new_doc", return_value=quiz),
			patch("lms.fmge.day3_course.frappe.get_doc", return_value=section),
		):
			self.assertIs(_pool_quiz([{"quiz": "section"}]), quiz)
		quiz.insert.assert_called_once_with(ignore_permissions=True, set_name=QUIZ_NAME)


if __name__ == "__main__":
	unittest.main()
