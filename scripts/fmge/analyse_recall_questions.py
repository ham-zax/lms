#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["scikit-learn>=1.4", "numpy>=1.26"]
# ///
"""Classify the extracted FMGE recall questions and write the measured pattern statistics.

Reads the local full-text CSV from extract_recall_questions.py and writes two
committed, text-free outputs:

- research/fmge-source-material/extracted/question-patterns.csv  (one row per question)
- research/fmge-source-material/analysis/recall-pattern-stats.md  (tables)

    uv run scripts/fmge/analyse_recall_questions.py
"""

from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_predict

ROOT = Path(__file__).resolve().parents[2]
RESEARCH = ROOT / "research/fmge-source-material"
FULL_CSV = RESEARCH / "corpus/recall-questions-full.csv"
PATTERNS_CSV = RESEARCH / "extracted/question-patterns.csv"
STATS_MD = RESEARCH / "analysis/recall-pattern-stats.md"

# Provider subject label -> NBEMS blueprint subject.
SUBJECT_MAP = {
	"Anatomy": "Anatomy",
	"Physiology": "Physiology",
	"Biochemistry": "Biochemistry",
	"Pathology": "Pathology",
	"Microbiology": "Microbiology",
	"Pharmacology": "Pharmacology",
	"Forensic Medicine": "Forensic Medicine",
	"Medicine": "Medicine",
	"Psychiatry": "Psychiatry",
	"Dermatology": "Dermatology",
	"Surgery": "General Surgery",
	"Anaesthesia": "Anaesthesiology",
	"Orthopaedics": "Orthopaedics",
	"Radiology": "Radiology (diagnosis + therapy)",
	"Pediatrics": "Paediatrics",
	"Paediatrics": "Paediatrics",
	"Ophthalmology": "Ophthalmology",
	"ENT": "ENT",
	"Gynaecology & Obstetrics": "Obstetrics & Gynaecology",
	"PSM": "Community Medicine",
	"Community Medicine": "Community Medicine",
}
# NBEMS June 2026 bulletin, marks out of 300 (radiodiagnosis 5 + radiotherapy 5 combined,
# because providers label both as Radiology).
BLUEPRINT = {
	"Anatomy": 17,
	"Physiology": 17,
	"Biochemistry": 17,
	"Pathology": 13,
	"Microbiology": 13,
	"Pharmacology": 13,
	"Forensic Medicine": 10,
	"Medicine": 33,
	"Psychiatry": 5,
	"Dermatology": 5,
	"General Surgery": 32,
	"Anaesthesiology": 5,
	"Orthopaedics": 5,
	"Radiology (diagnosis + therapy)": 10,
	"Paediatrics": 15,
	"Ophthalmology": 15,
	"ENT": 15,
	"Obstetrics & Gynaecology": 30,
	"Community Medicine": 30,
}

IMAGE_RE = re.compile(
	r"\b(?:image|images|picture|photo(?:graph)?|shown|depicted|given below|as below|below image|marked (?:with|by|as|in|area|structure|part)|labell?ed|given (?:condition|image|picture|specimen|instrument)"
	r"|figure|spot(?: the| this)?|identify(?: the| this)? (?:instrument|structure|condition|procedure|fracture|lesion"
	r"|sign|organism|image|device|specimen|bone|muscle|nerve|artery|finding|disease|tumou?r|appliance)"
	r"|instrument|ecg (?:is |was )?(?:shown|given|below)|x-?ray (?:is |was )?(?:shown|given|below))\b",
	re.IGNORECASE,
)
NEGATIVE_RE = re.compile(
	r"\bEXCEPT\b|\bexcept\b|\bNOT\b|\bfalse\b|\bincorrect\b|\buntrue\b|\bwrong\b"
	r"|\bnot (?:true|correct|a|an|seen|associated|used|found|included|indicated|given|done|part|feature|cause"
	r"|recommended|advised|present|required|characteristic|typical)\b",
)
VIGNETTE_RE = re.compile(
	r"\b\d+[- ]?(?:year|yr|month|day|week)s?[- ]?old\b|\bpatient\b|\bpresents?\b|\bpresented\b|\bcomplain"
	r"|\bbrought\b|\badmitted\b|\bhistory of\b|\bon examination\b|\bexamination (?:shows|reveals)\b"
	r"|\ba (?:young |pregnant |middle-aged |old |elderly )?(?:man|woman|male|female|child|boy|girl|neonate|newborn"
	r"|baby|infant|lady|gentleman|farmer|worker|primigravida|multigravida)\b|\bG\dP\d",
	re.IGNORECASE,
)
CALC_RE = re.compile(
	r"calculat|how (?:much|many)|compute|sensitivity|specificity|predictive value|prevalence|incidence rate"
	r"|standard deviation|\bmean\b|\bmedian\b|\bratio\b|\brate\b|dose of|ml of|percentage",
	re.IGNORECASE,
)
# Primary task, judged on the lead-in (last sentence), first match wins.
TASKS = [
	(
		"management",
		r"manag|treat|drug of choice|next (?:best )?step|line of|therapy|surgery of choice|procedure of choice"
		r"|antidote|first[- ]line|immediate|intervention|best approach|advis|done next|to be given|should be given"
		r"|what (?:should|will) (?:be|you) do|prescribe|operat",
	),
	(
		"investigation",
		r"investigation|\btest\b|diagnostic|confirm|screening|gold standard|imaging|medium|stain|interpret"
		r"|will be seen|finding|expected|level|\bseen\b|\bshow\b|lab",
	),
	(
		"diagnosis",
		r"diagnosis|most likely|probable|identify|spot|what is (?:this|the condition)|condition|type of|name of"
		r"|which (?:disease|syndrome|organism|tumou?r|fracture|lesion)|suffering",
	),
	(
		"mechanism",
		r"mechanism|cause|due to|because|pathogenesis|why|responsible|mediated|action|receptor|enzyme|deficien",
	),
	("anatomy", r"nerve|artery|vein|muscle|injur|damage|structure|suppl|drain|site|located|localiz|level of"),
]
TASK_RES = [(name, re.compile(pattern, re.IGNORECASE)) for name, pattern in TASKS]

# Model subject predictions at or above this probability are treated as usable (see the printed check).
CONFIDENT = 0.2

FIELDS = [
	"question_id",
	"year",
	"session",
	"part",
	"provider",
	"completeness",
	"source_question_number",
	"subject",
	"subject_method",
	"subject_confidence",
	"stem_words",
	"stem_type",
	"task",
	"image_based",
	"negative_stem",
	"clinical_vignette",
	"calculation",
	"provider_answer",
	"duplicate_of",
	"repeat_of_earlier_sitting",
]


def lead_in(stem: str) -> str:
	sentences = [s for s in re.split(r"(?<=[.?:])\s+", stem.strip()) if s]
	return sentences[-1] if sentences else stem


def classify(row: dict) -> dict:
	stem = row["stem"]
	words = len(stem.split())
	image = IMAGE_RE.search(stem) is not None or row.get("provider_image") == "yes"
	vignette = VIGNETTE_RE.search(stem) is not None
	numbers = len(re.findall(r"\d+(?:\.\d+)?", stem))
	calculation = numbers >= 2 and CALC_RE.search(stem) is not None
	final = lead_in(stem)
	task = next((name for name, pattern in TASK_RES if pattern.search(final)), "")
	if not task:
		task = next((name for name, pattern in TASK_RES if pattern.search(stem)), "fact recall")
	if calculation:
		task = "calculation"
	if image:
		stem_type = "image-led"
	elif vignette:
		stem_type = "clinical vignette"
	elif words <= 15:
		stem_type = "one-liner"
	else:
		stem_type = "direct (longer)"
	return {
		"stem_words": words,
		"stem_type": stem_type,
		"task": task,
		"image_based": "yes" if image else "no",
		"negative_stem": "yes" if NEGATIVE_RE.search(stem) else "no",
		"clinical_vignette": "yes" if vignette else "no",
		"calculation": "yes" if calculation else "no",
	}


def tokens(text: str) -> set[str]:
	return {t for t in re.findall(r"[a-z0-9]+", text.lower()) if len(t) > 2}


def jaccard(a: set[str], b: set[str]) -> float:
	return len(a & b) / len(a | b) if a and b else 0.0


def sitting(row: dict) -> str:
	return f"{row['year']} {row['session']}"


def main() -> int:
	with FULL_CSV.open(encoding="utf-8") as handle:
		rows = list(csv.DictReader(handle))

	texts = [f"{r['stem']} {r['option_a']} {r['option_b']} {r['option_c']} {r['option_d']}" for r in rows]
	token_sets = [tokens(t) for t in texts]

	# Subject: provider label where present, otherwise a text classifier trained on the labelled rows.
	labelled = [i for i, r in enumerate(rows) if r["provider_subject"] in SUBJECT_MAP]
	y = np.array([SUBJECT_MAP[rows[i]["provider_subject"]] for i in labelled])
	vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1, sublinear_tf=True, stop_words="english")
	x_all = vectorizer.fit_transform(texts)
	model = LogisticRegression(max_iter=3000, C=8, class_weight="balanced")
	cv_proba = cross_val_predict(model, x_all[labelled], y, cv=5, method="predict_proba")
	classes = np.unique(y)
	cv_pred = classes[cv_proba.argmax(axis=1)]
	cv_accuracy = float((cv_pred == y).mean())
	confident = cv_proba.max(axis=1) >= CONFIDENT
	confident_accuracy = float((cv_pred[confident] == y[confident]).mean()) if confident.any() else 0.0
	confident_share = float(confident.mean())
	model.fit(x_all[labelled], y)
	proba = model.predict_proba(x_all)
	predicted = model.classes_[proba.argmax(axis=1)]
	confidence = proba.max(axis=1)

	# Duplicates: FMGEPrep samples that are the same recalled item as a PrepLadder question.
	prepladder = [i for i, r in enumerate(rows) if r["provider"] == "PrepLadder"]
	duplicate_of: dict[int, str] = {}
	session_matches: dict[str, Counter] = defaultdict(Counter)
	for i, r in enumerate(rows):
		if r["provider"] != "FMGEPrep":
			continue
		best, best_j = None, 0.0
		for j in prepladder:
			score = jaccard(token_sets[i], token_sets[j])
			if score > best_j:
				best, best_j = j, score
		if best is not None and best_j >= 0.55:
			duplicate_of[i] = rows[best]["question_id"]
			session_matches[f"FMGEPrep {sitting(r)}"][f"PrepLadder {sitting(rows[best])}"] += 1

	# Repeats: a PrepLadder question that closely matches one from an earlier sitting.
	repeat_of: dict[int, str] = {}
	order = sorted(prepladder, key=lambda i: (int(rows[i]["year"]), rows[i]["session"]))
	for position, i in enumerate(order):
		for j in order[:position]:
			if sitting(rows[j]) == sitting(rows[i]):
				continue
			if jaccard(token_sets[i], token_sets[j]) >= 0.6:
				repeat_of[i] = rows[j]["question_id"]
				break

	out = []
	for i, r in enumerate(rows):
		provider_subject = r["provider_subject"]
		features = classify(r)
		out.append(
			{
				"question_id": r["question_id"],
				"year": r["year"],
				"session": r["session"],
				"part": r["part"],
				"provider": r["provider"],
				"completeness": r["completeness"],
				"source_question_number": r["source_question_number"],
				"subject": SUBJECT_MAP.get(provider_subject, predicted[i]),
				"subject_method": "provider label" if provider_subject in SUBJECT_MAP else "model",
				"subject_confidence": "1.00" if provider_subject in SUBJECT_MAP else f"{confidence[i]:.2f}",
				**features,
				"provider_answer": r["provider_answer"],
				"duplicate_of": duplicate_of.get(i, ""),
				"repeat_of_earlier_sitting": repeat_of.get(i, ""),
			}
		)
	PATTERNS_CSV.parent.mkdir(parents=True, exist_ok=True)
	with PATTERNS_CSV.open("w", newline="", encoding="utf-8") as handle:
		writer = csv.DictWriter(handle, fieldnames=FIELDS)
		writer.writeheader()
		writer.writerows(out)

	# Image-detector check against FMGEPrep's own image flag.
	fp = [(r, o) for r, o in zip(rows, out, strict=True) if r["provider"] == "FMGEPrep"]
	truth = [r["provider_image"] == "yes" for r, _ in fp]
	guess = [IMAGE_RE.search(r["stem"]) is not None for r, _ in fp]
	tp = sum(t and g for t, g in zip(truth, guess, strict=True))
	image_recall = tp / max(1, sum(truth))
	image_precision = tp / max(1, sum(guess))

	STATS_MD.write_text(
		render_stats(
			out, cv_accuracy, len(labelled), image_recall, image_precision, sum(truth), session_matches
		),
		encoding="utf-8",
	)
	print(f"Wrote {len(out)} rows to {PATTERNS_CSV}")
	print(f"Subject model 5-fold accuracy {cv_accuracy:.1%} on {len(labelled)} labelled questions")
	print(
		f"  at confidence >= {CONFIDENT}: accuracy {confident_accuracy:.1%} on {confident_share:.0%} of questions"
	)
	print(f"Image detector vs FMGEPrep flag: recall {image_recall:.0%}, precision {image_precision:.0%}")
	print(f"Wrote {STATS_MD}")
	return 0


def pct(part: int, whole: int) -> str:
	return f"{100 * part / whole:.0f}%" if whole else "-"


def render_stats(
	out, cv_accuracy, n_labelled, image_recall, image_precision, n_images, session_matches
) -> str:
	primary = [o for o in out if o["provider"] == "PrepLadder"]
	groups: dict[str, list[dict]] = defaultdict(list)
	for o in primary:
		groups[f"{o['year']} {o['session']}"].append(o)
	full = {k: v for k, v in groups.items() if v[0]["completeness"] == "full"}
	samples_2124 = [o for o in out if o["provider"] == "FMGEPrep" and int(o["year"]) <= 2025]
	fmgeprep_2026 = [o for o in out if o["provider"] == "FMGEPrep" and int(o["year"]) == 2026]

	def summary_row(label, items):
		n = len(items)
		c = Counter(o["stem_type"] for o in items)
		return (
			f"| {label} | {n} | {median(int(o['stem_words']) for o in items):.0f} "
			f"| {pct(c['one-liner'], n)} | {pct(c['direct (longer)'], n)} | {pct(c['clinical vignette'], n)} "
			f"| {pct(c['image-led'], n)} | {pct(sum(o['negative_stem'] == 'yes' for o in items), n)} "
			f"| {pct(sum(o['calculation'] == 'yes' for o in items), n)} |"
		)

	lines = [
		"# FMGE recall pattern statistics (generated)",
		"",
		"Generated by `scripts/fmge/analyse_recall_questions.py` from the local recall corpus. "
		"Do not edit by hand; rerun the script.",
		"",
		"## Corpus",
		"",
		"| Sitting (provider label) | Provider | Questions | Completeness |",
		"| --- | --- | --- | --- |",
	]
	for key in sorted(groups):
		items = groups[key]
		lines.append(f"| {key} | PrepLadder | {len(items)} | {items[0]['completeness']} |")
	lines += [
		f"| 2021-2025 (18 paper parts) | FMGEPrep public samples | {len(samples_2124)} | sample (10 per part) |",
		f"| 2026 (4 paper parts) | FMGEPrep public samples | {len(fmgeprep_2026)} | sample (10 per part) |",
		"",
		"## Stem form by sitting",
		"",
		"Stem type is exclusive: image-led, else clinical vignette, else one-liner (<= 15 words), else longer direct. "
		"Negative and calculation overlap with it.",
		"",
		"| Sitting | n | Median words | One-liner | Direct (longer) | Clinical vignette | Image-led | Negative | Calculation |",
		"| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
	]
	for key in sorted(groups):
		lines.append(summary_row(key, groups[key]))
	all_full = [o for v in full.values() for o in v]
	lines.append(summary_row("**All full sittings**", all_full))
	lines.append(summary_row("FMGEPrep samples 2021-2025", samples_2124))
	lines.append(summary_row("FMGEPrep samples 2026", fmgeprep_2026))

	tasks = ["fact recall", "diagnosis", "investigation", "management", "mechanism", "anatomy", "calculation"]
	lines += [
		"",
		"## Task tested (primary, from the lead-in)",
		"",
		"| Sitting | n | " + " | ".join(t.title() for t in tasks) + " |",
		"| --- | --- | " + " | ".join("---" for _ in tasks) + " |",
	]
	for key in sorted(groups):
		items = groups[key]
		c = Counter(o["task"] for o in items)
		lines.append(f"| {key} | {len(items)} | " + " | ".join(pct(c[t], len(items)) for t in tasks) + " |")
	c = Counter(o["task"] for o in all_full)
	lines.append(
		f"| **All full sittings** | {len(all_full)} | "
		+ " | ".join(pct(c[t], len(all_full)) for t in tasks)
		+ " |"
	)

	vign = [o for o in all_full if o["clinical_vignette"] == "yes"]
	cv = Counter(o["task"] for o in vign)
	lines += [
		"",
		f"Clinical vignettes in full sittings ({len(vign)}) ask for: "
		+ ", ".join(f"{t} {pct(cv[t], len(vign))}" for t in tasks if cv[t])
		+ ".",
		"",
		"## Subject mix of full sittings vs NBEMS blueprint",
		"",
		f"Only sittings with provider subject labels are shown. 2025 recalls carry no subject label, and a text "
		f"classifier trained on the {n_labelled} labelled questions reached only {cv_accuracy:.0%} cross-validated "
		"accuracy, so 2025 subject counts are not reported (the per-question CSV keeps the prediction, marked "
		"`model`).",
		"",
	]
	keys = sorted(k for k in full if full[k][0]["subject_method"] == "provider label")
	lines.append("| Subject | Blueprint /300 | " + " | ".join(f"{k} (per 300)" for k in keys) + " |")
	lines.append("| --- | --- | " + " | ".join("---" for _ in keys) + " |")
	per_sitting = {k: Counter(o["subject"] for o in full[k]) for k in keys}
	for subject, marks in BLUEPRINT.items():
		cells = []
		for k in keys:
			n = len(full[k])
			cells.append(f"{300 * per_sitting[k][subject] / n:.0f}")
		lines.append(f"| {subject} | {marks} | " + " | ".join(cells) + " |")

	labelled_rows = [o for o in primary if o["subject_method"] == "provider label"]
	by_subject: dict[str, list[dict]] = defaultdict(list)
	for o in labelled_rows:
		by_subject[o["subject"]].append(o)
	lines += [
		"",
		f"## Subject profiles (provider-labelled questions, 2021-2024, n={len(labelled_rows)})",
		"",
		"| Subject | n | Median words | One-liner | Vignette | Image-led | Negative | Calculation | Diagnosis | Management "
		"| Investigation | Fact recall |",
		"| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
	]
	for subject in sorted(by_subject, key=lambda s: -len(by_subject[s])):
		items = by_subject[subject]
		n = len(items)
		st = Counter(o["stem_type"] for o in items)
		tk = Counter(o["task"] for o in items)
		lines.append(
			f"| {subject} | {n} | {median(int(o['stem_words']) for o in items):.0f} | {pct(st['one-liner'], n)} "
			f"| {pct(st['clinical vignette'], n)} | {pct(st['image-led'], n)} "
			f"| {pct(sum(o['negative_stem'] == 'yes' for o in items), n)} "
			f"| {pct(sum(o['calculation'] == 'yes' for o in items), n)} | {pct(tk['diagnosis'], n)} "
			f"| {pct(tk['management'], n)} | {pct(tk['investigation'], n)} | {pct(tk['fact recall'], n)} |"
		)

	words = sorted(int(o["stem_words"]) for o in all_full)
	vignette_words = sorted(int(o["stem_words"]) for o in all_full if o["stem_type"] == "clinical vignette")
	lines += [
		"",
		"## Stem length (all full sittings)",
		"",
		f"- All stems: median {median(words):.0f} words, 90th percentile {words[int(0.9 * len(words))]}, "
		f"95th percentile {words[int(0.95 * len(words))]}.",
		f"- Clinical vignettes: median {median(vignette_words):.0f} words, 90th percentile "
		f"{vignette_words[int(0.9 * len(vignette_words))]}.",
	]

	lines += [
		"",
		"## Answer key balance (provider keys, full sittings)",
		"",
		"| Sitting | A | B | C | D |",
		"| --- | --- | --- | --- | --- |",
	]
	for key in keys:
		c = Counter(o["provider_answer"] for o in full[key])
		n = len(full[key])
		lines.append(f"| {key} | " + " | ".join(pct(c[letter], n) for letter in "ABCD") + " |")

	repeats = [o for o in primary if o["repeat_of_earlier_sitting"]]
	lines += [
		"",
		"## Repeats across sittings",
		"",
		f"{len(repeats)} of {len(primary)} PrepLadder questions ({pct(len(repeats), len(primary))}) closely match a "
		"question from an earlier sitting (word-set similarity >= 0.6 on stem + options).",
		"",
		"| Sitting | Questions | Close repeats of an earlier sitting |",
		"| --- | --- | --- |",
	]
	for key in sorted(groups):
		items = groups[key]
		k = sum(bool(o["repeat_of_earlier_sitting"]) for o in items)
		lines.append(f"| {key} | {len(items)} | {k} ({pct(k, len(items))}) |")

	lines += [
		"",
		"## Cross-provider overlap",
		"",
		"FMGEPrep sample questions that match a PrepLadder question (similarity >= 0.55):",
		"",
		"| FMGEPrep sitting | Matched PrepLadder sitting(s) |",
		"| --- | --- |",
	]
	for key in sorted(session_matches):
		lines.append(
			f"| {key} | " + ", ".join(f"{k} ({v})" for k, v in session_matches[key].most_common()) + " |"
		)

	lines += [
		"",
		"## Method checks",
		"",
		f"- Subject classifier: 5-fold accuracy {cv_accuracy:.0%} on {n_labelled} provider-labelled questions.",
		f"- Image detector (stem wording) against FMGEPrep's own image flag on {n_images} flagged samples: "
		f"recall {image_recall:.0%}, precision {image_precision:.0%}. Recall PDFs describe the image in the stem "
		'("image given below"), which is what the detector reads.',
		"- Stem type, task, negative and calculation are rule-based on the stem text; see the regexes in the script.",
		"",
	]
	return "\n".join(lines)


if __name__ == "__main__":
	raise SystemExit(main())
