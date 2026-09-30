"""Anonymous practice and timed access to the reviewed Day 1 bank."""

import frappe
from frappe.rate_limiter import rate_limit

from lms.fmge.day1_course import BANK_ID, SOURCE_PDF_URL
from lms.fmge.public_quiz import _check_public_answer, _get_public_quiz, _submit_public_quiz

SOURCE_DOCUMENT = "Day 1 PSM notes"


@frappe.whitelist(allow_guest=True, methods=["GET", "POST"])
@rate_limit(limit=60, seconds=60 * 60)
def get_public_day1_quiz():
	return _get_public_quiz(BANK_ID)


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=20, seconds=60 * 60)
def submit_public_day1_quiz(results: str):
	return _submit_public_quiz(results, BANK_ID, SOURCE_DOCUMENT, SOURCE_PDF_URL)


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=600, seconds=60 * 60)
def check_public_day1_answer(question: str, answer: str):
	return _check_public_answer(question, answer, BANK_ID, SOURCE_DOCUMENT, SOURCE_PDF_URL)
