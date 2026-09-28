# FMGE five-year question-pattern report (2021-2025)

## Scope and evidence

This report calibrates question-generation style from public **recall-based reconstructions**, not official NBEMS question papers.

Observed source set:

- 2021: PrepLadder December 2021 recall PDF.
- 2022: PrepLadder June 2022 recall PDF.
- 2023: PrepLadder January 2023 recall PDF.
- 2024: PrepLadder January and June 2024 recall PDFs.
- 2025: public January 2025 subject-wise 300-question recall and July 2025 subject-wise recall, cross-checked against PrepLadder's current PYQ/trend pages.
- Current format constraint: NBEMS FMGE information bulletin for time-bound sections.

The 2025 PrepLadder PDF binaries were listed publicly but were not reliably fetchable through the research tool during this pass, so 2025 conclusions use independent recall reconstructions rather than pretending those binaries were inspected.

Do not interpret recall-provider answer keys as authoritative medical truth.

## Core finding

FMGE is best modeled as a **compressed mixed-format exam**.

Difficulty does not come mainly from long stems. Recent recalls repeatedly mix:

1. very short factual/association questions;
2. short clinical vignettes with one decisive clue;
3. image, radiograph, pathology, anatomy, instrument, waveform or graph recognition;
4. diagnosis followed by investigation or management;
5. "next best step", treatment-of-choice and investigation-of-choice decisions;
6. close alternatives where one clue separates the best response;
7. mechanisms and consequence prediction;
8. PSM/biostatistics calculations and study-design interpretation.

The generator should reproduce this mixture rather than making every higher-tier item a long vignette.

## Year-by-year pattern

### 2021

The December 2021 recall already contains a strong mixture of direct and image-assisted items. Examples include an image-led dermatology feature question, image/anatomy identification, a clinical lesion followed by treatment choice, and short direct association questions.

Pattern:
- direct recall remains substantial;
- images are not decorative - they often carry the diagnostic clue;
- many questions require one relationship: image/condition -> structure, cause, treatment or feature;
- options are generally same-domain alternatives.

### 2022

The June 2022 recall makes the clinical application layer more obvious. The opening questions include trauma + image -> fracture identification, presentation -> epidemiological history, infection presentation -> false statement, and radiograph -> best treatment.

Pattern:
- more short scenario framing around standard facts;
- "best treatment" and "best diagnostic method" are common task forms;
- image plus management is a recurring construction;
- single-best-answer discrimination matters more than raw memorization alone.

### 2023

The January 2023 recall continues the mixture rather than replacing direct recall. The same early section contains culture-media recall, molecular mechanism, histology identification, nerve supply, embryology from a neck mass, gait localization, barium-swallow interpretation, lymphatic spread and physiology.

Pattern:
- direct and clinical questions coexist in the same subject block;
- basic sciences are frequently clinically framed;
- image/diagram interpretation is routine;
- questions often ask for a mechanism, localization or downstream relationship instead of the fact exactly as memorized.

### 2024

January and June 2024 recall material remains compact. January opens with very direct anesthesia facts; June includes both direct factual questions and short clinical/application items, including DNA-repair syndromes, ENT diagnosis, seizure management, drug adverse-effect management, immune deficiency and ocular diagnosis.

Pattern:
- one-line direct questions remain normal;
- short clinical scenarios are common but usually contain only the clues needed;
- management/next-step questions are prominent in clinical and pharmacology material;
- negative/EXCEPT questions occur, but are a minority and should not be overgenerated;
- visual identification and instrument/anatomy questions remain important.

### 2025

January 2025 and July 2025 recalls show the strongest shift toward **compressed clinical + visual/application framing**, while still preserving many direct facts.

January examples include:
- unstable rhythm -> cardioversion;
- pancreatitis-type presentation -> diagnostic investigation;
- trauma + blood at meatus -> injury localization;
- radiology sign -> diagnosis;
- instrument/image identification;
- pathology pattern -> tumor diagnosis;
- fetal anemia -> monitoring method;
- CTG/image/instrument interpretation;
- management after complications.

July examples include:
- anatomy localization and IBQs;
- nerve physiology/order-of-susceptibility reasoning;
- environmental/biochemistry clinical presentations;
- histopathology/genetic markers;
- PSM study design, statistics and calculations;
- ENT image + treatment;
- ophthalmic visual diagnosis;
- ECG-style/clinical medicine interpretation;
- immediate management in burns, airway, trauma and surgery;
- image recognition linked to management or investigation.

Pattern:
- images/instruments/waveforms are used across several subjects, not only radiology/pathology;
- "recognize -> act" questions are increasingly important;
- short stems can still be difficult when options are close;
- two-hop questions exist, but the exam rarely needs an unnecessarily long narrative.

## Stable five-year FMGE question DNA

### 1. Four-option single-best-answer

The generated bank should use exactly four options with one best response.

"Tricky" must mean **close medical alternatives with a decisive discriminator**, never genuine ambiguity.

### 2. Stem compression

FMGE stems are usually economical.

A difficult question should prefer:

clinical clue(s) -> inference -> answer

over:

long story -> same inference -> answer.

Default clinical stems should usually fit in roughly 1-4 concise sentences.

### 3. Mixed direct and applied questions

Do not eliminate direct recall.

A realistic block should deliberately contain both:
- direct fact/association questions; and
- short application/vignette questions.

The recent trend is toward more applied framing, but direct questions remain a meaningful scoring component.

### 4. Visual literacy

When source material permits, use:
- anatomy labels;
- pathology/histology;
- dermatology;
- radiology;
- ECG/waveforms;
- instruments/procedures;
- graphs/curves;
- obstetric/ophthalmic images.

The image should contain examinable information. Never add a decorative image.

A reasonable generator heuristic is **about 10-20% visual-led items when the input PDF contains enough usable visuals**. This is a calibration heuristic, not an official NBEMS quota.

### 5. One- and two-hop reasoning dominate

Typical hard constructions:

- clues -> diagnosis;
- diagnosis -> investigation;
- diagnosis -> first-line management;
- mechanism -> consequence;
- lesion -> structure -> deficit;
- drug -> adverse effect -> antidote/management;
- image -> diagnosis -> next step;
- clinical state -> severity/category -> treatment.

Tier 3 should usually stop at two meaningful reasoning hops.

### 6. Management and investigation are high-value task forms

Clinical questions frequently test:
- next best step;
- first-line treatment;
- immediate stabilization;
- definitive treatment;
- investigation of choice;
- confirmatory investigation;
- monitoring method.

Distractors should often be adjacent steps in the same algorithm.

### 7. Basic science is clinically portable

Do not reserve clinical framing for Medicine/Surgery.

Recent and older recalls support:
- Anatomy -> lesion/localization/deficit;
- Physiology -> waveform/response/changed variable;
- Biochemistry -> enzyme/deficiency/metabolic presentation;
- Pathology -> morphology + marker + diagnosis;
- Microbiology -> clinical syndrome + organism/test/treatment;
- Pharmacology -> mechanism/ADR/drug choice/antidote.

### 8. PSM needs calculations and design interpretation

PSM should not be generated only as factual program recall.

Where supported by the source PDF, include:
- incidence/prevalence;
- sensitivity/specificity or screening logic;
- study design;
- statistical test selection;
- normal distribution/basic biostatistics;
- vaccination/program questions;
- waste-management/public-health application.

### 9. Distractor closeness is central

Good FMGE-style distractors are usually from the same clinical or conceptual neighborhood.

Examples of discriminator axes:
- most likely vs possible;
- initial vs definitive;
- screening vs confirmation;
- sensitive vs specific;
- cause vs complication;
- acute vs chronic;
- anatomical level;
- timing;
- one laboratory/imaging clue;
- mechanism;
- treatment sequence.

### 10. Recurrent concept, new direction

PYQ learning should influence **concept selection and archetype**, not cause copied questions.

If a source/notes question already asks disease -> diagnosis, a new item should preferably test another direction:
- disease -> mechanism;
- disease -> investigation;
- disease -> complication;
- finding -> disease;
- treatment -> adverse effect;
- lesion -> functional deficit.

## Generator calibration

### Tier model

**Tier 1 - Direct / recognition**
- explicit source fact;
- one relationship;
- may be direct, image identification or classic association;
- no artificial trick.

**Tier 2 - Discriminative application**
- usually one reasoning hop;
- two or three options initially plausible;
- one clue decisively separates the best response;
- common forms: differential diagnosis, investigation, management order, close mechanism or anatomy.

**Tier 3 - Compressed two-step application**
- usually two reasoning hops;
- answer not copied verbatim from a single sentence;
- requires synthesis of source concepts;
- still concise and FMGE-like;
- must not import an unstated guideline/fact.

Default training mix per 50-question block:
- Tier 1: 15
- Tier 2: 20
- Tier 3: 15

This 30/40/30 training split is a learning design, not a claim about an official FMGE difficulty distribution.

### Stem-mode prior

For a large source with enough material, aim approximately for:
- 30-40% direct/compact factual;
- 40-50% short clinical/application;
- 10-20% visual-led or data/graph/instrument-led, when the PDF supports it.

These are generation priors and can overlap with task types. Do not force them when source content is unsuitable.

### Task-mode prior

Across the bank, ensure meaningful coverage of:
- diagnosis/identification;
- investigation/interpretation;
- management/next step;
- mechanism/consequence;
- anatomy/localization;
- adverse effect/antidote/drug choice;
- calculation/study design where relevant;
- classification/sequence/EXCEPT sparingly.

## Current exam-speed constraint

Current NBEMS bulletins use time-bound sections; the published example is 50 questions in 50 minutes. The generator should therefore favor high information density and avoid unnecessarily long stems.

## Consequence for the PDF question-bank prompt

The prompt should not say "make Tier 3 maximally hard" without qualification.

It should say:

> Make Tier 3 the hardest **compressed, source-supported FMGE-style application** that can be solved in about a minute by a well-prepared candidate. Prefer two-step inference over long narrative complexity. Never add outside examinable facts to manufacture difficulty.

## Sources

- PrepLadder FMGE previous-year paper hub:
  https://www.prepladder.com/fmge-study-material/previous-years-question-papers/fmge-previous-year-question-papers
- PrepLadder December 2021 recall PDF:
  https://image.prepladder.com/content/FMGE-dec-2021-pyq-pdf.pdf
- PrepLadder June 2022 recall PDF:
  https://image.prepladder.com/content/fmge-jun-2022-pyq-pdf.pdf
- PrepLadder January 2023 recall PDF:
  https://image.prepladder.com/content/fmge-jan-2023-pyq-pdf.pdf
- PrepLadder January 2024 recall PDF:
  https://image.prepladder.com/content/FMGE_Jan_2024_Question_paper.docx.pdf
- PrepLadder June 2024 recall PDF:
  https://image.prepladder.com/content/FMGE_June_2024_Question_Paper.docx.pdf
- PrepLadder 10-year trend analysis (secondary interpretation):
  https://www.prepladder.com/fmge-study-material/preparation-strategy/fmge-pyq-trend-analysis
- January 2025 subject-wise recall used for pattern inspection:
  https://www.scribd.com/document/821382459/19-1-25-300-Final-Fmge-Jan-2025-Subject-Wise-All-300
- July 2025 subject-wise recall used for pattern inspection:
  https://www.scribd.com/document/896472684/Fmge-July-25-Recall-Subject-Final
- NBEMS FMGE portal:
  https://www.natboard.edu.in/viewnbeexam?exam=fmge
