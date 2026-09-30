#!/usr/bin/env python3
"""Build a packaged FMGE question bank from a reviewed Markdown source and lint its exam style."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE = ROOT / "research/pdf_extracted_questions_data/Day2_PSM_combined.md"
DEFAULT_OUTPUT = ROOT / "lms/fmge/data/psm_block_1.json"
ANSWER_KEY_HEADING = "# ANSWER KEY AND TEACHING REVIEW"
# A long PDF is delivered as several mock sections in one reply thread, each headed like this.
SECTION_HEADING_RE = re.compile(r"^#\s+SECTION\s+(\d+)\s+OF\s+(\d+)\b.*$", re.MULTILINE | re.IGNORECASE)
PUBLIC_DIR = ROOT / "lms/public"
DIFFICULTY_BY_TIER = {1: "direct", 2: "moderate", 3: "hard"}

# Real FMGE stems never point at study material; a stem that does is testing the notes, not medicine.
SOURCE_REFERENCE_RE = re.compile(
	r"\b(?:the|these|your|in the|from the) (?:notes?|source|pdf|slides?|handout)\b"
	r"|\bpdf\b|\bslide\b|\bon page\b|\bp\.\s*\d"
	r"|\baccording to the (?:notes?|source|pdf|table|figure|chart|slide|schedule shown)\b"
	r"|\b(?:shown|displayed|annotated|listed|given|depicted) (?:in|on) the (?:notes?|source|pdf|table|figure|chart|slide|page)\b",
	re.IGNORECASE,
)
# "The preferred method listed…" still points at the notes, even without naming them.
LISTED_RE = re.compile(r"\b(?:listed|specified|mentioned|stated)\b", re.IGNORECASE)
# Explanations are read by students; audit notes and pointers at the notes belong in the audit.
EXPLANATION_NOTE_RE = re.compile(
	r"\b(?:listed|specified|handout|here)\b|should not be presented|excluded from the options"
	r"|\bthis does not make\b",
	re.IGNORECASE,
)
# Without an attached image, "shown"/"displayed" can only refer to the notes.
SHOWN_RE = re.compile(r"\b(?:shown|displayed|annotated|depicted)\b", re.IGNORECASE)
# The stem must not hand the learner the fact that decides the answer.
PREMISE_LEAK_RE = re.compile(
	r"\b(?:states?|stated|teaches|taught|mentions?|notes?|shows?|annotates?) that\b"
	r"|\b(?:identifies|marks|lists|classifies|defines|describes) [\w\s-]{1,40}? as\b"
	r"|\bis (?:described|defined|listed|marked|identified) (?:as|under)\b",
	re.IGNORECASE,
)
BANNED_OPTION_RE = re.compile(
	r"^(?:all|none) of the (?:above|following)$|^both [a-d] and [a-d]$", re.IGNORECASE
)
SOURCE_PAGE_RE = re.compile(r"\bpp?\.\s*\d")
MAX_STEM_WORDS = 60
# Two unrelated recalls glued into one item ("Which pair correctly gives X and Y?").
DOUBLE_BARREL_RE = re.compile(
	r"\b(?:which|what) (?:pair|combination)\b|\bcorrect(?:ly)? (?:pair|combination|match(?:es)?)\b|\bmatches both\b",
	re.IGNORECASE,
)
VIGNETTE_RE = re.compile(
	r"\b\d+[- ]?(?:year|yr|month|day|week)s?[- ]?old\b|\bpatient\b|\bpresents?\b|\bbrought\b|\badmitted\b"
	r"|\bhistory of\b|\ba (?:young |pregnant |middle-aged |old |elderly )?(?:man|woman|male|female|child|boy|girl"
	r"|neonate|newborn|baby|infant|lady|farmer|worker|primigravida)\b",
	re.IGNORECASE,
)
LEADING_NUMBER_RE = re.compile(r"^[<>≤≥~≈]?\s*([+\-−]?)\s*[₹$]?\s*(\d+(?:[.,]\d+)?)")
# Measured from 1,001 provider-labelled FMGE recall questions (2021-2024), see
# research/fmge-source-material/analysis/recall-pattern-stats.md: share of one-liners,
# clinical vignettes and image-led stems per subject.
SUBJECT_PROFILES = {
	"Anatomy": (0.20, 0.12, 0.61),
	"Physiology": (0.69, 0.16, 0.03),
	"Biochemistry": (0.55, 0.24, 0.13),
	"Pathology": (0.39, 0.41, 0.10),
	"Microbiology": (0.33, 0.47, 0.16),
	"Pharmacology": (0.39, 0.46, 0.13),
	"Forensic Medicine": (0.30, 0.22, 0.15),
	"Medicine": (0.25, 0.59, 0.14),
	"Psychiatry": (0.29, 0.65, 0.00),
	"Dermatology": (0.14, 0.18, 0.64),
	"General Surgery": (0.23, 0.51, 0.20),
	"Anaesthesiology": (0.41, 0.32, 0.14),
	"Orthopaedics": (0.04, 0.35, 0.61),
	"Radiology": (0.38, 0.12, 0.50),
	"Paediatrics": (0.30, 0.53, 0.13),
	"Ophthalmology": (0.13, 0.53, 0.29),
	"ENT": (0.23, 0.57, 0.14),
	"Obstetrics & Gynaecology": (0.40, 0.33, 0.20),
	"Community Medicine": (0.50, 0.22, 0.02),
}


def clean_inline(value: str) -> str:
	value = value.strip()
	value = value.replace("**", "").replace("__", "").replace("`", "")
	value = re.sub(r"\s+", " ", value)
	return value.strip()


def strip_code_fences(text: str) -> str:
	"""Web sessions often wrap parts of the reply in ``` fences; they carry no content."""
	return "\n".join(line for line in text.splitlines() if not line.strip().startswith("```"))


def select_section(text: str, section: int | None) -> str:
	"""Return one section of a multi-section source; a single-section source is returned whole."""
	text = strip_code_fences(text)
	headings = list(SECTION_HEADING_RE.finditer(text))
	if not headings:
		if section not in (None, 1):
			raise ValueError(f"Source has no '# SECTION {section} OF N' heading")
		return text
	numbers = [int(match.group(1)) for match in headings]
	if len(set(numbers)) != len(numbers):
		raise ValueError(f"Duplicate section headings: {numbers}")
	if section is None:
		if len(headings) > 1:
			raise ValueError(f"Source holds sections {numbers}; choose one with --section")
		section = numbers[0]
	if section not in numbers:
		raise ValueError(f"Section {section} not found; source holds sections {numbers}")
	index = numbers.index(section)
	end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
	return text[headings[index].end() : end]


def parse_question_blocks(text: str, id_prefix: str = "PSM-B1") -> list[dict]:
	text = strip_code_fences(text)
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
		image_source = ""
		for row in block:
			stripped = row.strip()
			image_match = re.match(r"^\*\*Image:\*\*\s+(.+)$", stripped)
			image_alt_match = re.match(r"^\*\*Image alt:\*\*\s+(.+)$", stripped)
			image_source_match = re.match(r"^\*\*Image source:\*\*\s+(.+)$", stripped)
			option_match = re.match(r"^([A-D])\.\s+(.*)$", stripped)
			if image_match and not option_rows:
				image_url = clean_inline(image_match.group(1))
			elif image_alt_match and not option_rows:
				image_alt = clean_inline(image_alt_match.group(1))
			elif image_source_match and not option_rows:
				image_source = clean_inline(image_source_match.group(1))
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
			"id": f"{id_prefix}-Q{number:03d}",
			"number": number,
			"tier": current_tier,
			"difficulty": DIFFICULTY_BY_TIER[current_tier],
			"stem": stem,
			"options": [text for _, text in option_rows],
		}
		if image_alt and not image_url:
			raise ValueError(f"Q{number} has image alt text but no image URL")
		if image_source and not image_url:
			raise ValueError(
				f"Q{number} needs its image cropped from '{image_source}'; run "
				"scripts/fmge/extract_pdf_image.py and add the printed **Image:** line"
			)
		if image_url:
			question["image_url"] = image_url
			question["image_alt"] = image_alt or "Question image"
			if image_source:
				question["image_source"] = image_source
		questions.append(question)

	return questions


def parse_answer_key(text: str) -> dict[int, dict]:
	text = strip_code_fences(text)
	_, marker, answer_text = text.partition(ANSWER_KEY_HEADING)
	if not marker:
		raise ValueError(f"Missing heading: {ANSWER_KEY_HEADING}")

	pattern = re.compile(
		r"^###\s+Q(\d+)\s+[—–-]\s+\*\*([A-D])\s+[—–-]\s+(.*?)\*\*\s*$",
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


def build_bank(
	source: Path,
	*,
	bank_id: str = "fmge-psm-block-1",
	id_prefix: str = "PSM-B1",
	title: str = "FMGE PSM Day 2 Mock",
	subject: str = "Community Medicine",
	description: str = "FMGE-style 50-question PSM section generated from the reviewed Day 2 PSM source.",
	expected_questions: int | None = None,
	order: str = "source",
	section: int | None = None,
) -> dict:
	text = select_section(source.read_text(encoding="utf-8"), section)
	questions = parse_question_blocks(text, id_prefix)
	answers = parse_answer_key(text)

	if not questions:
		raise ValueError("No questions found")
	if expected_questions is None:
		expected_questions = len(questions)
	elif len(questions) != expected_questions:
		raise ValueError(f"Expected {expected_questions} questions, found {len(questions)}")
	if set(answers) != {question["number"] for question in questions}:
		raise ValueError("Answer key does not cover exactly the parsed question set")

	for question in questions:
		answer = answers[question["number"]]
		question.update(answer)
		correct_index = ord(question["correct_option"]) - ord("A")
		question["answer_label"] = question.pop("answer")
		question["answer"] = question["options"][correct_index]

	if order == "interleaved":
		questions = interleave_tiers(questions)
	elif order != "source":
		raise ValueError(f"Unknown question order: {order}")

	return {
		"schema_version": 1,
		"bank_id": bank_id,
		"title": title,
		"subject": subject,
		"description": description,
		"expected_questions": expected_questions,
		"duration_minutes": expected_questions,
		"max_attempts": 1,
		"passing_percentage": 50,
		"show_answers": 0,
		"show_submission_history": 1,
		"shuffle_questions": 0,
		"enable_negative_marking": 0,
		"questions": questions,
	}


def interleave_tiers(questions: list[dict]) -> list[dict]:
	"""Spread each tier evenly through the section, as a real FMGE section mixes difficulty."""
	by_tier: dict[int, list[dict]] = {}
	for question in questions:
		by_tier.setdefault(question["tier"], []).append(question)
	keyed = [
		((index + 0.5) / len(items), tier, question)
		for tier, items in by_tier.items()
		for index, question in enumerate(items)
	]
	return [question for _, _, question in sorted(keyed, key=lambda row: (row[0], row[1]))]


def _normalize(value: str) -> str:
	return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def lint_bank(bank: dict) -> tuple[list[str], list[str]]:
	"""Return (errors, warnings) for FMGE exam-style problems the generator is known to produce."""
	errors: list[str] = []
	warnings: list[str] = []
	questions = bank["questions"]

	for q in questions:
		label = f"Q{q['number']}"
		stem = q["stem"]
		has_image = bool(q.get("image_url"))

		if (
			SOURCE_REFERENCE_RE.search(stem)
			or LISTED_RE.search(stem)
			or (not has_image and SHOWN_RE.search(stem))
		):
			errors.append(f"{label}: stem refers to the study material instead of standing alone")
		if PREMISE_LEAK_RE.search(stem):
			errors.append(f"{label}: stem states the fact the answer depends on")

		normalized = [_normalize(option) for option in q["options"]]
		if len(set(normalized)) != len(normalized):
			errors.append(f"{label}: duplicate options")
		if any(BANNED_OPTION_RE.match(option.strip()) for option in q["options"]):
			errors.append(f"{label}: all/none-of-the-above or combined-letter option")

		answer = _normalize(q["answer"])
		if len(answer) >= 5 and not answer.replace(" ", "").isdigit() and answer in _normalize(stem):
			warnings.append(f"{label}: correct option text appears in the stem")

		words = len(stem.split())
		if words > MAX_STEM_WORDS:
			warnings.append(f"{label}: stem has {words} words (> {MAX_STEM_WORDS}; FMGE allows ~1 minute)")

		correct_index = ord(q["correct_option"]) - ord("A")
		correct_length = len(q["options"][correct_index])
		longest_distractor = max(len(o) for i, o in enumerate(q["options"]) if i != correct_index)
		if correct_length >= 20 and correct_length > 1.5 * longest_distractor:
			warnings.append(f"{label}: correct option is much longer than every distractor")

		if DOUBLE_BARREL_RE.search(stem):
			warnings.append(f"{label}: asks for a pair/combination; FMGE items test one relationship")

		numbers = [LEADING_NUMBER_RE.match(option.strip()) for option in q["options"]]
		if all(numbers):
			values = [
				float(match.group(2).replace(",", ""))
				* (-1 if match.group(1) in "-−" and match.group(1) else 1)
				for match in numbers
			]
			if values not in (sorted(values), sorted(values, reverse=True)):
				warnings.append(f"{label}: numeric options are not in ascending order")

		explanation = q.get("explanation") or ""
		if not explanation:
			errors.append(f"{label}: missing teaching explanation")
		elif SOURCE_REFERENCE_RE.search(explanation) or EXPLANATION_NOTE_RE.search(explanation):
			warnings.append(f"{label}: explanation points at the notes or carries an audit note")
		# A key moved during letter balancing leaves an explanation that argues for another option.
		explained = _normalize(explanation)
		answer_words = {word for word in answer.split() if len(word) >= 4}
		if answer_words and not answer_words & set(explained.split()):
			for letter, option in zip("ABCD", q["options"], strict=True):
				other = _normalize(option)
				if letter != q["correct_option"] and len(other) >= 5 and other in explained:
					errors.append(
						f"{label}: explanation names option {letter}, not the keyed answer; check the key"
					)
					break
		if not SOURCE_PAGE_RE.search(q.get("source") or ""):
			errors.append(f"{label}: source citation has no PDF page (p.N)")

	# Items in one section must not answer or echo each other.
	for q in questions:
		answer = _normalize(q["answer"])
		# Single common words ("Epidemic") collide with ordinary stem wording; the give-aways
		# worth catching are phrases and values ("1 lakh IU/mL", "vaccine carrier").
		if len(answer) < 5 or answer.replace(" ", "").isdigit() or " " not in answer:
			continue
		for other in questions:
			if other is not q and answer in _normalize(other["stem"]):
				errors.append(
					f"Q{other['number']}: stem gives away the answer to Q{q['number']} ('{q['answer']}')"
				)
	option_sets = [(q["number"], {_normalize(o) for o in q["options"]}) for q in questions]
	for index, (number, options) in enumerate(option_sets):
		for other_number, other_options in option_sets[index + 1 :]:
			if len(options & other_options) >= 3:
				warnings.append(f"Q{number} and Q{other_number} share 3+ options; vary the option sets")

	total = len(questions)
	if total:
		counts = {letter: sum(q["correct_option"] == letter for q in questions) for letter in "ABCD"}
		for letter, count in counts.items():
			# Letter shares mean little in a very short section.
			if total >= 12 and not 0.15 <= count / total <= 0.35:
				warnings.append(f"answer key: {letter} is correct in {count}/{total} questions")
		keys = "".join(q["correct_option"] for q in questions)
		run = re.search(r"([A-D])\1{3,}", keys)
		if run:
			warnings.append(f"answer key: {len(run.group(0))} consecutive '{run.group(1)}' answers")

		longest = 0
		for q in questions:
			lengths = [len(o) for o in q["options"]]
			correct = lengths[ord(q["correct_option"]) - ord("A")]
			if correct == max(lengths) and lengths.count(correct) == 1:
				longest += 1
		if longest / total > 0.4:
			warnings.append(
				f"options: the correct option is the unique longest in {longest}/{total} questions"
			)

		profile = SUBJECT_PROFILES.get(bank.get("subject", ""))
		images = sum(bool(q.get("image_url")) for q in questions) / total
		if not images and (profile is None or profile[2] >= 0.05):
			warnings.append(
				"no image-led questions; FMGE uses images in this subject when the source has usable visuals"
			)
		if profile:
			vignettes = sum(bool(VIGNETTE_RE.search(q["stem"])) for q in questions) / total
			one_liners = (
				sum(len(q["stem"].split()) <= 15 and not q.get("image_url") for q in questions) / total
			)
			if vignettes > profile[1] + 0.25:
				warnings.append(
					f"stem mix: {vignettes:.0%} clinical vignettes vs {profile[1]:.0%} in real FMGE "
					f"{bank['subject']}; convert some to direct one-liners"
				)
			if one_liners < profile[0] - 0.25:
				warnings.append(
					f"stem mix: {one_liners:.0%} one-liners vs {profile[0]:.0%} in real FMGE {bank['subject']}"
				)

	return errors, warnings


def format_lint_report(bank: dict, errors: list[str], warnings: list[str]) -> str:
	questions = bank["questions"]
	tiers = {tier: sum(q["tier"] == tier for q in questions) for tier in (1, 2, 3)}
	images = sum(bool(q.get("image_url")) for q in questions)
	lines = [
		f"{bank['bank_id']}: {len(questions)} questions; tiers {tiers[1]}/{tiers[2]}/{tiers[3]}; "
		f"image-led {images}",
		*(f"ERROR   {message}" for message in errors),
		*(f"WARNING {message}" for message in warnings),
		f"{len(errors)} style errors, {len(warnings)} warnings",
	]
	return "\n".join(lines)


def _check_local_images(bank: dict) -> None:
	for q in bank["questions"]:
		url = q.get("image_url") or ""
		if url.startswith("/assets/lms/"):
			path = PUBLIC_DIR / url.removeprefix("/assets/lms/")
			if not path.is_file():
				raise ValueError(f"Q{q['number']} image not found: {path}")


def main() -> int:
	parser = argparse.ArgumentParser()
	parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
	parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
	parser.add_argument("--bank-id", default="fmge-psm-block-1")
	parser.add_argument("--id-prefix", default="PSM-B1", help="Question IDs become <prefix>-Q001...")
	parser.add_argument("--title", default="FMGE PSM Day 2 Mock")
	parser.add_argument("--subject", default="Community Medicine")
	parser.add_argument(
		"--description",
		default="FMGE-style 50-question PSM section generated from the reviewed Day 2 PSM source.",
	)
	parser.add_argument(
		"--expected",
		type=int,
		help="Fail unless the section has exactly this many questions (default: take the count found)",
	)
	parser.add_argument(
		"--section",
		type=int,
		help="Section number to build when the source holds several '# SECTION k OF m' parts",
	)
	parser.add_argument(
		"--order",
		choices=("source", "interleaved"),
		default="interleaved",
		help="source keeps Markdown order (tier blocks); interleaved mixes tiers through the section",
	)
	parser.add_argument(
		"--check",
		action="store_true",
		help="Validate source and existing output without rewriting it",
	)
	parser.add_argument("--lint", action="store_true", help="Print the FMGE style report without writing")
	parser.add_argument("--strict", action="store_true", help="Fail when the style lint finds errors")
	args = parser.parse_args()

	bank = build_bank(
		args.source,
		bank_id=args.bank_id,
		id_prefix=args.id_prefix,
		title=args.title,
		subject=args.subject,
		description=args.description,
		expected_questions=args.expected,
		order=args.order,
		section=args.section,
	)
	_check_local_images(bank)
	errors, warnings = lint_bank(bank)
	serialized = json.dumps(bank, ensure_ascii=False, indent=2) + "\n"

	if args.lint:
		print(format_lint_report(bank, errors, warnings))
		return 1 if args.strict and errors else 0
	if errors or warnings:
		print(
			f"Style lint: {len(errors)} errors, {len(warnings)} warnings (run with --lint for details)",
			file=sys.stderr,
		)
	if args.strict and errors:
		raise SystemExit("Refusing to write: FMGE style lint errors (see --lint)")

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
