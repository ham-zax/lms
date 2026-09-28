"""Tests for the FMGE Markdown-to-bank builder and its exam-style lint.

Run: python3 -m unittest scripts/fmge/test_build_question_bank.py
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import build_question_bank as builder  # noqa: E402

CLEAN_QUESTIONS = [
	(
		1,
		"The recommended storage temperature for most UIP vaccines at the point of use is:",
		["-15°C to -25°C", "+2°C to +8°C", "0°C to +2°C", "+8°C to +15°C"],
		"B",
	),
	(
		2,
		"A child aged 18 months attends for routine immunization. Which vaccine is due?",
		["BCG", "DPT booster-1", "TT", "Hepatitis B birth dose"],
		"B",
	),
	(
		3,
		"Cases rise sharply and fall within one incubation period after a wedding meal. The epidemic type is:",
		["Point-source", "Continuous common-source", "Propagated", "Slow modern"],
		"A",
	),
	(
		4,
		"The diluent used to reconstitute BCG vaccine is:",
		["Distilled water", "Phosphate-buffered saline", "Normal saline", "Dextrose 5%"],
		"C",
	),
]


def render(questions, *, extra_stem_lines=None, tier_for=lambda n: 1 + (n - 1) % 3):
	extra_stem_lines = extra_stem_lines or {}
	lines = ["# QUESTION BANK — BLOCK 1", ""]
	for tier in (1, 2, 3):
		lines += [f"## TIER {tier}", ""]
		for number, stem, options, _ in questions:
			if tier_for(number) != tier:
				continue
			lines += [f"### Q{number}", stem, *extra_stem_lines.get(number, []), ""]
			lines += [f"{letter}. {text}" for letter, text in zip("ABCD", options, strict=True)]
			lines.append("")
	lines += [builder.ANSWER_KEY_HEADING, ""]
	for number, _, options, key in questions:
		lines += [
			f"### Q{number} — **{key} — {options['ABCD'.index(key)]}**",
			"**Topic:** Test topic",
			f"**Source:** PDF p.{number + 10} | E0",
			"Why this option is correct, in one sentence.",
			"",
		]
	return "\n".join(lines)


class BuilderTestCase(unittest.TestCase):
	def build(self, text: str, **kwargs) -> dict:
		with tempfile.TemporaryDirectory() as tmp:
			path = Path(tmp) / "bank.md"
			path.write_text(text, encoding="utf-8")
			return builder.build_bank(path, expected_questions=kwargs.pop("expected", 4), **kwargs)

	def test_builds_ids_tiers_and_answers(self):
		bank = self.build(render(CLEAN_QUESTIONS), bank_id="fmge-test", id_prefix="PSM-B2")
		first = bank["questions"][0]
		self.assertEqual(bank["bank_id"], "fmge-test")
		self.assertEqual(bank["duration_minutes"], 4)
		self.assertEqual(first["id"], "PSM-B2-Q001")
		self.assertEqual(first["answer"], "+2°C to +8°C")
		self.assertEqual(first["source"], "PDF p.11 | E0")

	def test_clean_bank_has_no_style_errors(self):
		errors, _ = builder.lint_bank(self.build(render(CLEAN_QUESTIONS)))
		self.assertEqual(errors, [])

	def test_flags_stems_that_point_at_the_notes(self):
		questions = list(CLEAN_QUESTIONS)
		questions[3] = (4, "Which diluent is shown for BCG in the notes?", *questions[3][2:])
		errors, _ = builder.lint_bank(self.build(render(questions)))
		self.assertIn("Q4: stem refers to the study material instead of standing alone", errors)

	def test_flags_premise_leak(self):
		questions = list(CLEAN_QUESTIONS)
		questions[1] = (
			2,
			"Guidance states that measles vaccine within 3 days of exposure is protective. Best action?",
			*questions[1][2:],
		)
		errors, _ = builder.lint_bank(self.build(render(questions)))
		self.assertIn("Q2: stem states the fact the answer depends on", errors)

	def test_flags_banned_and_duplicate_options(self):
		questions = list(CLEAN_QUESTIONS)
		questions[0] = (1, questions[0][1], ["A", "B", "b", "All of the above"], "A")
		errors, _ = builder.lint_bank(self.build(render(questions)))
		self.assertIn("Q1: duplicate options", errors)
		self.assertIn("Q1: all/none-of-the-above or combined-letter option", errors)

	def test_shown_is_allowed_when_an_image_is_attached(self):
		questions = list(CLEAN_QUESTIONS)
		questions[2] = (3, "The epidemic curve shown is most consistent with:", *questions[2][2:])
		text = render(
			questions,
			extra_stem_lines={3: ["**Image:** /files/fmge/curve.png", "**Image alt:** Epidemic curve"]},
		)
		errors, warnings = builder.lint_bank(self.build(text))
		self.assertEqual(errors, [])
		self.assertFalse(any("no image-led" in warning for warning in warnings))

	def test_unresolved_image_source_blocks_the_build(self):
		text = render(CLEAN_QUESTIONS, extra_stem_lines={2: ["**Image source:** p.34 | cold box photo"]})
		with self.assertRaisesRegex(ValueError, "Q2 needs its image cropped"):
			self.build(text)

	def test_answer_heading_accepts_plain_hyphens(self):
		text = render(CLEAN_QUESTIONS).replace("— **", "- **").replace(" — ", " - ")
		keys = {q["number"]: q["correct_option"] for q in self.build(text)["questions"]}
		self.assertEqual(keys, {1: "B", 2: "B", 3: "A", 4: "C"})

	def test_parses_the_prompt_output_contract(self):
		text = "\n".join(
			[
				"```",
				"## DOCUMENT INGESTION REPORT",
				"- Page images visible: Yes",
				"# QUESTION BANK — BLOCK 2",
				"## TIER 1 — DIRECT / RECOGNITION",
				"### Q1",
				"The device shown is used for:",
				"**Image source:** p.61 | lower-left photo, vaccine carrier",
				"**Image:** /files/fmge/carrier.png",
				"**Image alt:** Insulated box with four ice packs",
				"",
				"A. Outreach sessions",
				"B. District storage",
				"C. State storage",
				"D. Air transport",
				"```",
				"# ANSWER KEY AND TEACHING REVIEW",
				"### Q1 — **A — Outreach sessions**",
				"**Archetype:** image",
				"**Topic:** Cold chain — carriers",
				"**Source:** PDF p.61 | E0 | Diagram",
				"**Closest distractor:** B — defeated by capacity, p.60",
				"**Concept link:** n/a",
				"A vaccine carrier keeps vaccines cold for a day of outreach; district stores use ILRs.",
				"# FINAL PATTERN AUDIT",
				"- Total: 1",
			]
		)
		question = self.build(text, expected=1)["questions"][0]
		self.assertEqual(question["image_source"], "p.61 | lower-left photo, vaccine carrier")
		self.assertEqual(question["image_url"], "/files/fmge/carrier.png")
		self.assertEqual(question["stem"], "The device shown is used for:")
		self.assertEqual(
			question["explanation"],
			"A vaccine carrier keeps vaccines cold for a day of outreach; district stores use ILRs.",
		)

	def test_flags_a_stem_that_gives_away_another_answer(self):
		questions = list(CLEAN_QUESTIONS)
		questions[1] = (
			2,
			"A child reconstituted with normal saline at 18 months. Which vaccine is due?",
			*questions[1][2:],
		)
		errors, _ = builder.lint_bank(self.build(render(questions)))
		self.assertIn("Q2: stem gives away the answer to Q4 ('Normal saline')", errors)

	def test_flags_pairs_unordered_numbers_and_reused_options(self):
		questions = list(CLEAN_QUESTIONS)
		questions[0] = (
			1,
			"Which pair correctly gives the dose?",
			["20 IU/kg", "40 IU/kg", "10 IU/kg", "50 IU/kg"],
			"A",
		)
		questions[3] = (4, "The dose of ERIG is:", ["20 IU/kg", "40 IU/kg", "10 IU/kg", "60 IU/kg"], "B")
		_, warnings = builder.lint_bank(self.build(render(questions)))
		self.assertIn("Q1: asks for a pair/combination; FMGE items test one relationship", warnings)
		self.assertIn("Q1: numeric options are not in ascending order", warnings)
		self.assertIn("Q1 and Q4 share 3+ options; vary the option sets", warnings)

	def test_image_warning_follows_the_subject_profile(self):
		bank = self.build(render(CLEAN_QUESTIONS), subject="Community Medicine")
		self.assertFalse(any("no image-led" in w for w in builder.lint_bank(bank)[1]))
		bank = self.build(render(CLEAN_QUESTIONS), subject="Anatomy")
		self.assertTrue(any("no image-led" in w for w in builder.lint_bank(bank)[1]))

	def test_interleaved_order_mixes_tiers(self):
		questions = [
			(n, f"Stem {n}?", [f"a{n}", f"b{n}", f"c{n}", f"d{n}"], "ABCD"[n % 4]) for n in range(1, 7)
		]
		bank = self.build(
			render(questions, tier_for=lambda n: 1 if n <= 3 else 2), expected=6, order="interleaved"
		)
		self.assertEqual([q["tier"] for q in bank["questions"]], [1, 2, 1, 2, 1, 2])
		self.assertEqual([q["id"] for q in bank["questions"]][:2], ["PSM-B1-Q001", "PSM-B1-Q004"])

	def test_flags_skewed_answer_key(self):
		questions = [(n, stem, options, "A") for n, stem, options, _ in CLEAN_QUESTIONS]
		_, warnings = builder.lint_bank(self.build(render(questions)))
		self.assertIn("answer key: 4 consecutive 'A' answers", warnings)


if __name__ == "__main__":
	unittest.main()
