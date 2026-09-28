"""Anonymous practice access to the published FMGE mock in Frappe Learning."""

from __future__ import annotations

import json
import re

import frappe
from frappe import _
from frappe.rate_limiter import rate_limit
from frappe.utils import cint

from lms.lms.doctype.lms_question.lms_question import (
	QUESTION_CORRECTNESS_FIELDS,
	QUESTION_OPTION_FIELDS,
)

PUBLIC_BANK_ID = "fmge-psm-block-1"
MAX_RESULTS_BYTES = 20_000
SOURCE_DOCUMENT = "Day 2 PSM notes"
# Served from lms/public/fmge, a link to the notes PDF the bank was written from.
SOURCE_PDF_URL = "/assets/lms/fmge/day2-psm-notes.pdf"
# "p.60", "PDF p.60", "pp.78–79", "pp.15, 18" -> the page list after the prefix.
SOURCE_PAGES_RE = re.compile(r"\bpp?\.\s*(\d+(?:\s*[–,-]\s*\d+)*)")
# Evidence grades (E0, E1, E0-E1) are for the question writer, not the learner.
EVIDENCE_RE = re.compile(r"^(?:Evidence:\s*)?E\d(?:-E\d)?\.?$")


def _published_quiz():
	name = frappe.db.get_value("LMS Quiz", {"fmge_bank_id": PUBLIC_BANK_ID}, "name")
	if not name:
		frappe.throw(_("FMGE mock is not available."), frappe.DoesNotExistError)
	quiz = frappe.get_doc("LMS Quiz", name)
	if not quiz.course or not frappe.db.get_value("LMS Course", quiz.course, "published"):
		frappe.throw(_("FMGE mock is not available."), frappe.DoesNotExistError)
	return quiz


def _question_rows(quiz):
	questions = {}
	for row in quiz.questions:
		question = frappe.get_doc("LMS Question", row.question)
		if question.fmge_bank_id != PUBLIC_BANK_ID or question.type != "Choices":
			frappe.throw(_("FMGE mock question bank is inconsistent."), frappe.ValidationError)
		questions[question.name] = question
	return questions


def _correct_answer(question) -> str:
	correct = [
		question.get(option)
		for option, flag in zip(QUESTION_OPTION_FIELDS, QUESTION_CORRECTNESS_FIELDS, strict=True)
		if cint(question.get(flag))
	]
	if len(correct) != 1:
		frappe.throw(_("FMGE mock question bank is inconsistent."), frappe.ValidationError)
	return correct[0]


def _source_reference(source: str | None) -> dict:
	"""Turn a bank source note into what a learner needs to find it in the notes."""
	source = source or ""
	match = SOURCE_PAGES_RE.search(source)
	pages = re.sub(r"\s*,\s*", ", ", match.group(1)) if match else ""
	first_page = cint(re.match(r"\d+", pages).group()) if pages else 0
	details = [
		part.strip().rstrip(".")
		for part in source.split("|")[1:]
		if part.strip() and not EVIDENCE_RE.match(part.strip())
	]
	return {
		"source_document": SOURCE_DOCUMENT,
		"source_pages": pages,
		"source_detail": ", ".join(details),
		"source_url": f"{SOURCE_PDF_URL}#page={first_page}" if first_page else SOURCE_PDF_URL,
	}


def _feedback(question, chosen: str | None) -> dict:
	correct_answer = _correct_answer(question)
	return {
		"answer": chosen,
		"correct_answer": correct_answer,
		"is_correct": chosen == correct_answer,
		"tier": cint(question.fmge_tier),
		"explanation": question.fmge_explanation or "",
		**_source_reference(question.fmge_source),
	}


def _is_option(question, answer) -> bool:
	return isinstance(answer, str) and answer in [question.get(field) for field in QUESTION_OPTION_FIELDS]


@frappe.whitelist(allow_guest=True, methods=["GET", "POST"])
@rate_limit(limit=60, seconds=60 * 60)
def get_public_quiz() -> dict:
	"""Serve only the published FMGE practice questions, without answer keys."""
	quiz = _published_quiz()
	questions = _question_rows(quiz)
	return {
		"quiz": {
			"name": quiz.name,
			"title": quiz.title,
			"duration": quiz.duration,
			"total_marks": quiz.total_marks,
			"passing_percentage": quiz.passing_percentage,
			"max_attempts": 0,
			"show_answers": 0,
			"show_submission_history": 0,
			"shuffle_questions": quiz.shuffle_questions,
			"limit_questions_to": quiz.limit_questions_to,
			"enable_negative_marking": 0,
			"enable_proctoring": 0,
			"questions": [
				{"name": row.name, "question": row.question, "marks": row.marks, "type": "Choices"}
				for row in quiz.questions
			],
		},
		"questions_by_name": {
			name: {
				"name": name,
				"question": question.question,
				"type": "Choices",
				"multiple": 0,
				"fmge_tier": cint(question.fmge_tier),
				"fmge_difficulty": question.fmge_difficulty,
				**{field: question.get(field) for field in QUESTION_OPTION_FIELDS},
			}
			for name, question in questions.items()
		},
	}


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=20, seconds=60 * 60)
def submit_public_quiz(results: str) -> dict:
	"""Grade one anonymous practice attempt without creating a user or submission."""
	if not isinstance(results, str) or len(results.encode("utf-8")) > MAX_RESULTS_BYTES:
		frappe.throw(_("Invalid FMGE answers."), frappe.ValidationError)
	try:
		answer_rows = json.loads(results)
	except (TypeError, ValueError):
		frappe.throw(_("Invalid FMGE answers."), frappe.ValidationError)
	if not isinstance(answer_rows, list):
		frappe.throw(_("Invalid FMGE answers."), frappe.ValidationError)

	quiz = _published_quiz()
	questions = _question_rows(quiz)
	if len(answer_rows) > len(questions):
		frappe.throw(_("Invalid FMGE answers."), frappe.ValidationError)
	answers = {}
	for row in answer_rows:
		if not isinstance(row, dict) or set(row) != {"question_name", "answer"}:
			frappe.throw(_("Invalid FMGE answers."), frappe.ValidationError)
		name, answer = row["question_name"], row["answer"]
		if name not in questions or name in answers or not isinstance(answer, list) or len(answer) > 1:
			frappe.throw(_("Invalid FMGE answers."), frappe.ValidationError)
		if answer and not _is_option(questions[name], answer[0]):
			frappe.throw(_("Invalid FMGE answers."), frappe.ValidationError)
		answers[name] = answer[0] if answer else None

	score = 0
	review = []
	for row in quiz.questions:
		question = questions[row.question]
		feedback = _feedback(question, answers.get(question.name))
		if feedback["is_correct"]:
			score += cint(row.marks)
		review.append({"question": question.question, **feedback})

	total = cint(quiz.total_marks)
	percentage = round(score * 100 / total, 2) if total else 0
	return {
		"score": score,
		"score_out_of": total,
		"percentage": percentage,
		"pass": percentage >= cint(quiz.passing_percentage),
		"is_open_ended": False,
		"review": review,
	}


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=600, seconds=60 * 60)
def check_public_answer(question: str, answer: str) -> dict:
	"""Practice mode: mark one answer and explain it, citing the page in the notes."""
	questions = _question_rows(_published_quiz())
	if question not in questions or not _is_option(questions[question], answer):
		frappe.throw(_("Invalid FMGE answer."), frappe.ValidationError)
	return _feedback(questions[question], answer)
