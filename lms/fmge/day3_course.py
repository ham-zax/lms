"""Install the Day 3 pool as one compact mock course lesson."""

from __future__ import annotations

import json

import frappe
from frappe import _

from lms.fmge.importer import _load_bank, import_bank
from lms.lms.utils import get_editorjs_blocks, get_lms_route

COURSE_NAME = "fmge-psm-day-3"
COURSE_TITLE = "FMGE PSM Day 3"
CHAPTER_TITLE = "Day 3 PSM Practice"
QUIZ_TITLE = "FMGE PSM Day 3 Mock"
QUIZ_NAME = "fmge-psm-day-3-compact-mock"
QUIZ_BANK_ID = "fmge-psm-day3-compact"
SOURCE_PDF_URL = "/assets/lms/fmge/day3-psm-notes.pdf"
MOCK_URL = "/lms/fmge/day3/mock"
BANK_FILES = tuple(f"psm_day3_section_{section}.json" for section in range(1, 5))
SHORT_INTRODUCTION = "A fresh 54-question PSM mock from 106 reviewed questions."
COURSE_DESCRIPTION = (
	f'<p><a href="{MOCK_URL}">Take the mock without signing in</a></p>'
	"<p>Each new mock draws 27 Tier 1, 21 Tier 2, and 6 Tier 3 questions "
	"from the 106-question Day 3 pool. Practice or take a timed mock; "
	"each result includes explanations and source pages.</p>"
	f'<p><a href="{SOURCE_PDF_URL}">Open the Day 3 PSM reference PDF</a></p>'
)


def _course(owner):
	if frappe.db.exists("LMS Course", COURSE_NAME):
		course = frappe.get_doc("LMS Course", COURSE_NAME)
		if course.title != COURSE_TITLE:
			frappe.throw(_("The Day 3 course name belongs to another course."), frappe.ValidationError)
		if course.short_introduction != SHORT_INTRODUCTION or course.description != COURSE_DESCRIPTION:
			course.short_introduction = SHORT_INTRODUCTION
			course.description = COURSE_DESCRIPTION
			course.save(ignore_permissions=True)
		return course
	course = frappe.new_doc("LMS Course")
	course.title = COURSE_TITLE
	course.short_introduction = SHORT_INTRODUCTION
	course.description = COURSE_DESCRIPTION
	course.append("instructors", {"instructor": owner})
	course.insert(ignore_permissions=True, set_name=COURSE_NAME)
	if course.name != COURSE_NAME:
		frappe.throw(_("The Day 3 course received an unexpected name."), frappe.ValidationError)
	return course


def _chapter(course):
	linked = [row.chapter for row in course.chapters]
	matching = frappe.get_all(
		"Course Chapter", filters={"course": course.name, "title": CHAPTER_TITLE}, pluck="name"
	)
	if len(matching) > 1:
		frappe.throw(_("The Day 3 course has duplicate PSM chapters."), frappe.ValidationError)
	if matching:
		if matching[0] not in linked:
			frappe.throw(_("The Day 3 chapter is not linked to its course."), frappe.ValidationError)
		return frappe.get_doc("Course Chapter", matching[0])
	if linked:
		frappe.throw(_("The Day 3 course already has a different chapter."), frappe.ValidationError)
	chapter = frappe.new_doc("Course Chapter")
	chapter.title = CHAPTER_TITLE
	chapter.course = course.name
	chapter.insert(ignore_permissions=True)
	course.reload()
	course.append("chapters", {"chapter": chapter.name})
	course.save(ignore_permissions=True)
	return chapter


def _pool_quiz(sections):
	name = frappe.db.get_value("LMS Quiz", {"fmge_bank_id": QUIZ_BANK_ID}, "name")
	quiz = frappe.get_doc("LMS Quiz", name) if name else frappe.new_doc("LMS Quiz")
	if name and name != QUIZ_NAME:
		frappe.throw(_("The Day 3 compact quiz has an unexpected name."), frappe.ValidationError)
	quiz.title = QUIZ_TITLE
	quiz.fmge_bank_id = QUIZ_BANK_ID
	quiz.max_attempts = 0
	quiz.show_answers = 0
	quiz.show_submission_history = 0
	quiz.passing_percentage = 50
	quiz.duration = "54"
	quiz.shuffle_questions = 0
	quiz.limit_questions_to = 0
	quiz.enable_negative_marking = 0
	quiz.marks_to_cut = 0
	quiz.enable_proctoring = 0
	quiz.set("questions", [])
	for section in sections:
		for row in frappe.get_doc("LMS Quiz", section["quiz"]).questions:
			quiz.append(
				"questions",
				{
					"question": row.question,
					"question_detail": row.question_detail,
					"type": "Choices",
					"marks": 1,
				},
			)
	if quiz.is_new():
		quiz.insert(ignore_permissions=True, set_name=QUIZ_NAME)
	else:
		quiz.save(ignore_permissions=True)
	if quiz.name != QUIZ_NAME:
		frappe.throw(_("The Day 3 compact quiz received an unexpected name."), frappe.ValidationError)
	return quiz


def _lesson(quiz, chapter):
	linked = [row.lesson for row in chapter.lessons]
	if quiz.lesson:
		lesson = frappe.get_doc("Course Lesson", quiz.lesson)
		if lesson.course != chapter.course or lesson.chapter != chapter.name or lesson.name not in linked:
			frappe.throw(_("The Day 3 mock is linked outside its course."), frappe.ValidationError)
		if lesson.title != QUIZ_TITLE:
			lesson.title = QUIZ_TITLE
			lesson.save(ignore_permissions=True)
		return lesson
	if linked or quiz.course:
		frappe.throw(_("The Day 3 course already has a different lesson."), frappe.ValidationError)
	lesson = frappe.new_doc("Course Lesson")
	lesson.title = QUIZ_TITLE
	lesson.chapter = chapter.name
	lesson.content = json.dumps(
		{
			"blocks": [{"id": "fmgeday3mock", "type": "quiz", "data": {"quiz": quiz.name}}],
			"version": "2.29.0",
		}
	)
	lesson.insert(ignore_permissions=True)
	chapter.append("lessons", {"lesson": lesson.name})
	chapter.save(ignore_permissions=True)
	return lesson


def _replace_previous_section_lessons(chapter, sections):
	"""Replace the earlier four-section layout only when it has no learner work."""
	if not chapter.lessons:
		return
	if len(chapter.lessons) == 1:
		return
	if len(chapter.lessons) != len(sections):
		frappe.throw(_("The Day 3 course has an unexpected lesson layout."), frappe.ValidationError)
	if frappe.db.count("LMS Enrollment", {"course": chapter.course}):
		frappe.throw(
			_("The Day 3 course has enrollments; review its lessons before replacing them."),
			frappe.ValidationError,
		)
	lesson_names = []
	for row, section in zip(chapter.lessons, sections, strict=True):
		lesson = frappe.get_doc("Course Lesson", row.lesson)
		quiz = frappe.get_doc("LMS Quiz", section["quiz"])
		blocks = get_editorjs_blocks(lesson.content)
		if (
			lesson.course != chapter.course
			or lesson.chapter != chapter.name
			or lesson.title != section["title"]
			or lesson.body
			or lesson.instructor_content
			or quiz.lesson != lesson.name
			or quiz.course != chapter.course
			or len(blocks) != 1
			or blocks[0].get("type") != "quiz"
			or (blocks[0].get("data") or {}).get("quiz") != quiz.name
			or frappe.db.count("LMS Quiz Submission", {"quiz": quiz.name})
		):
			frappe.throw(
				_("The previous Day 3 lessons contain work or unexpected content."), frappe.ValidationError
			)
		lesson_names.append(lesson.name)
	chapter.set("lessons", [])
	chapter.save(ignore_permissions=True)
	for lesson_name, section in zip(lesson_names, sections, strict=True):
		frappe.delete_doc("Course Lesson", lesson_name, ignore_permissions=True)
		frappe.db.set_value("LMS Quiz", section["quiz"], {"course": None, "lesson": None})
	chapter.reload()


def install_day3_psm_course():
	"""Import all 106 questions and publish one dynamic 54-question mock lesson."""
	sections = [import_bank(filename) for filename in BANK_FILES]
	quiz = _pool_quiz(sections)
	course = _course(quiz.owner)
	chapter = _chapter(course)
	_replace_previous_section_lessons(chapter, sections)
	lesson = _lesson(quiz, chapter)
	if not course.published:
		course.reload()
		course.published = 1
		course.save(ignore_permissions=True)
	return {
		"course": course.name,
		"course_url": get_lms_route(f"courses/{course.name}"),
		"mock_url": get_lms_route("fmge/day3/mock"),
		"lesson": lesson.name,
		"pool_questions": len(quiz.questions),
		"mock_questions": 54,
	}


def verify_day3_psm_course():
	"""Check placement and all source question IDs."""
	course = frappe.get_doc("LMS Course", COURSE_NAME)
	if not course.published or course.title != COURSE_TITLE or len(course.chapters) != 1:
		frappe.throw(_("The Day 3 course is not published with one chapter."), frappe.ValidationError)
	if MOCK_URL not in (course.description or ""):
		frappe.throw(_("The Day 3 course is missing its public mock link."), frappe.ValidationError)
	chapter = frappe.get_doc("Course Chapter", course.chapters[0].chapter)
	if chapter.course != course.name or len(chapter.lessons) != 1:
		frappe.throw(_("The Day 3 course must contain one mock lesson."), frappe.ValidationError)
	lesson = frappe.get_doc("Course Lesson", chapter.lessons[0].lesson)
	quiz = frappe.get_doc("LMS Quiz", QUIZ_NAME)
	if (
		quiz.course != course.name
		or quiz.lesson != lesson.name
		or quiz.title != QUIZ_TITLE
		or lesson.title != QUIZ_TITLE
		or not any(
			block.get("type") == "quiz" and (block.get("data") or {}).get("quiz") == quiz.name
			for block in get_editorjs_blocks(lesson.content)
		)
	):
		frappe.throw(_("The Day 3 mock is not linked correctly."), frappe.ValidationError)
	expected = [item["id"] for filename in BANK_FILES for item in _load_bank(filename)["questions"]]
	actual = [frappe.db.get_value("LMS Question", row.question, "fmge_question_id") for row in quiz.questions]
	if actual != expected or len(actual) != 106 or len(set(actual)) != 106:
		frappe.throw(_("The Day 3 pool does not match its source banks."), frappe.ValidationError)
	return {
		"course": course.name,
		"course_url": get_lms_route(f"courses/{course.name}"),
		"mock_url": get_lms_route("fmge/day3/mock"),
		"published": bool(course.published),
		"lessons": 1,
		"pool_questions": len(actual),
		"mock_questions": 54,
	}
