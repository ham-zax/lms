# Recall corpus

Research/discovery window: **2022-2026**. The `2021/` directory is supplemental to that discovery window but remains part of the separate **2021-2025 historical pattern-calibration window**.

This directory is for local source documents that are actually available for analysis. A URL in a manifest is not a corpus file.

Suggested filename convention:

`<canonical-session>__<provider>__<part-or-full>.<ext>`

Examples:

- `2021-12__prepladder__full.pdf`
- `2025-01__prepladder__part-1.pdf`

## Current status

The PrepLadder recall PDFs (Dec 2021, Jun 2022, Jan 2023, Jan/Jun 2024 selections, Jan/Jul 2025 Parts 1-2) are downloaded here for local analysis, together with cached FMGEPrep sample pages (`fmgeprep/`) and the extracted full-text `recall-questions-full.csv`. All of these are **gitignored**: they are third-party recall material and are never committed. Rebuild them with:

    uv run scripts/fmge/extract_recall_questions.py --fetch   # needs the PDFs listed in the script
    uv run scripts/fmge/analyse_recall_questions.py

Only the text-free `../extracted/question-patterns.csv` and the analysis files are committed.


When a recall document is added with permission to store it, record its provenance in `../manifests/paper-catalog-2022-2026.csv` and mark `corpus_status=local`.

Do not treat recall material as official NBEMS papers.
