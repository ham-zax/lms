#!/usr/bin/env python3
"""Build the packaged FMGE PSM question bank from the reviewed Markdown source."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE = ROOT / "research/pdf_extracted_questions_data/Day2_PSM_combined.md"
DEFAULT_OUTPUT = ROOT / "lms/fmge/data/psm_block_1.json"
ANSWER_KEY_HEADING = "# ANSWER KEY AND TEACHING REVIEW"


def clean_inline(value: str) -> str:
	value = value.strip()
	value = value.replace("**", "").replace("__", "").replace("`", "")
	value = re.sub(r"\s+", " ", value)
	return value.strip()


def parse_question_blocks(text: str) -> list[dict]:
	question_text, marker, _ = text.partition(ANSWER_KEY_HEADING)
	if not marker:
		raise ValueError(f"Missing heading: {ANSWER_KEY_HEADING}")

	lines = question_text.splitlines()
	questions: list[dict] = []
	current_tier: int | None = None
	i = 0

	while i < len(lines):
		tier_match = re.match(r"^#{1,2}\s+TIER\s+([123])\b", lines[i])
		if tier_match:
			current_tier = int(tier_match.group(1))
			i += 1
			continue

		question_match = re.match(r"^###\s+Q(\d+)\s*$", lines[i])
		if not question_match:
			i += 1
			continue
		if current_tier is None:
			raise ValueError(f"Question {question_match.group(1)} appears before a tier heading")

		number = int(question_match.group(1))
		i += 1
		block: list[str] = []
		while i < len(lines):
			if re.match(r"^###\s+Q\d+\s*$", lines[i]) or re.match(r"^#{1,2}\s+TIER\s+[123]\b", lines[i]):
				break
			if lines[i].strip() != "---":
				block.append(lines[i])
			i += 1

		option_rows: list[tuple[str, str]] = []
		stem_rows: list[str] = []
		image_url = ""
		image_alt = ""
		for row in block:
			stripped = row.strip()
			image_match = re.match(r"^\*\*Image:\*\*\s+(.+)$", stripped)
			image_alt_match = re.match(r"^\*\*Image alt:\*\*\s+(.+)$", stripped)
			option_match = re.match(r"^([A-D])\.\s+(.*)$", stripped)
			if image_match and not option_rows:
				image_url = clean_inline(image_match.group(1))
			elif image_alt_match and not option_rows:
				image_alt = clean_inline(image_alt_match.group(1))
			elif option_match:
				option_rows.append((option_match.group(1), clean_inline(option_match.group(2))))
			elif not option_rows and stripped:
				stem_rows.append(stripped)

		if [letter for letter, _ in option_rows] != ["A", "B", "C", "D"]:
			raise ValueError(f"Q{number} must contain exactly A-D options in order")
		stem = clean_inline(" ".join(stem_rows))
		if not stem:
			raise ValueError(f"Q{number} has no stem")

		question = {
			"id": f"PSM-B1-Q{number:03d}",
			"number": number,
			"tier": current_tier,
			"difficulty": {1: "direct", 2: "moderate", 3: "hard"}[current_tier],
			"stem": stem,
			"options": [text for _, text in option_rows],
		}
		if image_alt and not image_url:
			raise ValueError(f"Q{number} has image alt text but no image URL")
		if image_url:
			question["image_url"] = image_url
			question["image_alt"] = image_alt or "Question image"
		questions.append(question)

	return questions


def parse_answer_key(text: str) -> dict[int, dict]:
	_, marker, answer_text = text.partition(ANSWER_KEY_HEADING)
	if not marker:
		raise ValueError(f"Missing heading: {ANSWER_KEY_HEADING}")

	pattern = re.compile(
		r"^###\s+Q(\d+)\s+—\s+\*\*([A-D])\s+—\s+(.*?)\*\*\s*$",
		re.MULTILINE,
	)
	matches = list(pattern.finditer(answer_text))
	answers: dict[int, dict] = {}

	for index, match in enumerate(matches):
		number = int(match.group(1))
		start = match.end()
		if index + 1 < len(matches):
			end = matches[index + 1].start()
		else:
			final_audit = answer_text.find("# FINAL PATTERN AUDIT", start)
			end = final_audit if final_audit != -1 else len(answer_text)
		block = answer_text[start:end]
		source_match = re.search(r"^\*\*Source:\*\*\s*(.+?)\s*$", block, re.MULTILINE)
		source = clean_inline(source_match.group(1)) if source_match else ""

		explanation_rows: list[str] = []
		for row in block.splitlines():
			stripped = row.strip()
			if not stripped or stripped == "---":
				continue
			if re.match(
				r"^\*\*(Archetype|Topic|Source|Closest distractor|Discriminator|Key discriminator|Concept link):\*\*",
				stripped,
			):
				continue
			if stripped.startswith("#"):
				continue
			explanation_rows.append(stripped)

		answers[number] = {
			"correct_option": match.group(2),
			"answer": clean_inline(match.group(3)),
			"source": source,
			"explanation": clean_inline(" ".join(explanation_rows)),
		}

	return answers


def build_bank(source: Path) -> dict:
	text = source.read_text(encoding="utf-8")
	questions = parse_question_blocks(text)
	answers = parse_answer_key(text)

	if len(questions) != 50:
		raise ValueError(f"Expected 50 questions, found {len(questions)}")
	if set(answers) != {question["number"] for question in questions}:
		raise ValueError("Answer key does not cover exactly the parsed question set")

	for question in questions:
		answer = answers[question["number"]]
		question.update(answer)
		correct_index = ord(question["correct_option"]) - ord("A")
		question["answer_label"] = question.pop("answer")
		question["answer"] = question["options"][correct_index]

	return {
		"schema_version": 1,
		"bank_id": "fmge-psm-block-1",
		"title": "FMGE PSM Mock 1 - Section 1",
		"subject": "Community Medicine",
		"description": "FMGE-style 50-question PSM section generated from the reviewed Day 2 PSM source.",
		"expected_questions": 50,
		"duration_minutes": 50,
		"max_attempts": 1,
		"passing_percentage": 50,
		"show_answers": 0,
		"show_submission_history": 1,
		"shuffle_questions": 0,
		"enable_negative_marking": 0,
		"questions": questions,
	}


def main() -> int:
	parser = argparse.ArgumentParser()
	parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
	parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
	parser.add_argument(
		"--check",
		action="store_true",
		help="Validate source and existing output without rewriting it",
	)
	args = parser.parse_args()

	bank = build_bank(args.source)
	serialized = json.dumps(bank, ensure_ascii=False, indent=2) + "\n"

	if args.check:
		if not args.output.exists():
			raise SystemExit(f"Missing generated bank: {args.output}")
		if args.output.read_text(encoding="utf-8") != serialized:
			raise SystemExit("Generated question bank is out of date")
		print(f"OK: {len(bank['questions'])} questions; generated bank is current")
		return 0

	args.output.parent.mkdir(parents=True, exist_ok=True)
	args.output.write_text(serialized, encoding="utf-8")
	print(f"Wrote {len(bank['questions'])} questions to {args.output}")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
