# FMGE pattern analysis

This directory contains derived research, not source papers.

Historical pattern-calibration window: **2021-2025**. The separate research/discovery window is **2022-2026**.

Current outputs:

- `five-year-pattern-report.md` - evidence-bounded qualitative pattern extraction; each year section states when evidence is only a preview/discovery lead rather than an inspected full recall.
- `recall-pattern-stats.md` - generated tables from 1,821 extracted recall questions (`scripts/fmge/analyse_recall_questions.py`).
- `psm-block-1-review.md` - manual FMGE style/correctness review of the live PSM Block 1.
- [prompt-calibration.md](prompt-calibration.md) — generation prompt v9.6, preserving the measured subject profiles, real-question gallery and parser contract. Bank size is every distinct eligible High/Medium source-supported unit; topic/pattern variety guides section arrangement and mock selection rather than cutting bank coverage. It plans first, stops for “go”, and delivers sections of at most 50. v9.6 adds a page sweep and count equation to the plan, chronological date options, a keep-published-layout rule and a no-unsupported-figures rule for explanations.
- [prompt-review.md](prompt-review.md) — self-contained second-pass reviewer v1.2. Supply the same source PDF, the entire draft (inventory, sections, keys, audits and ledgers), and any earlier-bank exclusion ledger. It corrects source/truth failures, ambiguity, tier inflation, decorative images, answer cycles and stale audit counts, sweeps the PDF page by page for uninventoried units, recomputes the coverage count equation, then returns the full corrected text bank and image-requirements handoff with text readiness and unresolved checks.

- [prompt-paper-creator.md](prompt-paper-creator.md) — third-pass assembler. Supply the reviewed text, source PDF, review report and image requirements. It crops/masks authentic source images or verifies faithful schematic redraws, fills placeholders with real assets, selects a mock without deleting bank coverage, and delivers separate student/staff files with build and render checks.

Use **calibration → review → paper creation**. The first two passes return text and image placeholders; only the third produces and inspects assets. Text readiness and paper readiness are separate. A text-only third pass returns an assembly specification with missing capabilities, not a finished paper. The second pass can use established knowledge and ChatGPT search for uncertain or dynamic claims, but external facts cannot silently enter the PDF-only bank. Missing source evidence keeps review provisional. Neither prompt guarantees perfect verification; `scripts/fmge/build_question_bank.py` remains the local format/style check.

Structured outputs:

- `../extracted/question-patterns.csv` - one text-free row per recalled question (sitting, subject, stem form, task, image, negative, calculation, duplicates, repeats).
- `../corpus/recall-questions-full.csv` - full question text; local and gitignored (third-party recall material).

Pattern calculations should explicitly state their denominator and exclude samples, mirrors and incomplete sources when a whole-paper percentage would otherwise be misleading.
