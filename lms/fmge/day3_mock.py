"""Anonymous Day 3 mock: fixed tier slots, fresh questions within each tier."""

from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
import json
import secrets
import time

import frappe
from frappe import _
from frappe.rate_limiter import rate_limit
from frappe.utils import cint

from lms.fmge.day3_course import COURSE_NAME, QUIZ_NAME, SOURCE_PDF_URL
from lms.fmge.public_quiz import MAX_RESULTS_BYTES, _feedback, _is_option
from lms.lms.doctype.lms_question.lms_question import QUESTION_OPTION_FIELDS

# Three identical 18-slot blocks give 27 Tier 1, 21 Tier 2, 6 Tier 3.
# Each ninth position is Tier 3; the other tiers follow a stable interleaving.
TIER_PATTERN = (1, 2, 1, 2, 1, 2, 1, 2, 3, 1, 2, 1, 2, 1, 2, 1, 1, 3) * 3
TIER_COUNTS = {1: 27, 2: 21, 3: 6}
POOL_COUNTS = {1: 53, 2: 41, 3: 12}
SOURCE_DOCUMENT = "Day 3 PSM notes"
TOKEN_MAX_AGE = 24 * 60 * 60


def _sign(payload):
	key = ("fmge-day3-mock-v1:" + frappe.conf.encryption_key).encode()
	return hmac.new(key, payload.encode(), hashlib.sha256).hexdigest()


def _token_for(names):
	payload = base64.urlsafe_b64encode(
		json.dumps({"q": names, "iat": int(time.time())}, separators=(",", ":")).encode()
	).decode().rstrip("=")
	return f"{payload}.{_sign(payload)}"


def _pool():
	if not frappe.db.get_value("LMS Course", COURSE_NAME, "published"):
		frappe.throw(_("Day 3 mock is not available."), frappe.DoesNotExistError)
	quiz = frappe.get_doc("LMS Quiz", QUIZ_NAME)
	if quiz.course != COURSE_NAME:
		frappe.throw(_("Day 3 mock is not available."), frappe.DoesNotExistError)
	rows = {}
	by_tier = {tier: [] for tier in TIER_COUNTS}
	for row in quiz.questions:
		question = frappe.get_doc("LMS Question", row.question)
		tier = cint(question.fmge_tier)
		if question.type != "Choices" or tier not in by_tier or question.name in rows:
			frappe.throw(_("Day 3 question pool is inconsistent."), frappe.ValidationError)
		rows[question.name] = (row, question)
		by_tier[tier].append(question.name)
	if {tier: len(names) for tier, names in by_tier.items()} != POOL_COUNTS:
		frappe.throw(_("Day 3 question pool is incomplete."), frappe.ValidationError)
	return quiz, rows, by_tier


def select_questions(by_tier, sampler=secrets.SystemRandom()):
	"""Draw within tiers and place each draw in a fixed tier slot."""
	if {tier: len(by_tier[tier]) for tier in TIER_COUNTS} != POOL_COUNTS:
		raise ValueError("Day 3 question pool is incomplete")
	selected = {
		tier: iter(sampler.sample(by_tier[tier], count))
		for tier, count in TIER_COUNTS.items()
	}
	return [next(selected[tier]) for tier in TIER_PATTERN]


def _selected(token, rows):
	try:
		if not isinstance(token, str) or len(token) > 10000:
			raise ValueError
		payload, signature = token.rsplit(".", 1)
		if not hmac.compare_digest(_sign(payload), signature):
			raise ValueError
		data = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
		issued = data["iat"]
		if not isinstance(issued, int) or not 0 <= time.time() - issued <= TOKEN_MAX_AGE:
			raise ValueError
		names = data["q"]
	except (ValueError, TypeError, KeyError, json.JSONDecodeError, binascii.Error):
		frappe.throw(_("Invalid or expired Day 3 mock."), frappe.ValidationError)
	if (
		not isinstance(names, list)
		or len(names) != len(TIER_PATTERN)
		or len(set(names)) != len(names)
		or any(name not in rows or cint(rows[name][1].fmge_tier) != tier for name, tier in zip(names, TIER_PATTERN, strict=True))
	):
		frappe.throw(_("Invalid Day 3 mock selection."), frappe.ValidationError)
	return names


@frappe.whitelist(allow_guest=True, methods=["GET", "POST"])
@rate_limit(limit=60, seconds=60 * 60)
def get_public_day3_quiz():
	quiz, rows, by_tier = _pool()
	names = select_questions(by_tier)
	return {
		"quiz": {
			"name": quiz.name,
			"title": quiz.title,
			"duration": quiz.duration,
			"total_marks": len(names),
			"passing_percentage": quiz.passing_percentage,
			"max_attempts": 0,
			"show_answers": 0,
			"show_submission_history": 0,
			"shuffle_questions": 0,
			"limit_questions_to": 0,
			"enable_negative_marking": 0,
			"enable_proctoring": 0,
			"selection_token": _token_for(names),
			"questions": [
				{"name": rows[name][0].name, "question": name, "marks": 1, "type": "Choices"}
				for name in names
			],
		},
		"questions_by_name": {
			name: {
				"name": name,
				"question": rows[name][1].question,
				"type": "Choices",
				"multiple": 0,
				"fmge_tier": cint(rows[name][1].fmge_tier),
				"fmge_difficulty": rows[name][1].fmge_difficulty,
				**{field: rows[name][1].get(field) for field in QUESTION_OPTION_FIELDS},
			}
			for name in names
		},
	}


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=20, seconds=60 * 60)
def submit_public_day3_quiz(results: str, selection_token: str):
	if not isinstance(results, str) or len(results.encode("utf-8")) > MAX_RESULTS_BYTES:
		frappe.throw(_("Invalid Day 3 answers."), frappe.ValidationError)
	try:
		answer_rows = json.loads(results)
	except (TypeError, ValueError):
		frappe.throw(_("Invalid Day 3 answers."), frappe.ValidationError)
	if not isinstance(answer_rows, list) or len(answer_rows) > len(TIER_PATTERN):
		frappe.throw(_("Invalid Day 3 answers."), frappe.ValidationError)
	quiz, rows, _ = _pool()
	names = _selected(selection_token, rows)
	selected = set(names)
	answers = {}
	for item in answer_rows:
		if not isinstance(item, dict) or set(item) != {"question_name", "answer"}:
			frappe.throw(_("Invalid Day 3 answers."), frappe.ValidationError)
		name, answer = item["question_name"], item["answer"]
		if name not in selected or name in answers or not isinstance(answer, list) or len(answer) > 1:
			frappe.throw(_("Invalid Day 3 answers."), frappe.ValidationError)
		if answer and not _is_option(rows[name][1], answer[0]):
			frappe.throw(_("Invalid Day 3 answers."), frappe.ValidationError)
		answers[name] = answer[0] if answer else None
	review = [
		{
			"question": rows[name][1].question,
			**_feedback(rows[name][1], answers.get(name), SOURCE_DOCUMENT, SOURCE_PDF_URL),
		}
		for name in names
	]
	score = sum(item["is_correct"] for item in review)
	percentage = round(score * 100 / len(names), 2)
	return {
		"score": score,
		"score_out_of": len(names),
		"percentage": percentage,
		"pass": percentage >= cint(quiz.passing_percentage),
		"is_open_ended": False,
		"review": review,
	}


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=600, seconds=60 * 60)
def check_public_day3_answer(question: str, answer: str, selection_token: str):
	_, rows, _ = _pool()
	if question not in _selected(selection_token, rows) or not _is_option(rows[question][1], answer):
		frappe.throw(_("Invalid Day 3 answer."), frappe.ValidationError)
	return _feedback(rows[question][1], answer, SOURCE_DOCUMENT, SOURCE_PDF_URL)
