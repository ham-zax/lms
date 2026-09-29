"""Import curated FMGE question-bank data into native Frappe Learning quiz doctypes."""

from __future__ import annotations

import html
import json
from pathlib import Path

import frappe
from frappe import _

from lms.lms.doctype.lms_question.lms_question import (
	QUESTION_CORRECTNESS_FIELDS,
	QUESTION_EXPLANATION_FIELDS,
	QUESTION_OPTION_FIELDS,
)
from lms.lms.utils import get_editorjs_blocks, get_lms_route

DATA_DIR = Path(__file__).with_name("data")
FMGE_OPTION_COUNT = 4
DAY2_BANK_ID = "fmge-psm-block-1"
DAY2_COURSE_NAME = "fmge-mock-exams"
DAY2_COURSE_TITLE = "FMGE PSM Day 2"
DAY2_CHAPTER_TITLE = "Day 2 PSM Practice"
DAY2_SHORT_INTRODUCTION = "A 50-question Community Medicine mock from the Day 2 PSM notes."


def _load_bank(filename: str) -> dict:
	path = DATA_DIR / filename
	if not path.is_file():
		raise FileNotFoundError(path)
	return json.loads(path.read_text(encoding="utf-8"))


def _question_html(item: dict) -> str:
	stem = f"<p>{html.escape(item['stem'])}</p>"
	image_url = (item.get("image_url") or "").strip()
	if not image_url:
		return stem

	if not image_url.startswith(("/files/", "/assets/")):
		frappe.throw(
			_("Question {0} has an unsupported image URL.").format(item.get("id")),
			frappe.ValidationError,
		)

	alt = html.escape(item.get("image_alt") or "Question image")
	return f'{stem}<p><img src="{html.escape(image_url, quote=True)}" alt="{alt}"></p>'


def _validate_bank(bank: dict) -> None:
	if not bank.get("bank_id") or not bank.get("title"):
		frappe.throw(_("FMGE bank_id and title are required."), frappe.ValidationError)

	questions = bank.get("questions") or []
	expected = int(bank.get("expected_questions") or 0)
	if expected and len(questions) != expected:
		frappe.throw(
			_("FMGE bank {0} expected {1} questions but contains {2}.").format(
				bank.get("bank_id"), expected, len(questions)
			),
			frappe.ValidationError,
		)

	seen_ids: set[str] = set()
	for item in questions:
		question_id = item.get("id")
		if not question_id or question_id in seen_ids:
			frappe.throw(_("FMGE question IDs must be present and unique."), frappe.ValidationError)
		seen_ids.add(question_id)

		options = item.get("options") or []
		if len(options) != FMGE_OPTION_COUNT or any(not option for option in options):
			frappe.throw(
				_("Question {0} must have exactly four non-empty options.").format(question_id),
				frappe.ValidationError,
			)
		if item.get("correct_option") not in {"A", "B", "C", "D"}:
			frappe.throw(
				_("Question {0} must have one correct option A-D.").format(question_id),
				frappe.ValidationError,
			)
		if item.get("tier") not in {1, 2, 3}:
			frappe.throw(
				_("Question {0} must have FMGE tier 1, 2, or 3.").format(question_id),
				frappe.ValidationError,
			)
		if item.get("difficulty") not in {"direct", "moderate", "hard"}:
			frappe.throw(
				_("Question {0} has an invalid FMGE difficulty.").format(question_id),
				frappe.ValidationError,
			)


def _assert_legacy_question_matches(question, item: dict) -> None:
	if question.type != "Choices":
		frappe.throw(
			_("Existing LMS Question {0} has the same stem but a different type.").format(question.name),
			frappe.ValidationError,
		)

	correct_index = ord(item["correct_option"]) - ord("A")
	for index in range(FMGE_OPTION_COUNT):
		if (question.get(QUESTION_OPTION_FIELDS[index]) or "") != item["options"][index]:
			frappe.throw(
				_("Existing LMS Question {0} has the same stem but different options.").format(question.name),
				frappe.ValidationError,
			)
		expected = 1 if index == correct_index else 0
		if int(question.get(QUESTION_CORRECTNESS_FIELDS[index]) or 0) != expected:
			frappe.throw(
				_("Existing LMS Question {0} has the same stem but a different answer key.").format(
					question.name
				),
				frappe.ValidationError,
			)


def _find_question(item: dict, legacy_quiz_name: str | None = None):
	existing_name = frappe.db.get_value("LMS Question", {"fmge_question_id": item["id"]}, "name")
	if existing_name:
		return frappe.get_doc("LMS Question", existing_name)

	stem = _question_html(item)
	legacy_name = frappe.db.get_value("LMS Question", {"question": stem}, "name")
	if legacy_name and legacy_quiz_name:
		belongs_to_legacy_quiz = frappe.db.exists(
			"LMS Quiz Question",
			{"parent": legacy_quiz_name, "question": legacy_name},
		)
		if belongs_to_legacy_quiz:
			legacy = frappe.get_doc("LMS Question", legacy_name)
			if not legacy.get("fmge_question_id"):
				_assert_legacy_question_matches(legacy, item)
				return legacy

	return frappe.new_doc("LMS Question")


def _sync_question(bank: dict, item: dict, legacy_quiz_name: str | None = None) -> str:
	question = _find_question(item, legacy_quiz_name)
	is_new = question.is_new()
	correct_index = ord(item["correct_option"]) - ord("A")

	question.question = _question_html(item)
	question.type = "Choices"
	question.marks = 1
	question.fmge_question_id = item["id"]
	question.fmge_bank_id = bank["bank_id"]
	question.fmge_tier = item["tier"]
	question.fmge_difficulty = item["difficulty"]
	question.fmge_source = item.get("source") or ""
	question.fmge_explanation = item.get("explanation") or ""

	for index, field in enumerate(QUESTION_OPTION_FIELDS):
		question.set(field, item["options"][index] if index < FMGE_OPTION_COUNT else None)
	for index, field in enumerate(QUESTION_CORRECTNESS_FIELDS):
		question.set(field, 1 if index == correct_index else 0)
	for field in QUESTION_EXPLANATION_FIELDS:
		question.set(field, None)

	if is_new:
		question.insert(ignore_permissions=True)
	else:
		question.save(ignore_permissions=True)
	return question.name


def _find_quiz(bank: dict):
	existing_name = frappe.db.get_value("LMS Quiz", {"fmge_bank_id": bank["bank_id"]}, "name")
	if existing_name:
		return frappe.get_doc("LMS Quiz", existing_name)
	return frappe.new_doc("LMS Quiz")


def import_bank(filename: str) -> dict:
	"""Reconcile one curated FMGE bank into native LMS Question/LMS Quiz records."""
	bank = _load_bank(filename)
	_validate_bank(bank)

	quiz = _find_quiz(bank)
	created = quiz.is_new()
	legacy_quiz_name = None if created else quiz.name
	question_names = [_sync_question(bank, item, legacy_quiz_name) for item in bank["questions"]]

	quiz.title = bank["title"]
	quiz.fmge_bank_id = bank["bank_id"]
	quiz.max_attempts = int(bank.get("max_attempts", 1))
	quiz.show_answers = int(bank.get("show_answers", 0))
	quiz.show_submission_history = int(bank.get("show_submission_history", 1))
	quiz.passing_percentage = int(bank.get("passing_percentage", 50))
	quiz.duration = str(int(bank.get("duration_minutes", 50)))
	quiz.shuffle_questions = int(bank.get("shuffle_questions", 0))
	quiz.limit_questions_to = 0
	quiz.enable_negative_marking = int(bank.get("enable_negative_marking", 0))
	quiz.marks_to_cut = 0
	quiz.enable_proctoring = 0
	quiz.set("questions", [])

	for item, question_name in zip(bank["questions"], question_names, strict=True):
		quiz.append(
			"questions",
			{
				"question": question_name,
				"question_detail": _question_html(item),
				"type": "Choices",
				"marks": 1,
			},
		)

	if created:
		quiz.insert(ignore_permissions=True)
	else:
		quiz.save(ignore_permissions=True)

	return {
		"quiz": quiz.name,
		"title": quiz.title,
		"created": created,
		"reconciled": not created,
		"questions": len(question_names),
		"total_marks": quiz.total_marks,
		"duration_minutes": int(quiz.duration),
		"max_attempts": quiz.max_attempts,
	}


def install_psm_block_1() -> dict:
	"""Install the first FMGE section as a native, enrollable Frappe course lesson."""
	result = import_bank("psm_block_1.json")
	result.update(_place_psm_quiz_in_course(result["quiz"]))
	return result


def _place_psm_quiz_in_course(quiz_name: str) -> dict:
	quiz = frappe.get_doc("LMS Quiz", quiz_name)
	if quiz.lesson:
		lesson = frappe.get_doc("Course Lesson", quiz.lesson)
		quiz_in_content = any(
			block.get("type") == "quiz" and (block.get("data") or {}).get("quiz") == quiz_name
			for block in get_editorjs_blocks(lesson.content)
		)
		if lesson.quiz_id != quiz_name and not quiz_in_content:
			frappe.throw(
				_("FMGE quiz is linked to a lesson that no longer contains it."),
				frappe.ValidationError,
			)
		if quiz.fmge_bank_id == DAY2_BANK_ID:
			if lesson.course != DAY2_COURSE_NAME:
				frappe.throw(_("The Day 2 quiz is linked to an unexpected course."), frappe.ValidationError)
			course = frappe.get_doc("LMS Course", lesson.course)
			course.title = DAY2_COURSE_TITLE
			course.short_introduction = DAY2_SHORT_INTRODUCTION
			course.description = _public_course_description()
			course.save(ignore_permissions=True)
			chapter = frappe.get_doc("Course Chapter", lesson.chapter)
			chapter.title = DAY2_CHAPTER_TITLE
			chapter.save(ignore_permissions=True)
			lesson.title = quiz.title
			lesson.save(ignore_permissions=True)
		return _course_location(lesson.course, lesson.name)

	course = frappe.new_doc("LMS Course")
	course.title = DAY2_COURSE_TITLE
	course.short_introduction = DAY2_SHORT_INTRODUCTION
	course.description = _public_course_description()
	course.append("instructors", {"instructor": quiz.owner})
	if quiz.fmge_bank_id == DAY2_BANK_ID:
		course.insert(ignore_permissions=True, set_name=DAY2_COURSE_NAME)
	else:
		course.insert(ignore_permissions=True)

	chapter = frappe.new_doc("Course Chapter")
	chapter.title = DAY2_CHAPTER_TITLE
	chapter.course = course.name
	chapter.insert(ignore_permissions=True)
	course.reload()
	course.append("chapters", {"chapter": chapter.name})
	course.save(ignore_permissions=True)

	lesson = frappe.new_doc("Course Lesson")
	lesson.title = quiz.title
	lesson.chapter = chapter.name
	lesson.content = json.dumps(
		{
			"blocks": [{"id": "fmgepsmmock1", "type": "quiz", "data": {"quiz": quiz.name}}],
			"version": "2.29.0",
		}
	)
	lesson.insert(ignore_permissions=True)
	chapter.append("lessons", {"lesson": lesson.name})
	chapter.save(ignore_permissions=True)

	course.reload()
	course.published = 1
	course.save(ignore_permissions=True)
	return _course_location(course.name, lesson.name)


def _public_course_description() -> str:
	return (
		"<p>Practice 50 Community Medicine questions from the Day 2 PSM notes. "
		"Review the answer, explanation, and source page after submission.</p>"
		f'<p><a href="{html.escape(get_lms_route("fmge/mock"), quote=True)}">'
		f"{html.escape(_('Take the mock without signing in'))}</a>.</p>"
	)


def _course_location(course: str, lesson: str) -> dict:
	return {
		"course": course,
		"lesson": lesson,
		"course_url": get_lms_route(f"courses/{course}"),
	}
