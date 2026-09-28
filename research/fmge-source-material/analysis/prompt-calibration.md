# FMGE source-grounded three-tier question-bank master prompt

## Version

v7 - v6 plus two evidence updates:
- **Measured FMGE pattern.** Stem mix, task mix, stem length, negative share, lead-in phrasing and per-subject profiles come from 1,499 recalled questions in five full sittings (Dec 2021, Jun 2022, Jan 2023, Jan 2025, Jul 2025), checked against 180 FMGEPrep samples.
- **Block-coherence and specificity rules** from the manual review of PSM Block 1 (`psm-block-1-review.md`), so a new block should not need that rewording or rework.

v6 had added: stand-alone stems, no stated premises, real image items, option parity, the NBEMS blueprint, handoff ledgers, checkable audits and the builder output contract.

Pattern evidence: `five-year-pattern-report.md` and the generated `recall-pattern-stats.md`. Exam structure: NBEMS June 2026 Information Bulletin (official).

## How to use this prompt (operator notes, not part of the prompt)

1. In a web session with a model that can see PDF **page images**, upload the notes PDF and paste everything from `# ROLE` to the end.
2. Save the model's complete Markdown reply (all parts, if it continued) as `research/pdf_extracted_questions_data/<Source>_combined.md`.
3. For every `**Image source:**` line, crop the figure with `uv run scripts/fmge/extract_pdf_image.py` and paste the printed `**Image:**` / `**Image alt:**` lines under it.
4. Run `python3 scripts/fmge/build_question_bank.py --source <md> --subject "<blueprint subject>" --lint`. Send every lint ERROR back to the same session for a rewrite (or fix it by hand), then build with `--strict`. The lint checks the mechanical rules: stand-alone stems, stated premises, cross-item give-aways, pair items, shared option sets, numeric order, answer balance, and stem mix against the subject profile.
5. Keep the `# QUESTION-DNA LEDGER` from each block. Paste it into the next session's first message so the new block does not repeat old questions.

---

# ROLE

You are an expert FMGE item writer: a medical examiner, a medical educator and an adversarial single-best-answer MCQ editor.

Transform the uploaded medical PDF into a **new FMGE-style question bank**. The PDF may contain printed text, handwritten notes, highlights, tables, diagrams, clinical/radiology/pathology images, instruments, graphs, solved MCQs, explanations and mnemonics.

Do NOT reproduce the PDF's own questions. Extract its medical knowledge and write new questions that read exactly like FMGE exam questions: a candidate in the exam hall has never seen these notes.

GOLDEN RULE: every question must be solvable, defensible and explainable from the uploaded PDF, and the fact it teaches must also be medically true. The usable question space is the intersection of **PDF-supported knowledge** and **truth-compatible knowledge**. A true fact absent from the PDF may not be tested; a PDF statement that looks false, unsafe, overgeneralized, outdated or spatially misread may not be taught. External knowledge may validate or veto an item, never silently become examinable.

---

# 0. SESSION CAPABILITY CHECK

Before anything else, state in one line each:

- whether you can see the rendered page images (not only extracted text);
- how many PDF viewer pages you can access;
- whether you can browse for validation.

If you cannot see page images: generate no item that depends on handwriting, arrows, table alignment or a visual, and say so in the ingestion report. Never claim to have inspected something you could not see.

---

# 1. FMGE EXAM FACTS (official NBEMS bulletin)

- 300 single-best-answer MCQs in two parts of 150 questions, each part 150 minutes.
- Each part runs as time-bound sections (example given: 50 questions in 50 minutes). A candidate cannot return to a closed section. Write for about **one minute per question**.
- Exactly 4 options; the candidate chooses the "correct / best / most appropriate" response. No negative marking. Pass mark 150/300.
- English only. The syllabus follows the NMC Competency Based UG Curriculum. Use Indian national programmes, schedules and terminology when the PDF uses them.

Official subject blueprint (marks out of 300):

| Pre/para-clinical (100) | | Clinical (200) | |
|---|---|---|---|
| Anatomy | 17 | Medicine 33, Psychiatry 5, Dermatology & STD 5, Radiotherapy 5 | 48 |
| Physiology | 17 | General Surgery 32, Anaesthesiology 5, Orthopaedics 5, Radiodiagnosis 5 | 47 |
| Biochemistry | 17 | Obstetrics & Gynaecology | 30 |
| Pathology | 13 | Community Medicine | 30 |
| Microbiology | 13 | Paediatrics | 15 |
| Pharmacology | 13 | Ophthalmology | 15 |
| Forensic Medicine | 10 | ENT | 15 |

When the PDF covers several subjects, allocate questions roughly by this blueprint within what the PDF supports.

---

# 1A. MEASURED FMGE PATTERN (recall evidence, 2021-2025)

Measured on 1,499 recalled questions from five full sittings. Recalls are reconstructions, so treat these as good estimates, not official quotas.

Whole paper:

| Measure | Real FMGE |
|---|---|
| Stem form | one-liner (<= 15 words) 29% · longer direct 10% · clinical vignette 44% · image-led 17% (true share nearer 20%; the detector misses some) |
| Task asked | fact recall 28% · diagnosis 35% · management 14% · investigation 11% · mechanism 8% · anatomy/localization 3% · calculation 2% |
| What vignettes ask | diagnosis 50% · management 21% · fact 11% · investigation 9% · other 9% |
| Stem length | median 21 words; vignettes median 31, 90% under 52; 95% of all stems under 55 |
| Negative stems (EXCEPT/NOT/false) | about 5% (range 1-7% by sitting) |
| Lead-in phrasing | plain direct question ("What is…?", "Which drug…?") 37% · "Which of the following…" 24% · "…diagnosis?" 18% · "Identify/Spot…" 6% · negative 5% · "next (best) step" 3% · "most common" 3% · sentence completion ("… is:") 2% · "true about" 1% · "…of choice" 1% |
| Repeats | only ~1% of questions closely repeat an earlier sitting; concepts recur, wording does not |

Stem form by subject (one-liner / vignette / image-led, from 1,001 subject-labelled questions):

| Subject | One-liner | Vignette | Image | | Subject | One-liner | Vignette | Image |
|---|---|---|---|---|---|---|---|---|
| Community Medicine | 50% | 22% | 2% | | Medicine | 25% | 59% | 14% |
| Physiology | 69% | 16% | 3% | | General Surgery | 23% | 51% | 20% |
| Biochemistry | 55% | 24% | 13% | | Obstetrics & Gynaecology | 40% | 33% | 20% |
| Anatomy | 20% | 12% | 61% | | Paediatrics | 30% | 53% | 13% |
| Pathology | 39% | 41% | 10% | | Ophthalmology | 13% | 53% | 29% |
| Microbiology | 33% | 47% | 16% | | ENT | 23% | 57% | 14% |
| Pharmacology | 39% | 46% | 13% | | Orthopaedics | 4% | 35% | 61% |
| Forensic Medicine | 30% | 22% | 15% | | Dermatology | 14% | 18% | 64% |
| Anaesthesiology | 41% | 32% | 14% | | Radiology | 38% | 12% | 50% |
| Psychiatry | 29% | 65% | 0% | | | | | |

The remainder of each row is longer direct questions. Community Medicine is 63% fact recall, and its vignettes are short field or programme scenarios, not hospital cases.

How to use this:

- **Match the block's stem form to its subject row.** A Community Medicine block should be mostly short direct questions; an Anatomy, Dermatology, Radiology or Orthopaedics block should lean on images.
- **Tier is about reasoning, not stem form.** A Tier 2 or Tier 3 item can still be a one-liner ("Best indicator of combined maternal and newborn care is:"). Do not dress recall up as a vignette to raise its tier.
- **Use the real lead-ins.** Mostly plain direct questions and "Which of the following…". Use "next best step" and "…of choice" only where they fit.
- **Vignettes should mostly ask diagnosis or management.** That is what half and a fifth of real vignettes ask.

---

# 2. WHAT AN FMGE QUESTION LOOKS LIKE

FMGE difficulty comes from medical discrimination: a decisive clue, a mechanism, choosing the right investigation or management step, interpreting an image/graph/waveform/instrument, or combining one or two concepts.

It does NOT come from long stems, obscure trivia, ambiguous wording, two defensible answers, linguistic tricks or double negatives. A hard FMGE question is usually **compressed**: roughly 1-4 short sentences, at most about 60 words.

Recent recalls show a **mixture**, so write a mixture:

- A. **Direct compact recall**: structure, association, organism, drug, most common/characteristic feature, classification, value. Direct questions are normal FMGE questions; do not turn every fact into a vignette.
- B. **Short clinical diagnosis**: a few discriminating clues -> most likely diagnosis.
- C. **Investigation/interpretation**: investigation of choice, confirmatory test, monitoring method, lab/ECG/radiology/graph interpretation, screening vs diagnosis.
- D. **Management/next step**: immediate stabilization, next best step, first-line or definitive treatment, management after a complication or adverse effect. Where the PDF teaches an operation, test the operation (storage rule -> where to place the vaccine; VVM appearance -> use or discard; exposure + vaccine status -> schedule; equipment capacity -> which device).
- E. **Image/instrument/waveform**: see section 10.
- F. **Mechanism -> consequence**: drug action -> adverse effect; lesion -> deficit; enzyme defect -> presentation.
- G. **PSM/biostatistics application**: rates and ratios, study design, test choice, screening logic, programme application, immunization, biomedical waste. Not programme-name recall only.
- H. **Close discrimination**: two or three options look plausible; one clue settles it.
- I. **Two-step integration** (mainly Tier 3): clues -> diagnosis -> next step; image -> diagnosis -> management; drug -> mechanism -> consequence.

Basic sciences should be clinically portable when the PDF allows it (anatomy -> lesion/deficit, physiology -> waveform/changed variable, biochemistry -> enzyme/presentation, pathology -> morphology/marker, microbiology -> syndrome/organism/test, pharmacology -> mechanism/ADR/antidote), but a direct fact stays direct when that is the more authentic FMGE form.

---

# 3. STEM RULES (hard rules - an item that breaks one is rejected)

1. **Stand-alone stem.** The stem must read as an exam question. It must never mention or point at the study material: no "in the notes", "shown in the source", "according to the PDF/table/figure/slide", "the schedule displayed", "as annotated", "the source identifies…", "on page…". Test the fact itself: write "The diluent used to reconstitute BCG vaccine is:", not "Which diluent is shown for BCG?". Page citations belong only in the answer key.
2. **No stated premise.** The stem must not hand over the fact that decides the answer. Bad: "Measles vaccine given within 3 days of exposure is protective. A child exposed 48 hours ago… best action?" Good: "An unvaccinated 14-month-old had household contact with measles 48 hours ago. Best action?" If an item can only be solved once the stem states the key fact, it is reading comprehension: reject it or make it Tier 1 recall of that fact.
3. **"Shown" only with an image.** Use "shown", "displayed" or "depicted" only when the item carries an image (section 10).
4. **One question, one task.** End with a clear lead-in ("Most likely diagnosis is:", "Next best step is:", "Which of the following…?").
5. **Compression.** For every sentence ask: can it go without losing the discriminator? If yes, delete it. Age, sex and occupation appear only when they discriminate.
6. **Negatives sparingly.** Real FMGE has about 5% negative stems: aim for 2-3 per 50-item block, "EXCEPT/NOT" in capitals, never double negatives.
7. **Time anchors.** A historical, programme-status or version-dependent fact needs a time or version qualifier that the PDF supports ("Under the 2016 switch…"), or it is excluded.
8. **Name the population, product or version.** When the answer differs by age group, population, product, programme or guideline version, the stem names it. Bad: "The Anemia Mukt Bharat tablet contains:" (dose differs by group). Good: "Under Anemia Mukt Bharat, the IFA tablet for pregnant women contains:". Bad: "Cervavac schedule at 13 years?" (WHO also endorses a single dose). Good: "As per its licensed schedule, Cervavac at 13 years is given as:".
9. **Named authorities are fine; the notes are not.** "According to the Biomedical Waste Management Rules 2016…", "Under the UIP…" or "As per WHO…" are normal FMGE wording when the PDF supports that framework. "According to the notes/source/table" is never allowed.
10. **Length.** Real stems: median about 20 words, vignettes about 30, and almost none over 55. Keep one-liners at 15 words or fewer.

---

# 4. OPTION RULES (hard rules)

- Exactly four options, A-D, one best answer; all options homogeneous (same category, grammatical form and unit style).
- No "all of the above", "none of the above", "both A and B" or combined-letter options.
- No duplicate or near-duplicate options; no two options that are both defensible.
- **Length parity**: the correct option must not regularly be the longest or the most qualified. Across the block, the correct option is the unique longest in no more than about a third of items.
- Distractors come from the same neighbourhood: same disease family, drug class, adjacent management steps, competing investigations, nearby anatomical structures, similar organisms, related complications. A Tier 2/3 distractor should often be right in a nearby scenario but wrong for this stem.
- Every distractor must be plausible **for the setting in the stem** (no walk-in cooler offered for a subcentre outreach session, no tertiary procedure for a field-level question).
- No joke options, irrelevant organ systems, grammatical giveaways or repeated absolute words.
- **Numeric options in ascending order** (doses, years, rates, ranges), as FMGE papers print them.
- **One relationship per item.** No "Which pair/combination correctly gives X and Y?" items that join two unrelated recalls. Only use a matched pair when the pairing itself is the fact being tested (e.g. vaccine -> diluent).
- **Answer-letter balance**: across a 50-item block each letter is correct 10-15 times, with no run of more than 3 identical letters and no visible pattern. Decide letter positions deliberately after writing the options.

---

# 5. SOURCE BOUNDARY AND TRUTH GATE

The uploaded PDF is the **examinable knowledge source**.

Support classes (internal, reported in the key):

- E0 = explicitly stated in the PDF.
- E1 = direct inference from one PDF concept.
- E2 = synthesis of two or more PDF concepts/pages.
- E3 = needs an important fact absent from the PDF -> FORBIDDEN unless I enable external-knowledge mode.

Source support applies to the **whole item**: decisive stem clues, correct answer, the facts needed to eliminate each plausible distractor, numbers, management rules, reasoning links and the explanation. Neutral clinical framing (age, setting) may be invented only when it adds no diagnostic, therapeutic, mechanistic, epidemiological or guideline knowledge.

SOURCE-ONLY ELIMINATION TEST: could a learner who knows only this PDF pick one best answer using E0-E2? A familiar entity absent from the PDF may be a distractor only if no outside fact is needed to rule it out. Apply this especially to contraindications, schedules, drugs, adverse effects, organisms, staging, thresholds, calculations and mechanisms.

TRUTH-COMPATIBILITY GATE: the PDF is not assumed infallible. For dynamic, safety-relevant, unusually specific, annotation-dependent or suspicious facts (doses, schedules, cutoffs, contraindications, device principles, definitions, programme status, current guidelines), check against an authoritative source if you can browse, otherwise against well-established medical knowledge, and say which you used in the audit. Validation may approve, qualify, veto or force a rewrite; it may never supply a hidden step.

- PDF-supported and defensible -> may be tested.
- PDF-supported but contradicted/unsafe -> reject, or narrow to the shared true statement if the PDF still supports it.
- True but absent from the PDF -> do not test.
- Version/formulation/programme-dependent -> include the qualifier only if the PDF supports it; otherwise exclude.
- Historically true, no longer current -> time-anchor if the PDF supports the historical frame; otherwise exclude.
- "According to the PDF" is never a loophole for teaching a false or unsafe claim, and never appears in a stem.

If defending the answer or eliminating a distractor needs an unstated dose, cutoff, guideline, staging rule, contraindication or criterion, rewrite or reject the item. Tier 3 is inference, not hallucination.

CALCULATION GATE: a calculation is allowed only when the PDF states or directly supports the formula, every variable, any weighting or conversion factor, and the interpretation. Give the learner every number they need in the stem. Never supply an omitted disability weight, correction factor, denominator or cutoff from memory.

---

# 6. INGESTION

Before Question 1, inspect the entire accessible PDF. If it cannot be processed in one pass, index it in page ranges, finish, then generate.

For scanned or image-heavy PDFs, **the rendered page image outranks OCR or extracted text**. Anything that depends on handwriting, arrows, table alignment, spatial grouping or a visual relation must be checked on the rendered page.

The **PDF viewer page number** is the citation system (printed slide/page numbers are secondary labels only). Never fabricate a page.

Build a concept ledger by page: definitions, high-yield facts, causes, mechanisms, clinical clues, differentials, investigations, findings, pathology, treatments (immediate vs definitive), contraindications, adverse effects, complications, anatomy, classifications, algorithms, formulas, tables, images, handwritten additions and contrasts. Harvest small operational details aggressively: strains, diluents, routes/sites, temperatures, storage locations, time windows, schedules, numeric cutoffs, equipment capacity/duration, exceptions and can/cannot rules. Tag each with R (recall), D (discrimination), A (action), I (integration), V (visual). Small details must not disappear behind headline topics.

HANDWRITING: classify as CLEAR / PARTIALLY CLEAR / UNREADABLE / CONFLICTING. Use only CLEAR handwriting.

SPATIAL-RELATION GATE: a legible annotation can still be attached to the wrong printed concept. Decide what it modifies from arrows/leader lines, row/column alignment, shared underline/highlight, colour, boxes and labels, and only then proximity. Grade it HIGH (explicit link or several converging cues), MEDIUM (one weak cue) or LOW (free-floating/crowded). Use HIGH; MEDIUM only if another page corroborates it; never LOW. Never invent missing handwriting, arrows, row membership or note targets.

CONFLICTS: if handwriting conflicts with print, or years/schedules/versions conflict anywhere, use the version the PDF itself identifies as applicable (cite the resolving page); otherwise exclude items that depend on the conflict and list it in the ingestion report.

---

# 7. QUESTION EXCLUSION AND DUPLICATION

The exclusion set is: the PDF's own solved questions, every question already generated in this conversation, and any QUESTION-DNA LEDGER or bank I paste in. If I say earlier blocks exist but have not pasted their ledger, ask for it before generating; never claim cross-block deduplication you cannot check.

Question DNA = concept + direction tested + stem archetype + correct-answer relationship + viewer page(s).

A pasted bank or ledger from another session is calibration input only: it may reveal uncovered concepts, archetypes or missed visuals, never examinable facts. Verify and remap its page numbers against this PDF before relying on them; an item without a verifiable page still belongs in the exclusion set.

Reject a candidate when:

1. knowing an existing answer directly reveals the new answer;
2. it asks the opposite, exception, negative or converse of the same relationship;
3. the same option set works with minor edits;
4. the disease -> fact relationship is unchanged despite a reversed stem;
5. only age, sex, numbers, chronology or presentation changed cosmetically;
6. a learner who memorized the old item without understanding the topic could answer the new one.

BLOCK COHERENCE (items in the same block are seen together):

- No stem may contain another item's answer or deciding fact. For example, a calculation that states "vitamin A solution 1 lakh IU/mL" gives away a recall item asking that strength. State the number differently, or drop one of the two.
- No two items on the same micro-fact, even from different directions (e.g. "carrier holds 16-20 vials" and "which device for 16-20 vials").
- Do not reuse an option set: two items must not share three or more options.

Reusing a topic needs a different competency (identification -> management, mechanism -> expected finding, investigation -> interpretation, equipment -> operational decision, schedule recall -> patient-specific selection). Two items may share a disease only if they test different competencies. A dense page may yield several items with different DNA; a thin page may yield none.

---

# 8. THREE TIERS

Assign the tier by the **minimum cognitive operations needed**, not by stem length. A wrapper, long stem or calculation does not raise a tier. After writing each item, challenge it: if one memorized fact solves a Tier 2/3 item, downgrade it; if a Tier 3 item needs an unstated third fact, reject it as E3.

**TIER 1 - Direct / recognition** ("I studied this.")
Mainly E0; one source relationship answers it; direct fact, classic presentation, straightforward image identification, association, or a clearly taught treatment/investigation. Plausible same-category distractors, no artificial trick.

**TIER 2 - Discriminative application** ("I know both possibilities; one clue makes one better.")
E0-E1; exactly one meaningful discrimination or inference; at least two genuinely plausible source-supported options; one decisive discriminator (initial vs definitive, screening vs confirmatory, similar drugs/organisms, adjacent structures, most likely vs merely possible, timing/lab/imaging distinction). If one memorized line answers it without the discriminator, it is Tier 1.

**TIER 3 - Compressed two-step application** ("The answer was not a sentence in my notes, but the concepts to derive it were.")
E1-E2; two distinct source-supported propositions, both necessary, **both recalled by the learner rather than printed in the stem**; concise stem. Forms: finding -> diagnosis -> expected finding; diagnosis -> next investigation/management; drug action -> change -> adverse effect; lesion -> structure -> deficit; image -> diagnosis -> next step; two PDF concepts -> necessary inference. For each E2 item record Fact A (page X), Fact B (page Y) and the conclusion; reject if A alone answers it, B is decorative, or an unstated Fact C is needed.

HARD LIMIT: Tier 3 is the hardest source-supported FMGE-style item a well-prepared candidate can solve in about a minute. Not a long USMLE case, not super-specialty, not a three-guideline memory test. Prefer two hops; three only when every component is clearly taught.

---

# 9. BLOCK MIX

Default block: 50 questions = Tier 1: 15, Tier 2: 20, Tier 3: 15. This is a training design, not an official FMGE difficulty distribution. If the PDF cannot sustain it honestly, deliver the honest counts and say so; never inflate a tier.

Stem-form target: use the PDF subject's row in section 1A. For a mixed-subject PDF, use the whole-paper mix: about 30% one-liners, 10% longer direct, 45% vignettes and 15-20% image-led. Image items only when the PDF has usable figures. Stay within about 15 percentage points of the target, and report the actual mix in the audit.

Task target: in a clinical subject, diagnosis is the most common task, then management and investigation. In Community Medicine, Physiology, Biochemistry and Anaesthesiology, direct fact recall dominates. Cover mechanism/consequence, anatomy/localization, drug/ADR/antidote and calculation/study design where the PDF supports them. Do not force a quota the source cannot support.

---

# 10. IMAGE ITEMS

Do not ignore the PDF's diagrams, photographs, radiographs, specimens, instruments, charts, curves and tables. For each usable visual decide whether it supports: direct identification; finding -> diagnosis; image + clue -> diagnosis; image -> investigation/management; marked structure -> function/deficit; graph/waveform -> interpretation. Tier 1 usually uses the first; Tier 2 the middle; Tier 3 the last three.

An image item uses the **real figure**, which will be cropped from the PDF after you finish. Mark it on its own line directly under the stem, before the options:

    **Image source:** p.<viewer page> | <where the figure is on the page and what it is, e.g. "lower-left photo, vaccine carrier with ice packs">

Rules:

- The stem says "The image shown…", "The instrument shown…", "The curve shown…". It must not describe the finding in words, because that gives the answer away.
- The figure must contain the examinable information and must not have the answer printed on it (label, caption, arrow text). If the only usable figure is labelled with the answer, say in the audit that it needs masking, or skip it.
- If the figure is too small, unclear or ambiguous on the rendered page, do not use it.
- Never refer to an image that is not marked with an `**Image source:**` line.

---

# 11. WORKFLOW

1. **Ingest** the whole PDF (section 6). If pages remain unprocessed, stop and report them before generating.
2. **Exclusion map** (section 7).
3. **Coverage matrix**: topics, pages, concept density, contrasts, visuals, handwritten notes, solved-question contamination, and Tier 1/2/3 opportunities. Do not generate one question per page. For each major topic check which distinct competencies it supports: identify, distinguish, calculate, interpret, act, anticipate a consequence, select equipment, choose an investigation, choose management. Allocate by concept density and medical relevance; topic-name coverage alone is not enough. Preserve the PDF's conceptual level: an operational public-health fact becomes an operational question, a table tests its relationship, a visual becomes an image item. Do not turn every fact into a tertiary-care vignette.
4. **Candidates**: draft about 1.5-2 times the block size in candidate DNAs (75-100 for a 50-question block) before writing full items; for each note page(s), concept, competency, tier, archetype, answer relationship, closest distractor and discriminator. If you cannot track that many reliably, use a smaller block and say so.
5. **Adversarial QC** of every candidate. Reject or rewrite anything that fails:
   1. stem rules (section 3) - stand-alone stem, no stated premise, "shown" only with an image, population/product/version named, length;
   2. option rules (section 4) - including ascending numbers and one relationship per item;
   3. semantic exclusion, memory-leak and block-coherence tests (no stem gives away another item's answer; no shared option sets; no repeated micro-fact);
   4. whole-item E0-E2 support and the source-only elimination test;
   5. one clearly best answer;
   6. the tier challenge; for E2, both facts necessary;
   7. calculation gate;
   8. handwriting, spatial-relation and conflict gates;
   9. truth-compatibility gate;
   10. medical (not linguistic) difficulty; FMGE level, not NEET-PG/super-specialty;
   11. image item has a real, answer-free figure.
6. **Write** the accepted items, recheck them, and deliver.

Do not expose private chain-of-thought; give concise teaching reasoning only.

---

# 12. OUTPUT CONTRACT (exact format - it is parsed by a script)

Deliver sections in this order. Use these headings **exactly**. Do not add answers, tiers-in-stem, bold text or commentary inside the question section.

## Part 1

```
## DOCUMENT INGESTION REPORT
- Page images visible: Yes/No
- Viewer pages: <total>; interpreted: <n>; not processed: <list or none>
- Citation system: PDF viewer page number
- Subjects/topics: …
- Microfacts and operational details harvested (approximate count and main kinds): …
- Handwritten notes: Yes/No; visuals/tables: Yes/No; usable visuals for image items: <pages>
- Solved questions in PDF: <approximate count>
- Uncertain handwriting / unresolved spatial links: <pages or none>
- Source/version conflicts and how resolved: …
- Source-truth conflicts excluded or reframed: …

# QUESTION BANK — BLOCK <N>

## TIER 1 — DIRECT / RECOGNITION

### Q1
<stem>

A. <option>
B. <option>
C. <option>
D. <option>

### Q2
<stem>
**Image source:** p.34 | lower-left photo, instrument on a tray

A. <option>
B. <option>
C. <option>
D. <option>

## TIER 2 — DISCRIMINATIVE APPLICATION

### Q16
…

## TIER 3 — COMPRESSED TWO-STEP APPLICATION

### Q36
…
```

Format rules for the question section:

- The question heading is exactly `### Q<number>` with nothing else on the line. Number continuously from 1 through the block.
- The stem is plain text: no citation, tier, topic or answer hint.
- Each option is on its own line as `A. `, `B. `, `C. `, `D. `.
- `**Image source:**` goes only on image items, between the stem and the options.

## Part 2

```
# ANSWER KEY AND TEACHING REVIEW

### Q1 — **B — <exact text of option B>**
**Archetype:** <direct recall / short clinical diagnosis / investigation / management / mechanism / image / calculation / close discrimination / two-step integration>
**Topic:** <topic — subtopic>
**Source:** PDF p.<n>[, p.<m>] | E0/E1/E2 | Printed/Handwritten/Table/Diagram/Multi-page
**Closest distractor:** <option letter and text> — defeated by <discriminator>, p.<n>
**Concept link:** <Tier 3 only: Fact A (p.X) + Fact B (p.Y) -> conclusion>
<Teaching explanation: 1-3 sentences a student reads after answering. State why the answer is right and, in one clause, why the closest distractor is wrong. Source-supported facts only. No page numbers, no "the notes/PDF/source", no evidence grades.>
```

Answer-key rules:

- The heading is exactly `### Q<n> — **<letter> — <option text>**`, using em dashes.
- `**Source:**` must contain at least one `p.<n>` viewer page for the answer, plus the page that defeats the closest distractor if different.
- The teaching explanation is the only plain paragraph. It is shown to students, so write it as teaching, not as an audit note. Do not add textbook enrichment, external mechanisms, timing rules or guidelines merely because they are true.

## Part 3

```
# FINAL PATTERN AUDIT
- Total; Tier 1 / 2 / 3:
- Stem form: one-liner / longer direct / vignette / image-led (count only items with an **Image source:** line as image-led), next to the section 1A target for this subject:
- Lead-in forms used (direct question / which of the following / diagnosis / next step / other):
- Task modes: diagnosis / investigation / management / mechanism / anatomy / drug-ADR / calculation:
- Correct-option distribution A / B / C / D:
- Items where the correct option is the unique longest:
- Negative (EXCEPT/NOT) stems:
- Subjects (for multi-subject PDFs) vs blueprint:
- Source pages represented:
- Truth validation: which facts were checked, and against what (browsing or established knowledge):
- Notable rejections: up to 10, one line each (concept — reason)
- Deviations from the target mix, and why:
- Images needing answer masking:

# QUESTION-DNA LEDGER
| Q | Tier | Concept | Direction tested | Archetype | Answer relationship | Pages |
|---|---|---|---|---|---|---|
| 1 | 1 | … | … | … | … | … |
```

Audit rules: report only counts you can read off the delivered block. Do not print "0 ambiguous questions" or any other pass claim you did not actually check item by item. The DNA ledger is how the next block avoids repeats, so fill every row.

DELIVERY: if the reply would be cut off, stop at the end of a complete question or answer-key entry and write `CONTINUE FROM Q<n>`. When I reply "continue", resume with exactly the next item and the same headings. Do not restart or renumber.

---

# 13. SIMULATION MODE

If I request SIMULATION MODE: produce the same output contract (tier headings are still required for the parser, and the app mixes the tiers when it builds the section). Spread subjects by the blueprint, follow each subject's section 1A stem form, aim at the whole-paper task mix (diagnosis ~35%, fact recall ~28%, management ~14%, investigation ~11%, mechanism ~8%), and write strictly for one-minute decisions.

---

# 14. DEFAULT SETTINGS

Target: FMGE · four-option single best answer · block size 50 · tier mix 15/20/15
Direct questions: PRESERVE · short clinical framing: WHERE IT DISCRIMINATES · image items: REAL FIGURES WHEN THE PDF SUPPORTS
Stand-alone stems (no reference to notes/source): REQUIRED · stated premises in stems: FORBIDDEN · population/product/version named when the answer depends on it: REQUIRED
Stem form: MATCH THE SUBJECT PROFILE (section 1A) · negatives ~5% · stems at or under ~55 words
Block coherence (no cross-item give-aways, no shared option sets, no repeated micro-facts): REQUIRED
Option parity, ascending numeric options and answer-letter balance: REQUIRED · all/none of the above and pair/combination items: FORBIDDEN
Existing PDF solved questions and earlier blocks: STRICT SEMANTIC EXCLUSION
Printed text, clear handwriting, tables, diagrams: USE
External examinable knowledge: OFF · external truth validation: VETO/QUALIFY ONLY
Rendered-page authority for scanned PDFs · HIGH-confidence annotation linkage: REQUIRED
Cross-page inference and Tier 3 two-step synthesis: ON · long-vignette inflation: OFF
Answers beside questions: OFF · teaching explanations: ON · viewer-page citations: REQUIRED
Audit: CHECKABLE COUNTS ONLY · hallucination tolerance: ZERO

BEGIN: report the session capability check, ingest and map the complete accessible PDF, then generate. Do not write Question 1 until the concept ledger, exclusion set and coverage matrix are complete.
