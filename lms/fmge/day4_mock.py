"""Anonymous practice and timed access to the reviewed Day 4 bank."""

import frappe
from frappe.rate_limiter import rate_limit

from lms.fmge.day4_course import COURSE, SOURCE_PDF_URL
from lms.fmge.public_quiz import _check_public_answer, _get_public_quiz, _submit_public_quiz

SOURCE_DOCUMENT = "Day 4 PSM notes"


@frappe.whitelist(allow_guest=True, methods=["GET", "POST"])
@rate_limit(limit=60, seconds=60 * 60)
def get_public_day4_quiz(section: int | str = 1):
	return _get_public_quiz(COURSE.section(section)["bank_id"])


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=20, seconds=60 * 60)
def submit_public_day4_quiz(results: str, section: int | str = 1):
	return _submit_public_quiz(results, COURSE.section(section)["bank_id"], SOURCE_DOCUMENT, SOURCE_PDF_URL)


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=600, seconds=60 * 60)
def check_public_day4_answer(question: str, answer: str, section: int | str = 1):
	return _check_public_answer(
		question, answer, COURSE.section(section)["bank_id"], SOURCE_DOCUMENT, SOURCE_PDF_URL
	)
