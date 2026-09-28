#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pypdfium2>=4", "beautifulsoup4>=4"]
# ///
"""Extract every recalled FMGE question from the local provider recall PDFs into one CSV.

The PDFs and the full-text CSV are third-party recall material: they stay local
(gitignored under research/fmge-source-material/corpus/) and are never committed.
Only the text-free classification CSV built by analyse_recall_questions.py is.

    uv run scripts/fmge/extract_recall_questions.py            # PDFs + cached FMGEPrep pages
    uv run scripts/fmge/extract_recall_questions.py --fetch    # (re)download FMGEPrep public samples first
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import re
import time
import urllib.request
from dataclasses import dataclass
from pathlib import Path

import pypdfium2 as pdfium
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
CORPUS = ROOT / "research/fmge-source-material/corpus"
OUTPUT = CORPUS / "recall-questions-full.csv"
FMGEPREP_DIR = CORPUS / "fmgeprep"
FMGEPREP_URL = "https://fmgeprep.com/fmge-previous-year-question-papers/{slug}"
# Public preview pages: ~10 sample questions per paper part, answer key embedded in the page data.
FMGEPREP_PAGES = [
	("fmge-jun-2021-part-1", 2021, "June", "1"),
	("fmge-jun-2021-part-2", 2021, "June", "2"),
	("fmge-dec-2021-part-1", 2021, "December", "1"),
	("fmge-dec-2021-part-2", 2021, "December", "2"),
	("fmge-june-2022-part-1", 2022, "June", "1"),
	("fmge-june-2022-part-2", 2022, "June", "2"),
	("fmge-jan-2023-part-1", 2023, "January", "1"),
	("fmge-jan-2023-part-2", 2023, "January", "2"),
	("fmge-july-2023-part-1", 2023, "July", "1"),
	("fmge-july-2023-part-2", 2023, "July", "2"),
	("fmge-jan-2024-part-1", 2024, "January", "1"),
	("fmge-jan-2024-part-2", 2024, "January", "2"),
	("fmge-july-2024-part-1", 2024, "July", "1"),
	("fmge-july-2024-part-2", 2024, "July", "2"),
	("fmge-jan-2025-part-1", 2025, "January", "1"),
	("fmge-jan-2025-part-2", 2025, "January", "2"),
	("fmge-july-2025-part-1", 2025, "July", "1"),
	("fmge-july-2025-part-2", 2025, "July", "2"),
	("fmge-jan-2026-part-1", 2026, "January", "1"),
	("fmge-jan-2026-part-2", 2026, "January", "2"),
	("fmge-june-2026-part-a", 2026, "June", "1"),
	("fmge-june-2026-part-b", 2026, "June", "2"),
]


@dataclass(frozen=True)
class Source:
	file: str
	year: int
	session: str
	part: str
	layout: str  # "quesno" (2021-2023), "bullets" (2024 samples), "numbered" (2025 parts)
	url: str
	completeness: str  # "full" = whole sitting or whole part; "sample" = provider selection


SOURCES = [
	Source(
		"2021/2021-12__prepladder__full.pdf",
		2021,
		"December",
		"full",
		"quesno",
		"https://image.prepladder.com/content/FMGE-dec-2021-pyq-pdf.pdf",
		"full",
	),
	Source(
		"2022/2022-06__prepladder__full.pdf",
		2022,
		"June",
		"full",
		"quesno",
		"https://image.prepladder.com/content/fmge-jun-2022-pyq-pdf.pdf",
		"full",
	),
	Source(
		"2023/2023-01__prepladder__full.pdf",
		2023,
		"January",
		"full",
		"quesno",
		"https://image.prepladder.com/content/fmge-jan-2023-pyq-pdf.pdf",
		"full",
	),
	Source(
		"2024/2024-01__prepladder__sample.pdf",
		2024,
		"January",
		"sample",
		"bullets",
		"https://image.prepladder.com/content/FMGE_Jan_2024_Question_paper.docx.pdf",
		"sample",
	),
	Source(
		"2024/2024-06__prepladder__sample.pdf",
		2024,
		"June",
		"sample",
		"bullets",
		"https://image.prepladder.com/content/FMGE_June_2024_Question_Paper.docx.pdf",
		"sample",
	),
	Source(
		"2025/2025-01__prepladder__part-1.pdf",
		2025,
		"January",
		"1",
		"numbered",
		"https://image.prepladder.com/content/FMGE%20Jan%202025%20Part%201.pdf",
		"full",
	),
	Source(
		"2025/2025-01__prepladder__part-2.pdf",
		2025,
		"January",
		"2",
		"numbered",
		"https://image.prepladder.com/content/FMGE%20Jan%202025%20Part%202.pdf",
		"full",
	),
	Source(
		"2025/2025-07__prepladder__part-1.pdf",
		2025,
		"July",
		"1",
		"numbered",
		"https://image.prepladder.com/content/FMGE%20July%202025%20Part%201.pdf",
		"full",
	),
	Source(
		"2025/2025-07__prepladder__part-2.pdf",
		2025,
		"July",
		"2",
		"numbered",
		"https://image.prepladder.com/content/FMGE%20July%202025%20Part%202.pdf",
		"full",
	),
]

FIELDS = [
	"question_id",
	"year",
	"session",
	"part",
	"provider",
	"completeness",
	"source_file",
	"source_question_number",
	"source_page",
	"provider_subject",
	"provider_topic",
	"stem",
	"option_a",
	"option_b",
	"option_c",
	"option_d",
	"provider_answer",
	"provider_image",
]

PAGE_RE = re.compile(r"^=====PAGE (\d+)=====$")
NOISE_RE = re.compile(r"^(?:\d{1,3}|PrepLadder)$")


def clean(value: str) -> str:
	value = html.unescape(value).replace("￾", "-").replace("­", "")
	return re.sub(r"\s+", " ", value).strip()


def pdf_lines(path: Path) -> list[tuple[int, str]]:
	"""Return (page, line) pairs with running page headers/footers removed."""
	doc = pdfium.PdfDocument(str(path))
	rows: list[tuple[int, str]] = []
	for index in range(len(doc)):
		text = doc[index].get_textpage().get_text_range()
		for line in text.replace("\r", "").split("\n"):
			line = line.strip()
			if line and not NOISE_RE.match(line):
				rows.append((index + 1, line))
	return rows


def _options_from(lines: list[str], markers: list[re.Pattern], end: re.Pattern) -> list[str]:
	options: list[list[str]] = []
	current: list[str] | None = None
	for line in lines:
		if end.match(line):
			break
		matched = next((m for m in markers if m.match(line)), None)
		if matched is not None:
			current = [matched.sub("", line, count=1)]
			options.append(current)
		elif current is not None:
			current.append(line)
	return [clean(" ".join(parts)) for parts in options]


def parse_quesno(rows: list[tuple[int, str]]) -> list[dict]:
	start_re = re.compile(r"^Ques No:\s*(\d+)\s*,\s*QuesID\s*:\s*(\d+)")
	starts = [i for i, (_, line) in enumerate(rows) if start_re.match(line)]
	items = []
	for n, begin in enumerate(starts):
		block = rows[begin : starts[n + 1] if n + 1 < len(starts) else len(rows)]
		number = int(start_re.match(block[0][1]).group(1))
		subject = topic = ""
		stem: list[str] = []
		body = [line for _, line in block[1:]]
		i = 0
		while i < len(body) and not re.match(r"^O1:", body[i]):
			line = body[i]
			if line.startswith("Subject:"):
				subject = clean(line.removeprefix("Subject:"))
			elif line.startswith("Topic:"):
				topic = clean(line.removeprefix("Topic:"))
			elif line.startswith("Sub-Topic:"):
				pass
			else:
				stem.append(line)
			i += 1
		markers = [re.compile(rf"^O{k}:\s*") for k in range(1, 5)]
		options = _options_from(body[i:], markers, re.compile(r"^Ans:"))
		answer = next((re.match(r"^Ans:\s*(\d)", line) for line in body if line.startswith("Ans:")), None)
		items.append(
			{
				"number": number,
				"page": block[0][0],
				"subject": subject,
				"topic": topic,
				"stem": clean(" ".join(stem)),
				"options": options,
				"answer": "ABCD"[int(answer.group(1)) - 1] if answer and answer.group(1) in "1234" else "",
			}
		)
	return items


def parse_bullets(rows: list[tuple[int, str]]) -> list[dict]:
	subjects = {
		"Anaesthesia",
		"Anatomy",
		"Biochemistry",
		"Community Medicine",
		"Dermatology",
		"ENT",
		"Forensic Medicine",
		"Gynaecology & Obstetrics",
		"Medicine",
		"Microbiology",
		"Ophthalmology",
		"Orthopaedics",
		"Paediatrics",
		"Pathology",
		"Pharmacology",
		"Physiology",
		"Psychiatry",
		"Radiology",
		"Surgery",
		"PSM",
		"OBGYN",
		"Obstetrics & Gynaecology",
		"Pediatrics",
	}
	items = []
	subject = ""
	i = 0
	number = 0
	while i < len(rows):
		page, line = rows[i]
		heading = line.removeprefix("Subject:").strip()
		if heading in subjects:
			subject = heading
			i += 1
			continue
		if not line.startswith("Q. "):
			i += 1
			continue
		number += 1
		stem = [line.removeprefix("Q. ")]
		i += 1
		while i < len(rows) and not rows[i][1].startswith("● A."):
			stem.append(rows[i][1])
			i += 1
		block = []
		while i < len(rows) and not rows[i][1].startswith("✅"):
			block.append(rows[i][1])
			i += 1
		markers = [re.compile(rf"^● {letter}\.\s*") for letter in "ABCD"]
		options = _options_from(block, markers, re.compile(r"^✅"))
		answer = re.search(r"Correct Answer:\s*(\d)", rows[i][1]) if i < len(rows) else None
		items.append(
			{
				"number": number,
				"page": page,
				"subject": subject,
				"topic": "",
				"stem": clean(" ".join(stem)),
				"options": options,
				"answer": "ABCD"[int(answer.group(1)) - 1] if answer and answer.group(1) in "1234" else "",
			}
		)
	return items


def parse_numbered(rows: list[tuple[int, str]]) -> list[dict]:
	# Headers vary: "1. Question :", "65 Question :", "133 . Question :", "10.Question :",
	# "17. Question", "Question :110", a bare "Question :", or "113) Question ID : 852685"
	# followed by a bare "Question :" line.
	start_re = re.compile(r"^(?:(\d+)\s*\.?\s*)?Question\s*:?\s*(\d+)?\s*$")
	id_re = re.compile(r"^(\d+)\)\s*Question ID\s*:")
	starts: list[tuple[int, int]] = []
	pending: int | None = None
	for i, (_, line) in enumerate(rows):
		id_match = id_re.match(line)
		if id_match:
			pending = int(id_match.group(1))
			continue
		match = start_re.match(line)
		if not match:
			continue
		number = match.group(1) or match.group(2)
		if number is None:
			number = pending if pending is not None else (starts[-1][1] + 1 if starts else 1)
		starts.append((i, int(number)))
		pending = None

	items = []
	for n, (begin, number) in enumerate(starts):
		block = rows[begin : starts[n + 1][0] if n + 1 < len(starts) else len(rows)]
		body = [line for _, line in block[1:]]
		stem: list[str] = []
		i = 0
		while i < len(body) and not re.match(r"^Option 1\s*:", body[i]):
			stem.append(body[i])
			i += 1
		markers = [re.compile(rf"^Option {k}\s*:\s*") for k in range(1, 5)]
		options = _options_from(body[i:], markers, re.compile(r"^Correct option\s*:"))
		answer = next(
			(
				re.match(r"^Correct option\s*:\s*(\d)", line)
				for line in body
				if line.startswith("Correct option")
			),
			None,
		)
		items.append(
			{
				"number": number,
				"page": block[0][0],
				"subject": "",
				"topic": "",
				"stem": clean(" ".join(stem)),
				"options": options,
				"answer": "ABCD"[int(answer.group(1)) - 1] if answer and answer.group(1) in "1234" else "",
			}
		)
	return items


PARSERS = {"quesno": parse_quesno, "bullets": parse_bullets, "numbered": parse_numbered}


def fetch_fmgeprep() -> None:
	FMGEPREP_DIR.mkdir(parents=True, exist_ok=True)
	for slug, *_ in FMGEPREP_PAGES:
		request = urllib.request.Request(
			FMGEPREP_URL.format(slug=slug), headers={"User-Agent": "Mozilla/5.0"}
		)
		with urllib.request.urlopen(request, timeout=60) as response:
			(FMGEPREP_DIR / f"{slug}.html").write_bytes(response.read())
		time.sleep(1)


def _fmgeprep_questions(page_html: str) -> tuple[list[dict], int | None]:
	"""Read the question array the page ships to its client-side quiz."""
	text = page_html.replace('\\"', '"').replace("\\\\", "\\")
	start = text.find('"questions":[{')
	if start == -1:
		return [], None
	array_start = text.index("[", start)
	questions, _ = json.JSONDecoder().raw_decode(text[array_start:])
	total = re.search(r'"totalQuestions":(\d+)', text[max(0, start - 200) : start])
	return questions, int(total.group(1)) if total else None


def fmgeprep_rows() -> list[dict]:
	rows = []
	for slug, year, session, part in FMGEPREP_PAGES:
		path = FMGEPREP_DIR / f"{slug}.html"
		if not path.is_file():
			raise SystemExit(f"Missing {path}; run with --fetch")
		questions, total = _fmgeprep_questions(path.read_text(encoding="utf-8"))
		print(f"fmgeprep/{slug}: {len(questions)} public sample questions of {total}")
		for item in questions:
			soup = BeautifulSoup(item["question"], "html.parser")
			options = [re.sub(r"^[A-D]\.\s*", "", option) for option in item["options"]]
			options = (options + ["", "", "", ""])[:4]
			index = item.get("correctOptionIndex")
			rows.append(
				{
					"question_id": f"fp-{year}-{session[:3].lower()}-{part}-{item['id']}",
					"year": year,
					"session": session,
					"part": part,
					"provider": "FMGEPrep",
					"completeness": "sample",
					"source_file": f"fmgeprep/{slug}.html",
					"source_question_number": item.get("seqNum", ""),
					"source_page": "",
					"provider_subject": "",
					"provider_topic": "",
					"stem": clean(soup.get_text(" ")),
					"option_a": clean(options[0]),
					"option_b": clean(options[1]),
					"option_c": clean(options[2]),
					"option_d": clean(options[3]),
					"provider_answer": "ABCD"[index] if isinstance(index, int) and 0 <= index < 4 else "",
					"provider_image": "yes" if soup.find("img") else "no",
				}
			)
	return rows


def main() -> int:
	parser = argparse.ArgumentParser()
	parser.add_argument(
		"--fetch", action="store_true", help="Download the FMGEPrep public sample pages first"
	)
	args = parser.parse_args()
	if args.fetch:
		fetch_fmgeprep()

	rows_out = []
	for source in SOURCES:
		path = CORPUS / source.file
		if not path.is_file():
			raise SystemExit(f"Missing {path}; download it from {source.url}")
		items = PARSERS[source.layout](pdf_lines(path))
		sha = hashlib.sha256(path.read_bytes()).hexdigest()
		print(f"{source.file}: {len(items)} questions  sha256={sha[:16]}")
		for item in items:
			options = (item["options"] + ["", "", "", ""])[:4]
			rows_out.append(
				{
					"question_id": f"{source.year}-{source.session[:3].lower()}-{source.part}-q{item['number']:03d}",
					"year": source.year,
					"session": source.session,
					"part": source.part,
					"provider": "PrepLadder",
					"completeness": source.completeness,
					"source_file": source.file,
					"source_question_number": item["number"],
					"source_page": item["page"],
					"provider_subject": item["subject"],
					"provider_topic": item["topic"],
					"stem": item["stem"],
					"option_a": options[0],
					"option_b": options[1],
					"option_c": options[2],
					"option_d": options[3],
					"provider_answer": item["answer"],
					"provider_image": "",
				}
			)
	rows_out += fmgeprep_rows()
	with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
		writer = csv.DictWriter(handle, fieldnames=FIELDS)
		writer.writeheader()
		writer.writerows(rows_out)
	print(f"Wrote {len(rows_out)} questions to {OUTPUT}")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
