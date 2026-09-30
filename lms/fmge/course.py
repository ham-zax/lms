"""Shared installer for reviewed single-bank PSM courses."""

import json

import frappe
from frappe import _

from lms.fmge.importer import _load_bank, import_bank
from lms.lms.utils import get_editorjs_blocks, get_lms_route


class PSMCourse:
	def __init__(self, day: int, question_count: int):
		self.day = day
		self.question_count = question_count
		self.course_name = f"fmge-psm-day-{day}"
		self.course_title = f"FMGE PSM Day {day}"
		self.chapter_title = f"Day {day} PSM Practice"
		self.quiz_title = f"FMGE PSM Day {day} Mock"
		self.quiz_name = f"fmge-psm-day-{day}-mock"
		self.bank_id = f"fmge-psm-day{day}"
		self.bank_file = f"psm_day{day}.json"
		self.source_pdf_url = f"/assets/lms/fmge/day{day}-psm-notes.pdf"
		self.mock_url = f"/lms/fmge/day{day}/mock"
		self.short_introduction = (
			f"A {question_count}-question Community Medicine mock from the reviewed Day {day} PSM notes."
		)
		self.description = (
			f'<p><a href="{self.mock_url}">Take the mock without signing in</a></p>'
			f"<p>Revise Community Medicine with {question_count} reviewed questions from the Day {day} notes. "
			f"Choose untimed practice with immediate feedback or a {question_count}-minute mock. "
			"Results include teaching explanations and links to the source pages.</p>"
			f'<p><a href="{self.source_pdf_url}">Open the Day {day} PSM reference PDF</a></p>'
		)

	def _course(self, owner):
		if frappe.db.exists("LMS Course", self.course_name):
			course = frappe.get_doc("LMS Course", self.course_name)
			if course.title != self.course_title:
				frappe.throw(
					_("The Day {0} course name belongs to another course.").format(self.day),
					frappe.ValidationError,
				)
			if course.short_introduction != self.short_introduction or course.description != self.description:
				course.short_introduction = self.short_introduction
				course.description = self.description
				course.save(ignore_permissions=True)
			return course
		course = frappe.new_doc("LMS Course")
		course.title = self.course_title
		course.short_introduction = self.short_introduction
		course.description = self.description
		course.append("instructors", {"instructor": owner})
		course.insert(ignore_permissions=True, set_name=self.course_name)
		return course

	def _chapter(self, course):
		linked = [row.chapter for row in course.chapters]
		matching = frappe.get_all(
			"Course Chapter", filters={"course": course.name, "title": self.chapter_title}, pluck="name"
		)
		if matching:
			if len(matching) != 1 or linked != matching:
				frappe.throw(
					_("The Day {0} course has an unexpected chapter layout.").format(self.day),
					frappe.ValidationError,
				)
			return frappe.get_doc("Course Chapter", matching[0])
		if linked:
			frappe.throw(
				_("The Day {0} course already has a different chapter.").format(self.day),
				frappe.ValidationError,
			)
		chapter = frappe.new_doc("Course Chapter")
		chapter.title = self.chapter_title
		chapter.course = course.name
		chapter.insert(ignore_permissions=True)
		course.reload()
		course.append("chapters", {"chapter": chapter.name})
		course.save(ignore_permissions=True)
		return chapter

	def _lesson(self, quiz, chapter):
		linked = [row.lesson for row in chapter.lessons]
		if quiz.lesson:
			lesson = frappe.get_doc("Course Lesson", quiz.lesson)
			if (
				lesson.course != chapter.course
				or lesson.chapter != chapter.name
				or linked != [lesson.name]
				or not any(
					block.get("type") == "quiz" and (block.get("data") or {}).get("quiz") == quiz.name
					for block in get_editorjs_blocks(lesson.content)
				)
			):
				frappe.throw(
					_("The Day {0} quiz is linked to an unexpected lesson.").format(self.day),
					frappe.ValidationError,
				)
			return lesson
		if linked or quiz.course:
			frappe.throw(
				_("The Day {0} course already has a different lesson.").format(self.day),
				frappe.ValidationError,
			)
		lesson = frappe.new_doc("Course Lesson")
		lesson.title = self.quiz_title
		lesson.chapter = chapter.name
		lesson.content = json.dumps(
			{
				"blocks": [{"id": f"fmgeday{self.day}mock", "type": "quiz", "data": {"quiz": quiz.name}}],
				"version": "2.29.0",
			}
		)
		lesson.insert(ignore_permissions=True)
		chapter.append("lessons", {"lesson": lesson.name})
		chapter.save(ignore_permissions=True)
		return lesson

	def install(self):
		"""Reconcile the source bank and create one published course, chapter and lesson."""
		result = import_bank(self.bank_file)
		if result["quiz"] != self.quiz_name:
			frappe.throw(
				_("The Day {0} quiz has an unexpected name.").format(self.day), frappe.ValidationError
			)
		quiz = frappe.get_doc("LMS Quiz", result["quiz"])
		course = self._course(quiz.owner)
		chapter = self._chapter(course)
		self._lesson(quiz, chapter)
		if not course.published:
			course.reload()
			course.published = 1
			course.save(ignore_permissions=True)
		return self.verify()

	def verify(self):
		"""Check course placement, quiz settings and every ordered source question ID."""
		course = frappe.get_doc("LMS Course", self.course_name)
		if not course.published or course.title != self.course_title or len(course.chapters) != 1:
			frappe.throw(
				_("The Day {0} course is not published with one chapter.").format(self.day),
				frappe.ValidationError,
			)
		chapter = frappe.get_doc("Course Chapter", course.chapters[0].chapter)
		if chapter.course != course.name or chapter.title != self.chapter_title or len(chapter.lessons) != 1:
			frappe.throw(
				_("The Day {0} course must contain one mock lesson.").format(self.day), frappe.ValidationError
			)
		lesson = frappe.get_doc("Course Lesson", chapter.lessons[0].lesson)
		quiz = frappe.get_doc("LMS Quiz", self.quiz_name)
		if (
			quiz.course != course.name
			or quiz.lesson != lesson.name
			or quiz.fmge_bank_id != self.bank_id
			or lesson.course != course.name
			or lesson.title != self.quiz_title
			or lesson.chapter != chapter.name
			or quiz.title != self.quiz_title
			or int(quiz.duration) != self.question_count
			or int(quiz.total_marks) != self.question_count
			or quiz.show_answers
			or quiz.enable_negative_marking
			or self.mock_url not in (course.description or "")
			or not any(
				block.get("type") == "quiz" and (block.get("data") or {}).get("quiz") == quiz.name
				for block in get_editorjs_blocks(lesson.content)
			)
		):
			frappe.throw(
				_("The Day {0} mock is not configured or linked correctly.").format(self.day),
				frappe.ValidationError,
			)
		expected = [item["id"] for item in _load_bank(self.bank_file)["questions"]]
		actual = [
			frappe.db.get_value("LMS Question", row.question, "fmge_question_id") for row in quiz.questions
		]
		if (
			actual != expected
			or len(actual) != self.question_count
			or len(set(actual)) != self.question_count
		):
			frappe.throw(
				_("The Day {0} quiz does not match its source bank.").format(self.day), frappe.ValidationError
			)
		return {
			"course": course.name,
			"course_url": get_lms_route(f"courses/{course.name}"),
			"mock_url": get_lms_route(f"fmge/day{self.day}/mock"),
			"published": bool(course.published),
			"lesson": lesson.name,
			"questions": len(actual),
			"duration_minutes": int(quiz.duration),
		}
