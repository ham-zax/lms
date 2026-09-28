# FMGE source material research

This folder contains legally safe source material and a research index for building the FMGE-style examination experience.

## Important limitation: official past question papers are not released

NBEMS states that FMGE examination content is confidential, proprietary, and owned by NBEMS. Its published non-disclosure terms prohibit reproducing, transmitting, or publishing examination content, and NBEMS says it will not provide the examination content or answer keys.

Because of that, third-party "previous year paper" PDFs reconstructed from candidate recall are treated as **unofficial research sources**, not official FMGE papers. This repository does not automatically mirror them from provider sites. If a source document is legitimately available for local analysis, it belongs under `corpus/` with its provenance recorded in the manifests.

Official references:

- FMGE exam portal/current-session index (verified 2026-09-28; lists October 2026): https://www.natboard.edu.in/viewnbeexam?exam=fmge
- FMGE June 2026 Information Bulletin: https://nbe.edu.in/IB/FMGE%20JUNE%202026%20information%20bulletin.pdf
- FMGE December 2024 Information Bulletin (time-bound sections): https://natboard.edu.in/viewUpload?xyz=cUtIMVEvdzBwS1QzQXBtRjZPUzR4QT09
- FMGE December 2023 Information Bulletin (contains the NDA language): https://natboard.edu.in/viewUpload?xyz=a2lIYW44SEp1N01TSlNNcmU5cGp0QT09
- NBEMS 2021 notice on requests for FMGE question papers/answer keys: https://natboard.edu.in/viewNotice.php?NBE=bFYyZHZ5TnNWc3R2TkFuTGVIUnVhdz09

## Official PDF stored here

The `official/` directory currently contains:

- `FMGE_June_2026_Information_Bulletin.pdf` - the locally archived official June 2026 examination scheme, syllabus/blueprint, timing and candidate instructions. As verified on 2026-09-28, the NBEMS FMGE portal lists October 2026 as the current session.

Historical official bulletins remain linked from the NBEMS sources above rather than being treated as question papers.

This is **not a question paper**. It is an implementation/reference document published by NBEMS.

## Layout

- `official/` - authoritative NBEMS reference documents.
- `manifests/` - source discovery, provenance, quality classes, aliases and local-asset inventory.
- `corpus/2022/` ... `corpus/2026/` - locally available recall source documents for the 2022-2026 research/discovery window; `corpus/2021/` remains available for the separate historical calibration view.
- `extracted/` - normalized question-level extraction schema/data.
- `analysis/` - derived counts, trends and prompt-calibration findings.

[`manifests/local-assets.csv`](manifests/local-assets.csv) is the authoritative inventory of PDF/files actually present locally.

## Research/discovery window: 2022-2026

The working **research/discovery** catalog is [`manifests/paper-catalog-2022-2026.csv`](manifests/paper-catalog-2022-2026.csv). It records the publicly located recall-paper resources from FMGEPrep, Careers360, NEETFMGE Plans and PrepLadder and assigns an evidence class based on what has actually been checked. The catalog records source links, not imported questions or answers.

[`manifests/paper-catalog-2021-2025.csv`](manifests/paper-catalog-2021-2025.csv) is the **historical pattern-calibration window** used by the five-year report and prompt calibration. It is distinct from the 2022-2026 research/discovery window. Neither catalog establishes a whole-paper denominator until the underlying source has been inspected for completeness and duplicate questions.

Important supporting files:

- [`manifests/source-quality-rubric.md`](manifests/source-quality-rubric.md) - grades official, full recall, sample, mirror and landing-page sources.
- [`manifests/session-aliases-2022-2026.csv`](manifests/session-aliases-2022-2026.csv) - preserves provider month labels in the research/discovery window and marks possible June/July or December/January aliases for later fingerprint verification.
- [`analysis/session-source-findings-2026-09-28.md`](analysis/session-source-findings-2026-09-28.md) - facts added from the current research session, including the verified PrepLadder December 2021 direct-PDF URL.
- [`extracted/question-schema.md`](extracted/question-schema.md) - the per-question classification schema used for pattern extraction.

FMGEPrep sample pages are treated as examples rather than whole-paper denominators. The 2022 and 2023 NEETFMGE Plans PDFs are byte-identical to the corresponding PrepLadder PDFs and are not counted as independent recalls. The 2024 and 2025 NEETFMGE Plans PDFs have not been verified as mirrors.

Provider terms and permissions still matter. A public download URL is provenance, not automatic permission to republish the material.

## Ten-year search index: 2017-2026

| Year | Official FMGE question paper publicly released? | Public material located in research | Repository action |
| --- | --- | --- | --- |
| 2017 | No | Candidate-recall videos/blog material located | Not copied |
| 2018 | No | Memory-based/reconstructed paper listings located | Not copied |
| 2019 | No | Memory-based/reconstructed paper listings located | Not copied |
| 2020 | No | Memory-based/reconstructed paper listings located | Not copied |
| 2021 | No | Memory-based paper listings located; NBEMS separately reiterated that papers/answer keys are not released | Not copied |
| 2022 | No | Memory-based/reconstructed paper listings located | Not copied |
| 2023 | No | Memory-based/reconstructed paper listings located | Not copied |
| 2024 | No | Memory-based/reconstructed paper listings located | Not copied |
| 2025 | No | Memory-based/reconstructed paper listings located | Not copied |
| 2026 | No | Memory-based Jan/June recall listings located | Not copied |

## Research landing pages found

These are listed for provenance/research only. They are not treated as official NBEMS papers and their PDF contents have not been copied into this repository.

- Careers360 FMGE previous-year papers: https://medicine.careers360.com/articles/fmge-question-paper
- Careers360 2024 page: https://medicine.careers360.com/articles/fmge-question-paper-2024
- PrepLadder FMGE previous-year papers: https://www.prepladder.com/fmge-study-material/previous-years-question-papers/fmge-previous-year-question-papers
- DocTutorials FMGE previous-year papers: https://www.doctutorials.com/blog/fmge/fmge-previous-year-question-papers
- GetMyUni previous-year papers: https://www.getmyuni.com/exams/fmge-previous-years-papers

For 2017, recall material also appears in older educational blogs/videos, but it is still recall-based rather than an official released paper.

## Provider / recall catalog

See `manifests/provider-resources.md` and `manifests/provider-resources.csv` for public recall sessions and sample-resource pages from Cerebellum Academy, PrepLadder, Marrow, Careers360, and DBMCI.

## What to use for question generation

When generating our own FMGE-style bank, use:

1. the official NBEMS syllabus and exam blueprint;
2. user-provided medical source PDFs/textbooks/notes for which we have permission to process;
3. independently authored questions that match the FMGE format and difficulty;
4. images/diagrams that we are permitted to use.

Do not label reconstructed recall questions as "official FMGE questions."
