"""Pure selection tests; safe to run without an LMS test-site teardown."""

import inspect
import json
import random
import unittest
from collections import Counter
from pathlib import Path
from unittest.mock import patch

import frappe

from lms.fmge import day3_mock
from lms.fmge.day3_mock import (
	CONCEPT_GROUPS,
	GROUP_OF_ID,
	POOL_COUNTS,
	TIER_COUNTS,
	TIER_PATTERN,
	select_questions,
)

DATA = Path(__file__).parent / "data"


def _bank_items():
	for section in range(1, 5):
		yield from json.loads((DATA / f"psm_day3_section_{section}.json").read_text())["questions"]


class TestDay3Selection(unittest.TestCase):
	def setUp(self):
		self.pool = {
			tier: [f"tier-{tier}-question-{index}" for index in range(count)]
			for tier, count in POOL_COUNTS.items()
		}

	def test_fixed_tier_slots_and_unique_questions(self):
		selected = select_questions(self.pool, random.Random(7))
		self.assertEqual(len(selected), 54)
		self.assertEqual(len(set(selected)), 54)
		self.assertEqual([int(name.split("-")[1]) for name in selected], list(TIER_PATTERN))
		self.assertEqual(
			{tier: sum(name.startswith(f"tier-{tier}-") for name in selected) for tier in TIER_COUNTS},
			TIER_COUNTS,
		)

	def test_new_draw_changes_questions_without_changing_slots(self):
		first = select_questions(self.pool, random.Random(7))
		second = select_questions(self.pool, random.Random(8))
		self.assertNotEqual(first, second)
		self.assertNotEqual(set(first), set(second))
		self.assertEqual(
			[int(name.split("-")[1]) for name in first],
			[int(name.split("-")[1]) for name in second],
		)

	def test_incomplete_pool_is_rejected(self):
		self.pool[3].pop()
		with self.assertRaisesRegex(ValueError, "incomplete"):
			select_questions(self.pool, random.Random(7))


class TestDay3ConceptGroups(unittest.TestCase):
	def setUp(self):
		self.pool = {tier: [] for tier in TIER_COUNTS}
		for item in _bank_items():
			self.pool[item["tier"]].append(item["id"])

	def test_group_ids_exist_in_the_banks(self):
		self.assertEqual({tier: len(ids) for tier, ids in self.pool.items()}, POOL_COUNTS)
		all_ids = {qid for ids in self.pool.values() for qid in ids}
		self.assertLessEqual(set(GROUP_OF_ID), all_ids)

	def test_draws_respect_group_limits(self):
		for seed in range(300):
			selected = select_questions(self.pool, random.Random(seed), GROUP_OF_ID)
			self.assertEqual(len(set(selected)), len(TIER_PATTERN))
			used = Counter(GROUP_OF_ID[qid] for qid in selected if qid in GROUP_OF_ID)
			for group, count in used.items():
				self.assertLessEqual(count, CONCEPT_GROUPS[group][0], group)


class TestDay3Endpoints(unittest.TestCase):
	def test_invalid_answers_raise_validation_error(self):
		submit = inspect.unwrap(day3_mock.submit_public_day3_quiz)
		check = inspect.unwrap(day3_mock.check_public_day3_answer)
		pool = ({}, {}, {}, {})
		with (
			patch.object(day3_mock, "_pool", return_value=pool),
			patch.object(day3_mock, "_selected", return_value=[]),
			patch.object(day3_mock.frappe, "throw", side_effect=frappe.ValidationError),
		):
			with self.assertRaises(frappe.ValidationError):
				submit("not json", "token")
			with self.assertRaises(frappe.ValidationError):
				submit(json.dumps([{"question_name": "x", "answer": ["A"]}]), "token")
			with self.assertRaises(frappe.ValidationError):
				check("x", "A", "token")


if __name__ == "__main__":
	unittest.main()
