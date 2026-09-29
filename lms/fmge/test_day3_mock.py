"""Pure selection tests; safe to run without an LMS test-site teardown."""

import random
import unittest

from lms.fmge.day3_mock import POOL_COUNTS, TIER_COUNTS, TIER_PATTERN, select_questions


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


if __name__ == "__main__":
	unittest.main()
