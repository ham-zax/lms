# FMGE question-pattern report (2021-2025 calibration window)

## Evidence at a glance

This report is now **measured**. It rests on 1,499 recalled questions from five full sittings, plus provider samples, all extracted question by question on 2026-09-28.

| Sitting (provider label) | Source | Questions | Evidence class | Subject labels |
| --- | --- | --- | --- | --- |
| December 2021 | PrepLadder recall PDF, 155 pages | 300 | R1 | Yes |
| June 2022 | PrepLadder recall PDF, 149 pages | 300 | R1 | Yes |
| January 2023 | PrepLadder recall PDF, 144 pages (Q102 absent in source) | 299 | R1 | Yes |
| January 2024 | PrepLadder selection, 40 pages | 49 | R3 (provider selection) | Yes |
| June 2024 | PrepLadder selection, 38 pages | 53 | R3 (provider selection) | Yes |
| January 2025 | PrepLadder Part 1 + Part 2 PDFs | 300 | R1 | No |
| July 2025 | PrepLadder Part 1 + Part 2 PDFs | 300 | R1 | No |
| Jun 2021 - Jul 2025 (18 paper parts) | FMGEPrep public samples, 10 per part, with answer key and image flag | 180 | R3 | No |
| Jan and Jun 2026 (4 parts) | FMGEPrep public samples | 40 | R3 (discovery window only) | No |

Deduplication: the NEETFMGE Plans 2022/2023 PDFs are byte-identical to PrepLadder's. The 2024 and 2025 NEETFMGE PDFs are image-only copies of PrepLadder's 2024 selections and Jan 2025 Part 2 (R4). Only 29 of the 180 FMGEPrep samples match a PrepLadder question, so the two providers are largely independent reconstructions of the same sittings. The Scribd uploads could not be downloaded, and Careers360 offers no recall set, so neither contributed questions.

2024 has no full recall; its figures come from the two PrepLadder selections and FMGEPrep samples only.

Data and method:

- `scripts/fmge/extract_recall_questions.py` builds the full-text corpus. It stays local and gitignored (`corpus/recall-questions-full.csv`), because it is third-party recall material.
- `scripts/fmge/analyse_recall_questions.py` writes the committed, text-free `extracted/question-patterns.csv` and the full tables in [`recall-pattern-stats.md`](recall-pattern-stats.md).
- Stem form, task, negative and calculation labels are rule-based. A hand check of 27 random items found stem form correct in 27 and task correct in about 20 (~75%).
- The image detector reads the stem wording. Against FMGEPrep's own image flag it has 74% recall and 90% precision, so image shares below are slight underestimates.
- 2025 recalls carry no subject labels, and a text classifier reached only 51% accuracy, so **per-subject figures use the 1,001 labelled 2021-2024 questions only**.

Recalls are reconstructions: candidates remember stems better than options, and provider answer keys are not authoritative. Wording-level findings (stem form, length, lead-in) are more reliable than option-level ones.

## Official exam structure (NBEMS June 2026 bulletin, local copy)

Verified against `../official/FMGE_June_2026_Information_Bulletin.pdf` (sections 5 and 12):

- One paper of **300 MCQs**, given as two parts of **150 questions in 150 minutes** each on a single day.
- Each question has **4 response options**; the candidate selects the "correct / best / most appropriate" response.
- Each part is divided into **time-bound sections**. The bulletin's example is 3 sections of 50 questions in 50 minutes, with the number subject to change. A candidate cannot return to a closed section; Mark for Review works only inside the open section.
- **No negative marking.** Pass: at least 150/300.
- Syllabus: NMC Competency Based Undergraduate Curriculum.

| Pre- and para-clinical (100) | Marks | Clinical (200) | Marks |
| --- | --- | --- | --- |
| Anatomy | 17 | Medicine 33 + Psychiatry 5 + Dermatology & STD 5 + Radiotherapy 5 | 48 |
| Physiology | 17 | General Surgery 32 + Anaesthesiology 5 + Orthopaedics 5 + Radiodiagnosis 5 | 47 |
| Biochemistry | 17 | Obstetrics & Gynaecology | 30 |
| Pathology | 13 | Community Medicine | 30 |
| Microbiology | 13 | Paediatrics | 15 |
| Pharmacology | 13 | Ophthalmology | 15 |
| Forensic Medicine | 10 | Otorhinolaryngology | 15 |

The labelled 2021-2023 recalls track this blueprint within a few questions for most subjects. The exceptions are Surgery (41-46 per 300 in 2022-2023), OBG (40 in 2022) and Physiology (5-13), which differ from the blueprint. That may be a real deviation or provider labelling; generators should follow the official blueprint.

## Core findings

1. **FMGE is a mixed exam of short questions.** Across the five full sittings: 29% one-liners (15 words or fewer), 10% longer direct questions, 44% clinical vignettes and 17% image-led items (nearer 20% after detector correction). The median stem is 21 words; 95% of stems are under 55 words.
2. **Diagnosis is the most tested task (35%)**, then fact recall (28%), management (14%), investigation (11%), mechanism (8%), anatomy/localization (3%) and calculation (2%).
3. **Vignettes are mostly one-step.** Half of all vignettes ask for the diagnosis and a fifth ask for management. "Clues -> diagnosis -> next step" chains exist but are a minority.
4. **The stem form depends strongly on the subject.** This is the most useful finding for block generation (table below).
5. **Negative stems are rare**, about 5% (1-7% by sitting).
6. **Lead-ins are plain.** Plain direct questions ("What is…?", "Which drug…?") 37%, "Which of the following…" 24%, "…diagnosis?" 18%, "Identify/Spot…" 6%, negative 5%, "next (best) step" 3%, "most common" 3%, sentence completion 2%, "true about" 1%, "…of choice" 1%.
7. **Verbatim repeats are rare.** Only about 1% of questions closely repeat an earlier sitting's wording. Concepts recur, but the questions are re-written, so memorising old stems is not enough.
8. **Stems never refer to study material.** They do use named frameworks ("According to the biomedical waste guidelines…", "As per the MTP Act…").

### Stem form and task by subject (1,001 labelled questions, 2021-2024)

| Subject | n | Median words | One-liner | Vignette | Image-led | Negative | Diagnosis | Management | Fact recall |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| General Surgery | 123 | 25 | 23% | 51% | 20% | 9% | 34% | 21% | 24% |
| Medicine | 102 | 32 | 25% | 59% | 14% | 5% | 35% | 21% | 16% |
| Community Medicine | 100 | 15 | 50% | 22% | 2% | 7% | 9% | 9% | 63% |
| Obstetrics & Gynaecology | 93 | 14 | 40% | 33% | 20% | 10% | 24% | 17% | 41% |
| Anatomy | 56 | 12 | 20% | 12% | 61% | 0% | 36% | 0% | 29% |
| Biochemistry | 55 | 13 | 55% | 24% | 13% | 5% | 24% | 0% | 44% |
| Pharmacology | 54 | 20 | 39% | 46% | 13% | 6% | 17% | 31% | 24% |
| Pathology | 51 | 18 | 39% | 41% | 10% | 8% | 35% | 2% | 31% |
| Microbiology | 51 | 25 | 33% | 47% | 16% | 2% | 37% | 0% | 33% |
| Paediatrics | 47 | 21 | 30% | 53% | 13% | 6% | 32% | 11% | 38% |
| Ophthalmology | 45 | 28 | 13% | 53% | 29% | 2% | 49% | 22% | 9% |
| ENT | 44 | 30 | 23% | 57% | 14% | 5% | 43% | 16% | 18% |
| Forensic Medicine | 40 | 17 | 30% | 22% | 15% | 8% | 20% | 8% | 45% |
| Physiology | 32 | 13 | 69% | 16% | 3% | 0% | 12% | 0% | 44% |
| Radiology | 24 | 12 | 38% | 12% | 50% | 8% | 42% | 8% | 21% |
| Orthopaedics | 23 | 32 | 4% | 35% | 61% | 0% | 70% | 13% | 4% |
| Dermatology | 22 | 22 | 14% | 18% | 64% | 9% | 64% | 9% | 5% |
| Anaesthesiology | 22 | 16 | 41% | 32% | 14% | 5% | 14% | 14% | 59% |
| Psychiatry | 17 | 28 | 29% | 65% | 0% | 6% | 53% | 12% | 29% |

Three kinds of subject stand out:

- **Recall-heavy, short-stem subjects:** Community Medicine, Physiology, Biochemistry, Anaesthesiology.
- **Image-led subjects:** Anatomy, Dermatology, Orthopaedics, Radiology.
- **Vignette-led subjects:** Medicine, Psychiatry, ENT, Ophthalmology, Paediatrics.

Sample sizes for small subjects (fewer than 30 questions) are thin.

## Year-by-year pattern

| Sitting | Median words | One-liner | Vignette | Image-led | Negative | Diagnosis | Management | Fact recall |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Dec 2021 | 24 | 26% | 45% | 21% | 4% | 33% | 15% | 28% |
| Jun 2022 | 20 | 30% | 40% | 19% | 7% | 31% | 14% | 31% |
| Jan 2023 | 15 | 39% | 34% | 21% | 7% | 30% | 11% | 35% |
| Jan 2024 (selection) | 15 | 45% | 29% | 10% | 0% | 24% | 2% | 43% |
| Jun 2024 (selection) | 15 | 43% | 38% | 8% | 6% | 28% | 9% | 36% |
| Jan 2025 | 20 | 28% | 47% | 15% | 2% | 42% | 12% | 27% |
| Jul 2025 | 25 | 21% | 55% | 10% | 1% | 41% | 18% | 18% |
| FMGEPrep 2026 samples (n=40) | 32 | 2% | 62% | 30% | 0% | - | - | - |

Trend, with caution:

- **2025 moved towards clinical stems.** Vignettes rose to 47-55% (from 34-45%), diagnosis tasks to 41-42% (from 30-33%), direct recall fell (18% in July 2025), and stems got longer (median 25 words in July 2025).
- **The small 2026 samples continue this** (62% vignettes). 40 questions is too few to confirm it.
- **Image share is stable at about 10-21%.** It shows no clear rise; FMGEPrep's own flags give 25%, 20%, 15%, 8%, 15% and 23% for 2021-2026. Some 2025 image items may be missing from PrepLadder's reconstruction.
- **Negatives fell to 1-2% in 2025.**

Generator consequence: weight new banks toward the 2025 form, meaning more short clinical stems that ask diagnosis or management, while keeping about a quarter to a third of direct recall. Community Medicine and the other recall-heavy subjects remain mostly direct.

## Evidence-bounded generator DNA

These rules combine the measured pattern with single-best-answer item-writing practice.

1. **Four options, one best answer.** "Tricky" means close alternatives separated by a decisive clue, never real ambiguity.
2. **Compressed stems.** Median about 20 words; vignettes about 30; stay under about 55 words. Difficulty comes from inference, not reading load.
3. **Match stem form to the subject** (table above). Do not turn every fact into a vignette. In Community Medicine, half of real questions are one-liners and only 2% use images.
4. **Diagnosis first, then management and investigation**, in clinical subjects. Use "clues -> diagnosis" freely. Keep "diagnosis -> next step" chains for Tier 3 items, where they are the realistic hard form.
5. **Image items where the subject uses them**: Anatomy, Dermatology, Orthopaedics and Radiology (50-64%), Ophthalmology (29%), Surgery and OBG (about 20%). Use real figures only; never describe the finding in words.
6. **Plain lead-ins.** Mostly direct questions and "Which of the following…". Keep negatives to about 5%, and use "next best step" and "…of choice" only when they fit.
7. **Basic sciences are often clinically framed** (Microbiology 47%, Pharmacology 46%, Pathology 41% vignettes), but Physiology and Biochemistry stay mostly direct.
8. **PSM calculations are present but rare** (about 3% of Community Medicine). Include them only when the source supplies every parameter.
9. **Distractors come from the same neighbourhood** (same drug class, adjacent management steps, competing tests, nearby structures). This is item-writing practice, because recalled options are the least reliable part of a recall.
10. **Recurring concept, new wording.** Concepts recur across sittings but wording rarely repeats (about 1%), so test the concept from a new direction.

## Generator calibration

### Tier model (training design, not an official FMGE difficulty scale)

- **Tier 1 - Direct / recognition**: one explicit relationship; direct fact, classic presentation, image identification.
- **Tier 2 - Discriminative application**: one decisive discriminator between plausible options.
- **Tier 3 - Compressed two-step application**: two source facts, both recalled by the learner; usually two reasoning hops.

Default training mix per 50-question block: 15 / 20 / 15. Tier is about reasoning, not stem form: a Tier 2 or Tier 3 item can still be a one-liner, which matters in recall-heavy subjects.

### Stem-form and task targets

- Single-subject block: the subject's row in the table above, within about 15 percentage points.
- Mixed-subject or simulation block: about 30% one-liners, 10% longer direct, 45% vignettes, 15-20% image-led; tasks about 35% diagnosis, 28% recall, 14% management, 11% investigation, 8% mechanism, plus anatomy and calculation where supported.
- Subjects spread by the official blueprint.

## Lessons from the first generated block (PSM Block 1, v5 prompt)

The v5 block matched the tier mix, answer-letter balance and stem length, but not FMGE style:

- **37 of 50 stems referred to the study material.** Real FMGE stems never do.
- **4 items (Q36, Q40, Q45, Q48) printed the deciding fact in the stem.**
- **Items gave each other away.** For example, Q49's stem states Q15's answer.
- **Pair/combination items and shared option sets** (Q41, Q42; Q9 and Q35).
- **Ambiguous population or product** (Q14, Q34).
- **Stem form was roughly on-profile**, with 12 vignettes (24%) and 17 one-liners (34%) against 22% and 50% in real Community Medicine. The problem was how the harder items were built: "Tier 3" often came from premises printed in the stem rather than recalled facts.

Prompt v7 makes each of these a rule, and `scripts/fmge/build_question_bank.py --lint` checks the mechanical ones. Full item-by-item review: [`psm-block-1-review.md`](psm-block-1-review.md).

## Consequence for the PDF question-bank prompt

> Write Tier 3 as the hardest compressed, source-supported FMGE-style application a well-prepared candidate can solve in about a minute. Prefer two-step inference over narrative length. Never add outside examinable facts to manufacture difficulty. Follow the subject's measured stem form: in recall-heavy subjects, difficulty comes from close discrimination in short stems, not from vignettes.

## Sources

- PrepLadder FMGE previous-year paper hub: https://www.prepladder.com/fmge-study-material/previous-years-question-papers/fmge-previous-year-question-papers
- PrepLadder recall PDFs (Dec 2021, Jun 2022, Jan 2023, Jan 2024, Jun 2024, Jan 2025 Parts 1-2, Jul 2025 Parts 1-2): URLs and hashes in `../manifests/paper-catalog-2021-2025.csv`
- FMGEPrep previous-year papers (public samples): https://fmgeprep.com/fmge-previous-year-question-papers
- NEETFMGE Plans mirrors (not independent): `../manifests/paper-catalog-2021-2025.csv`
- NBEMS FMGE portal: https://www.natboard.edu.in/viewnbeexam?exam=fmge
- NBEMS June 2026 Information Bulletin (archived locally): https://nbe.edu.in/IB/FMGE%20JUNE%202026%20information%20bulletin.pdf
