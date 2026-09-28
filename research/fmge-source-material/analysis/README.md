# FMGE pattern analysis

This directory contains derived research, not source papers.

Historical pattern-calibration window: **2021-2025**. The separate research/discovery window is **2022-2026**.

Current outputs:

- `five-year-pattern-report.md` - evidence-bounded qualitative pattern extraction; each year section states when evidence is only a preview/discovery lead rather than an inspected full recall.
- `recall-pattern-stats.md` - generated tables from 1,821 extracted recall questions (`scripts/fmge/analyse_recall_questions.py`).
- `psm-block-1-review.md` - manual FMGE style/correctness review of the live PSM Block 1.
- `prompt-calibration.md` - current (v7) FMGE PDF-to-question-bank master prompt, calibrated from that pattern and from the first generated block; its output format is parsed by `scripts/fmge/build_question_bank.py`.

Structured outputs:

- `../extracted/question-patterns.csv` - one text-free row per recalled question (sitting, subject, stem form, task, image, negative, calculation, duplicates, repeats).
- `../corpus/recall-questions-full.csv` - full question text; local and gitignored (third-party recall material).

Pattern calculations should explicitly state their denominator and exclude samples, mirrors and incomplete sources when a whole-paper percentage would otherwise be misleading.
