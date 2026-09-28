# Session source findings - 2026-09-28

These are research observations established during the ChatGPT session and not binary PDF assets.

## Target windows

Research/discovery window: **2022-2026**.

Historical pattern-calibration window: **2021-2025**. Thus 2021 is supplemental to the discovery window but part of the five-year historical calibration window.

The 2026 official bulletin describes the current exam blueprint. The 2026 recall links belong to the research/discovery window, but their public samples and landing pages cannot supply a whole-paper denominator.

## Added from this session

- PrepLadder publicly lists a December 2021 recall paper.
- Verified direct PDF URL: https://image.prepladder.com/content/FMGE-dec-2021-pyq-pdf.pdf
- PrepLadder's hub also lists June 2022, January 2023, January/June 2024 and January/July 2025 recall resources.
- FMGEPrep entries in the existing manifest are public previews, generally 10 visible sample questions per part with fuller practice gated. Those samples are useful for examples but not a defensible whole-paper denominator.
- The NEETFMGE Plans 2022 PDF is already recorded in the repository research as byte-identical to the PrepLadder 2022 PDF. It must not be counted as an independent recall source.
- The NEETFMGE Plans 2023 PDF and the PrepLadder January 2023 PDF are byte-identical (SHA-256 `96e15362155e555b80479680109695f9d5a6f05ef6866cb37c481fa6d570b14a`). The 2024 and 2025 NEETFMGE Plans PDFs remain unverified as mirrors.
- Month labels across providers may differ around the same exam cycle (for example December/January and June/July). Do not collapse them until question fingerprints or exam-date evidence establish equivalence.
- Careers360 describes the material as memory-based/reconstructed rather than an official NBEMS release.

## Binary asset status

No third-party recall PDF binary is committed to this repository. The PrepLadder June 2022 PDF was first inspected through Khiip outside the repository; it is a 149-page provider recall document.

Later on 2026-09-28 all nine PrepLadder PDFs in the catalog were downloaded into `corpus/` for local analysis (gitignored, never committed) and 1,601 questions were extracted, plus 220 FMGEPrep public samples. NEETFMGE Plans 2024 and 2025 were confirmed as image-only copies of PrepLadder PDFs. See `five-year-pattern-report.md` and `recall-pattern-stats.md`.

The provenance data are captured in the manifests instead of being represented falsely as local corpus files.

## Recommended analysis order

Analyze the most recent complete material first:

1. 2026
2. 2025
3. 2024
4. 2023
5. 2022

Maintain session-level provenance and deduplicate mirrors before aggregate counting.
