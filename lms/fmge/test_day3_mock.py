"""Day 3 section API regressions, using mocked documents without touching site data."""

from lms.fmge import day3_mock
from lms.fmge.day3_course import COURSE as DAY3_COURSE
from lms.fmge.test_day1_mock import TestDay1Mock


class TestDay3Mock(TestDay1Mock):
	course = DAY3_COURSE
	endpoint = day3_mock


class TestDay3Section2Mock(TestDay3Mock):
	section = 2


class TestDay3Section3Mock(TestDay3Mock):
	section = 3


class TestDay3Section4Mock(TestDay3Mock):
	section = 4


del TestDay1Mock
