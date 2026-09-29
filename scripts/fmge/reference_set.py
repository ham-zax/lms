#!/usr/bin/env python3
"""Pick real recalled FMGE questions for one subject as a level reference for the web session.

The set is pasted after the question-bank prompt (section 1B) so the generator can match
real FMGE difficulty, concept depth and distractor closeness. Questions are chosen to
mirror the subject's measured stem-form and task mix, favour recent sittings, and skip
cross-provider duplicates and repeats.

    python3 scripts/fmge/reference_set.py --subject "Community Medicine"
    python3 scripts/fmge/reference_set.py --subject Anatomy --count 20 --seed 2

Needs the local full-text corpus (extract_recall_questions.py) and the classification
CSV (analyse_recall_questions.py).
"""

from __future__ import annotations

import argparse
import csv
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESEARCH = ROOT / "research/fmge-source-material"
FULL_CSV = RESEARCH / "corpus/recall-questions-full.csv"
PATTERNS_CSV = RESEARCH / "extracted/question-patterns.csv"
OUTPUT_DIR = RESEARCH / "corpus/reference-sets"
# Model-predicted subjects at or above this probability are ~81% accurate overall and
# ~96% precise for Community Medicine (see analyse_recall_questions.py).
MIN_CONFIDENCE = 0.2
SESSION_ORDER = {"January": 1, "June": 6, "July": 7, "December": 12}


def load(subject: str) -> list[dict]:
	with FULL_CSV.open(encoding="utf-8") as handle:
		full = {row["question_id"]: row for row in csv.DictReader(handle)}
	with PATTERNS_CSV.open(encoding="utf-8") as handle:
		patterns = list(csv.DictReader(handle))
	rows = []
	for pattern in patterns:
		if pattern["subject"] != subject or pattern["provider"] != "PrepLadder":
			continue
		if (
			pattern["subject_method"] != "provider label"
			and float(pattern["subject_confidence"]) < MIN_CONFIDENCE
		):
			continue
		if pattern["repeat_of_earlier_sitting"]:
			continue
		text = full[pattern["question_id"]]
		options = [text[f"option_{letter}"] for letter in "abcd"]
		if not all(options) or not text["provider_answer"] or max(map(len, options)) > 200:
			continue
		rows.append({**pattern, **text, "options": options})
	return rows


def pick(rows: list[dict], count: int, seed: int) -> list[dict]:
	"""Quota by stem form (the subject's own mix), newest sittings first, varied tasks."""
	rng = random.Random(seed)
	rng.shuffle(rows)
	rows.sort(key=lambda r: (-int(r["year"]), -SESSION_ORDER.get(r["session"], 0)))

	forms = Counter(r["stem_type"] for r in rows)
	quotas = {form: max(1, round(count * n / len(rows))) for form, n in forms.items()}
	while sum(quotas.values()) > count:
		quotas[max(quotas, key=quotas.get)] -= 1

	by_form: dict[str, list[dict]] = defaultdict(list)
	for row in rows:
		by_form[row["stem_type"]].append(row)

	chosen: list[dict] = []
	for form, quota in quotas.items():
		pool = by_form[form]
		used_tasks: Counter = Counter()
		while quota and pool:
			# Prefer the task seen least so far within this form; pool is already newest first.
			best = min(range(len(pool)), key=lambda i: (used_tasks[pool[i]["task"]], i))
			row = pool.pop(best)
			used_tasks[row["task"]] += 1
			chosen.append(row)
			quota -= 1
	rng.shuffle(chosen)
	return chosen


def render(subject: str, chosen: list[dict]) -> str:
	sittings = sorted({f"{r['session']} {r['year']}" for r in chosen}, key=lambda s: (s[-4:], s))
	lines = [
		f"# FMGE REFERENCE SET — {subject} ({len(chosen)} recalled questions)",
		"",
		"Real FMGE questions, reconstructed from candidate recall (PrepLadder), from "
		+ ", ".join(sittings)
		+ ". Use them only as described in section 1B of the prompt: to match the level, the "
		"concept depth, the wording and how close the wrong options are. They are part of the "
		"exclusion set: do not copy, paraphrase or re-test them. Answers are provider keys and "
		"may be wrong. Examinable facts still come only from the uploaded PDF.",
		"",
	]
	for number, row in enumerate(chosen, start=1):
		stem = row["stem"]
		if row["image_based"] == "yes":
			stem += " [In the exam this question shows an image, which is not reproduced here.]"
		lines += [f"### R{number} (FMGE {row['session']} {row['year']})", stem, ""]
		lines += [f"{letter}. {option}" for letter, option in zip("ABCD", row["options"], strict=True)]
		lines += ["", f"Answer: {row['provider_answer']}", ""]
	return "\n".join(lines)


def main() -> int:
	parser = argparse.ArgumentParser(
		description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
	)
	parser.add_argument("--subject", required=True, help='Blueprint subject, e.g. "Community Medicine"')
	parser.add_argument("--count", type=int, default=15)
	parser.add_argument("--seed", type=int, default=1, help="Change to draw a different set")
	parser.add_argument("--output", type=Path)
	args = parser.parse_args()

	rows = load(args.subject)
	if len(rows) < args.count:
		raise SystemExit(f"Only {len(rows)} usable questions for {args.subject!r}")
	chosen = pick(rows, args.count, args.seed)
	slug = re.sub(r"[^a-z0-9]+", "-", args.subject.lower()).strip("-")
	output = args.output or OUTPUT_DIR / f"{slug}.md"
	output.parent.mkdir(parents=True, exist_ok=True)
	output.write_text(render(args.subject, chosen), encoding="utf-8")

	forms = Counter(r["stem_type"] for r in chosen)
	years = Counter(r["year"] for r in chosen)
	print(f"Wrote {len(chosen)} questions to {output}")
	print(f"  from {len(rows)} usable; stem forms {dict(forms)}; years {dict(sorted(years.items()))}")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
