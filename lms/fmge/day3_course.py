"""Install and verify the reviewed Day 3 PSM course as four fixed sections."""

import frappe
from frappe import _

from lms.fmge.course import PSMCourse
from lms.lms.utils import get_editorjs_blocks

# The retired random-draw mock; its lesson is replaced by the section lessons.
COMPACT_QUIZ_NAME = "fmge-psm-day-3-compact-mock"


class Day3Course(PSMCourse):
	def __init__(self):
		super().__init__(day=3, section_count=4)

	def _section_spec(self, number):
		return {
			"number": number,
			"bank_id": f"{self.bank_id}-section-{number}",
			"bank_file": f"psm_day3_section_{number}.json",
			"quiz_name": f"day-3-psm-section-{number}",
			"quiz_title": f"Day 3 PSM — Section {number}",
			"mock_url": self.mock_url if number == 1 else f"{self.mock_url}?section={number}",
		}

	def _prepare_chapter(self, chapter, sections):
		"""Remove the retired random-mock lesson when it holds no learner work."""
		if len(chapter.lessons) != 1:
			return
		lesson = frappe.get_doc("Course Lesson", chapter.lessons[0].lesson)
		blocks = get_editorjs_blocks(lesson.content)
		if len(blocks) != 1 or (blocks[0].get("data") or {}).get("quiz") != COMPACT_QUIZ_NAME:
			return
		if frappe.db.count("LMS Enrollment", {"course": chapter.course}) or frappe.db.count(
			"LMS Quiz Submission", {"quiz": COMPACT_QUIZ_NAME}
		):
			frappe.throw(
				_("The Day 3 mock has learner work; review it before replacing the lesson."),
				frappe.ValidationError,
			)
		if lesson.body or lesson.instructor_content or lesson.chapter != chapter.name:
			frappe.throw(_("The Day 3 mock lesson has unexpected content."), frappe.ValidationError)
		chapter.set("lessons", [])
		chapter.save(ignore_permissions=True)
		frappe.db.set_value("LMS Quiz", COMPACT_QUIZ_NAME, {"course": None, "lesson": None})
		frappe.delete_doc("Course Lesson", lesson.name, ignore_permissions=True)
		chapter.reload()


COURSE = Day3Course()
COURSE_NAME = COURSE.course_name
BANK_FILES = tuple(COURSE.section(n)["bank_file"] for n in COURSE.section_numbers)
SOURCE_PDF_URL = COURSE.source_pdf_url
MOCK_URL = COURSE.mock_url


def install_day3_psm_course():
	return COURSE.install()


def verify_day3_psm_course():
	return COURSE.verify()
