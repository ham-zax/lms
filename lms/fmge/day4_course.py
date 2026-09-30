"""Install and verify the reviewed Day 4 PSM course."""

from lms.fmge.course import PSMCourse

COURSE = PSMCourse(day=4)
COURSE_NAME = COURSE.course_name
QUIZ_NAME = COURSE.quiz_name
BANK_ID = COURSE.bank_id
BANK_FILE = COURSE.bank_file
SOURCE_PDF_URL = COURSE.source_pdf_url
MOCK_URL = COURSE.mock_url


def install_day4_psm_course():
	return COURSE.install()


def verify_day4_psm_course():
	return COURSE.verify()
