# FMGE source-grounded three-tier question-bank master prompt (v9.3)

Paste everything below this line into the web session, together with the notes PDF. The prompt is self-contained.

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

- **Match each section's stem form to its subject row.** A Community Medicine section should be mostly short direct questions; an Anatomy, Dermatology, Radiology or Orthopaedics section should lean on images.
- **Tier is about reasoning, not stem form.** A Tier 2 or Tier 3 item can still be a one-liner. Tier 2: "Minimum antenatal visits under the RCH programme is:", where RCH 4 must be told apart from WHO 8. Tier 3: "Which of the following vaccines is contraindicated in pregnancy?", with a live vaccine among inactivated ones, which needs two recalled facts. Do not dress recall up as a vignette to raise its tier.
- **Use the real lead-ins.** Mostly plain direct questions and "Which of the following…". Use "next best step" and "…of choice" only where they fit.
- **Vignettes should mostly ask diagnosis or management.** That is what half and a fifth of real vignettes ask.

**Where the questions fall.** FMGE samples a subject widely and shallowly. In three sittings with topic labels (December 2021, June 2022, January 2023; 899 questions), no chapter drew more than about 4 questions per sitting, and most drew 0-2. Most-asked chapters, with counts across those three sittings:

| Subject | Most-asked chapters (count in 3 sittings) |
|---|---|
| Community Medicine | Nutrition 12 · Concept of health and disease (incl. levels of prevention) 11 · Allied health disciplines 8 · Health education and communication 8 · Biostatistics 7 · Epidemiology 6 · National programmes 6 · Communicable/NCD 6 · Demography 5 · Vaccines and cold chain 5 |
| Medicine | Cardiology 21 · Pulmonology 18 · Neurology 17 · Endocrinology 14 · Haematology 8 |
| Surgery | GI surgery 30 · Urology 28 · Vascular/cardiothoracic 10 · Endocrine 9 · Hepatobiliary-pancreatic 8 |
| OBG | Gynaecology 46 · Obstetrics 38 |
| Paediatrics | Nutrition and malnutrition 8 · Growth 5 · Neonatology 5 · Neurology 4 |
| Biochemistry | Vitamins 12 · Carbohydrate metabolism 9 · Lipid metabolism 6 · Enzymes 5 |
| Pharmacology | Spread evenly: ANS, CNS, anticancer, CVS, GIT, renal 5-6 each |
| Anatomy | Head and neck 8 · Upper limb 8 · Lower limb 6 · Thorax 6 · Abdomen, embryology, histology 5 each |
| Microbiology | Systemic bacteriology 17 · Virology 9 · General microbiology 8 · Mycology 6 |
| Pathology | RBC disorders 8 · Immunity 7 · WBC disorders, inflammation, liver 4 each |
| Physiology | Endocrine and reproductive 11 · CVS 5 |
| Forensic Medicine | Toxicology 10 · Thanatology 6 · Sexual jurisprudence 5 · Traumatology 4 |
| ENT | Nose and sinuses 15 · Ear 14 · Larynx 7 · Pharynx 5 |
| Ophthalmology | Retina 7 · Optics 6 · Cornea 5 · Orbit 5 · Conjunctiva, lens 4 each |

What gets asked inside a chapter is its core: definitions and classifications, "most common" and "of choice", classic signs and associations, standard formulas, stable schedules and programme components, classic images. Detail below that level is rare.

---

# 1B. REAL FMGE QUESTION GALLERY

These are real FMGE questions, reconstructed from candidate recall (2021-2025; wording lightly edited and some distractors tidied), with their level, form and trap. They show what the numbers in section 1A cannot: how hard real questions are, how much detail they ask for, how they are worded and how close the wrong options sit.

Use the gallery **only to calibrate**:
- Tier 1 should feel like the Tier 1 examples, Tier 2 like the Tier 2 examples, and Tier 3 no harder than the Tier 3 examples.
- Match their grain of detail, their wording and length, and how close their distractors are.
- Never copy, paraphrase or re-test a gallery question, and never take a fact from it. Examinable facts come only from the uploaded PDF. Gallery questions are part of the exclusion set (section 7).

**Community Medicine (PSM)**

G1 · Tier 1 · one-liner · recall
fIPV under the National Immunization Schedule is given at:
A. 6, 10 and 14 weeks · B. Birth, 6, 10 and 14 weeks, 16-24 months and 5 years · C. 6 weeks, 14 weeks and 9 months · D. 6, 10 and 12 weeks — **C**
Trap: A is the pentavalent/OPV schedule, a neighbouring row of the same table.

G2 · Tier 1 · one-liner · recall
WHO definition of blindness is visual acuity less than:
A. 1/60 · B. 3/60 · C. 6/60 · D. 6/18 — **B**
Trap: 6/60 is the older Indian definition.

G3 · Tier 1 · short scenario · programme recall
A girl with schizophrenia attends a PHC. The Government of India teleconsultation service for mental health support is:
A. Tele MANAS · B. U-WIN · C. Ni-kshay · D. NIKUSHT — **A**
Trap: other Government of India apps from the same family.

G4 · Tier 2 · short scenario · application
A pregnant woman whose last child is 2 years old completed her antenatal tetanus immunization in that pregnancy. For the current pregnancy she needs:
A. One booster dose of TT · B. One booster dose of Td · C. Two doses of TT · D. Two doses of Td — **B**
Trap: the "2 doses" rule applies only when the previous doses were more than 3 years ago; TT has been replaced by Td.

G5 · Tier 2 · short scenario · classification
A man with a family history of colon cancer undergoes screening colonoscopy. Screening is which level of prevention?
A. Primordial · B. Primary · C. Secondary · D. Tertiary — **C**
Trap: "prevention" makes candidates pick primary.

G6 · Tier 2 · scenario · study design
Office records from the past 20 years are used to compare the incidence of disease in factory workers exposed to aniline dyes with unexposed clerks. The study design is:
A. Prospective cohort · B. Retrospective cohort · C. Case-control · D. Ecological — **B**
Trap: "past records" suggests case-control, but the study starts from exposure and compares incidence.

G7 · Tier 2 · direct · health system
The eligible couple register is maintained by the:
A. ASHA · B. ANM / MPW (female) · C. Anganwadi worker · D. Village health guide — **B**
Trap: ASHA helps identify couples, but the register belongs to the ANM.

**Medicine and allied**

G8 · Tier 2 · vignette · diagnosis
A patient has palpitations, headache and sweating, with BP 180/100 mmHg. 24-hour urinary metanephrines are raised. Diagnosis?
A. Carcinoid tumour · B. Pheochromocytoma · C. Neuroblastoma · D. Cushing syndrome — **B**
Trap: carcinoid also causes episodic symptoms, but its marker is 5-HIAA.

G9 · Tier 1 · one-liner · investigation
CSF in bacterial meningitis shows:
A. Raised protein, low glucose · B. Raised protein, normal glucose · C. Low protein, raised glucose · D. Normal cells, normal glucose — **A**

G10 · image form · diagnosis
A patient has central chest pain and a history of heart disease. ECG is shown below. What is the diagnosis?
A. Anterolateral MI · B. Inferolateral MI · C. Acute pericarditis · D. Constrictive pericarditis
Form only: in image items, the stem gives brief context and the finding sits in the picture, never in words.

G11 · Tier 2 · vignette · diagnosis (Psychiatry)
A girl eats large amounts of food in one go and then makes herself vomit. Her BMI is 27. Most probable diagnosis?
A. Anorexia nervosa · B. Binge eating disorder · C. Bulimia nervosa · D. OCD — **C**
Trap: binge eating disorder has no compensatory vomiting; anorexia needs a low BMI.

**Surgery, OBG, Paediatrics**

G12 · Tier 3 · vignette · complication
A 2-month-old boy has had a scrotal swelling since birth. It is now suddenly painful, red and irreducible. Most likely diagnosis?
A. Acute epididymo-orchitis · B. Testicular torsion · C. Incarcerated inguinal hernia · D. Strangulated inguinal hernia — **D**
Trap: incarcerated and strangulated differ by one clue (redness and pain point to compromised blood supply).

G13 · Tier 2 · negative one-liner · anatomy
All of the following form the boundaries of Hesselbach's triangle EXCEPT:
A. Inferior epigastric artery · B. Rectus abdominis · C. Inguinal ligament · D. Vas deferens — **D**

G14 · Tier 2 · vignette · recall in context
One week after a normal delivery, a woman has pale brownish vaginal discharge. This is:
A. Lochia rubra · B. Lochia serosa · C. Lochia alba · D. Leucorrhoea — **B**
Trap: the timing (day 4-10) separates serosa from rubra and alba.

G15 · Tier 2 · one-liner · concept
Division of the zygote 9-12 days after fertilization produces:
A. Dichorionic diamniotic twins · B. Monochorionic diamniotic twins · C. Monochorionic monoamniotic twins · D. Conjoined twins — **C**
Trap: each neighbouring time window gives the neighbouring option.

G16 · Tier 1 · one-liner · recall
The best ultrasound parameter for gestational age in the first trimester is:
A. Biparietal diameter · B. Crown-rump length · C. Head circumference · D. Abdominal circumference — **B**

G17 · Tier 2 · vignette · diagnosis
A newborn has weak lower-limb pulses and strong upper-limb pulses. Diagnosis?
A. Transposition of great arteries · B. Coarctation of aorta · C. Tetralogy of Fallot · D. Ebstein anomaly — **B**

**Pre- and para-clinical**

G18 · Tier 1 · one-liner · recall
The artery palpated between the medial malleolus and the tendo calcaneus is the:
A. Anterior tibial · B. Posterior tibial · C. Dorsalis pedis · D. Popliteal — **B**

G19 · Tier 3 · vignette · lesion -> structure
During removal of a fish bone stuck in the pyriform fossa, a nerve is injured. Which nerve?
A. Recurrent laryngeal · B. Glossopharyngeal · C. Internal laryngeal · D. External laryngeal — **C**
Trap: two steps (the nerve lies under the mucosa of the pyriform fossa), with the other laryngeal nerves as neighbours.

G20 · Tier 1 · one-liner · physiology
The formula UV/P represents renal:
A. Filtration · B. Tubular secretion · C. Tubular reabsorption · D. Clearance — **D**

G21 · Tier 3 · calculation · physiology
If the radius of an artery falls to one-third, its resistance increases:
A. 9 times · B. 18 times · C. 27 times · D. 81 times — **D**
Trap: resistance varies with 1/r⁴, not 1/r² or 1/r³, and every option is a plausible power.

G22 · Tier 1 · one-liner · biochemistry
Zellweger syndrome is a disorder of:
A. Lysosomes · B. Peroxisomes · C. Mitochondria · D. Ribosomes — **B**

G23 · Tier 2 · one-liner · mechanism
Deficiency of which vitamin causes lactic acidosis?
A. Thiamine · B. Riboflavin · C. Niacin · D. Biotin — **A**
Trap: all are B-complex cofactors of energy metabolism; only thiamine blocks pyruvate dehydrogenase.

G24 · Tier 2 · vignette · diagnosis (Pathology)
A 5-year-old has an eye lesion; histology shows Flexner-Wintersteiner rosettes. Diagnosis?
A. Retinoblastoma · B. Optic nerve glioma · C. Rhabdomyosarcoma · D. Ocular melanoma — **A**

G25 · Tier 2 · vignette · organism
Profuse vomiting without fever starts 3 hours after a picnic meal of pre-packed salad and milk. Most likely organism?
A. Clostridium perfringens · B. Salmonella · C. Staphylococcus aureus · D. Bacillus cereus — **C**
Trap: B. cereus also causes early vomiting, but it is linked to fried rice.

G26 · Tier 3 · vignette · drug -> ADR -> treatment
A patient on haloperidol develops acute dystonia. Next best step?
A. Give benztropine · B. Switch to clozapine · C. Give fluphenazine · D. Increase the haloperidol dose — **A**

G27 · Tier 2 · negative one-liner · drug choice
Which of the following is NOT used for hypertension in pregnancy?
A. Methyldopa · B. Labetalol · C. Nifedipine · D. Enalapril — **D**

G28 · Tier 2 · vignette · management (Forensic Medicine)
A factory worker has headache, vomiting and blurred vision after drinking local spirit. Treatment?
A. Fomepizole · B. Flumazenil · C. N-acetylcysteine · D. Naloxone — **A**
Trap: every option is a real antidote for a different poisoning.

G29 · Tier 2 · scenario · finding
A family dies in a closed room filled with smoke from a wood fire. The body is likely to show:
A. Cherry-red hypostasis · B. Cyanosis · C. Blackish discoloration · D. Brown pigmentation — **A**

**Eye, ENT, skin, radiology, anaesthesia**

G30 · Tier 2 · vignette · lesion localization
A child has had a right eye that is down and out, with ptosis, since birth. Which nerve palsy?
A. Third · B. Fourth · C. Sixth · D. Seventh — **A**

G31 · Tier 1 · one-liner · recall
The utricle and saccule detect:
A. High-frequency sound · B. Low-frequency sound · C. Linear acceleration · D. Angular acceleration — **C**
Trap: angular acceleration belongs to the semicircular canals.

G32 · Tier 2 · negative one-liner · recall
Koebner phenomenon is seen in all of the following EXCEPT:
A. Psoriasis · B. Lichen planus · C. Vitiligo · D. Herpes simplex — **D**

G33 · image form · identification
Identify the instrument shown. / Identify the structure marked in the image. / The radiograph of the patient is shown below. Most likely diagnosis?
Form only: image items name the task in a few words and let the picture carry the finding.

G34 · Tier 1 · one-liner · recall
The recommended lead-equivalent thickness of a protective apron for radiology workers is:
A. 0.5 mm · B. 0.75 mm · C. 1 mm · D. 2 mm — **A**

G35 · Tier 2 · one-liner · device
The oxygen delivery device that gives a fixed FiO₂ regardless of the patient's breathing pattern is the:
A. Nasal cannula · B. Simple face mask · C. Venturi mask · D. Non-rebreathing mask — **C**

What the gallery shows:
- Most stems are one short sentence or a two-line scenario.
- Most traps are the neighbouring row of the same table (schedule, level, time window, related programme or antidote).
- "EXCEPT" items list true members of one list plus one outsider.
- Tier 3 is a short two-step item, not a long case.

---

# 1C. QUESTION PATTERN LIBRARY

Build questions from these real FMGE lead-in patterns, choosing the ones your PDF's facts fit. Fill each blank only with a fact the PDF supports.

Direct recall (Tier 1):
- "[Programme/scheme] was launched in:" · "[App/portal] is used for:" · "The strain/diluent/route of [vaccine] is:"
- "[Condition] is caused by / associated with:" · "Most common [site/cause/type] of [X] is:"
- "[Sign/eponym] is seen in:" · "The formula [X] represents:" · "Normal value of [parameter] is:"
- "WHO/national definition of [X] is:" · "Drug of choice for [X] is:" · "Identify the [instrument/structure/specimen] shown." (image)

Discrimination (Tier 2):
- "[2-3 clues]. Most likely diagnosis?" · "[Finding] is characteristic of:"
- "[Scenario]. This is which level of prevention / type of study / type of surveillance?"
- "[Scenario with one timing/age/status detail]. The correct schedule/dose/action is:"
- "All of the following are [members of a list] EXCEPT:" (about 1 item in 20)
- "Investigation of choice / confirmatory test for [X] is:" · "[Drug] is contraindicated in:"
- "The first step in managing [X] is:" · "[Parameter A] vs [parameter B]: which is true?"

Two-step (Tier 3):
- "[Clues] ... Next best step?" (recognize, then act)
- "[Drug] causes [effect]. Treatment?" or "[Clue] -> which structure is injured?"
- "[Numbers]. The [rate/ratio/volume] is:" (the formula must be in the PDF; give every number)
- "[Value] per 1,00,000. Has [threshold] been reached?" (unit conversion plus a recalled threshold)
- "Which of the following is contraindicated in [state]?" (the learner must recall both the property and the rule)

Wording habits: plain English, Indian terms (ANM, ASHA, PHC, UIP, ₹, lakh), numbers in options in ascending order, no "all/none of the above", and no reference to any study material.

---

# 2. WHAT AN FMGE QUESTION LOOKS LIKE

FMGE difficulty comes from medical discrimination: a decisive clue, a mechanism, choosing the right investigation or management step, interpreting an image/graph/waveform/instrument, or combining one or two concepts.

It does NOT come from long stems, obscure trivia, ambiguous wording, two defensible answers, linguistic tricks or double negatives. A hard FMGE question is usually **compressed**: roughly 1-4 short sentences, at most about 55 words.

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

1. **Stand-alone stem.** The stem must read as an exam question. It must never mention or point at the study material: no "in the notes", "shown in the source", "according to the PDF/table/figure/slide", "the schedule displayed", "as annotated", "the source identifies…", "on page…". Test the fact itself: write "The diluent used to reconstitute BCG vaccine is:", not "Which diluent is shown for BCG?". Page citations belong only in the answer key. The words **listed, specified, mentioned, stated** point at the notes even without naming them: write "The preferred method of refuse disposal is:", not "The preferred method listed for refuse disposal is:"; "Which biological control agent is used?", not "Which biological control is listed?".
2. **No stated premise.** The stem must not hand over the fact that decides the answer. Bad: "Measles vaccine given within 3 days of exposure is protective. A child exposed 48 hours ago… best action?" Good: "An unvaccinated 14-month-old had household contact with measles 48 hours ago. Best action?" If an item can only be solved once the stem states the key fact, it is reading comprehension: reject it or make it Tier 1 recall of that fact.
3. **"Shown" only with an image.** Use "shown", "displayed" or "depicted" only when the item carries an image (section 10).
4. **One question, one task.** End with a clear lead-in ("Most likely diagnosis is:", "Next best step is:", "Which of the following…?").
5. **Compression.** For every sentence ask: can it go without losing the discriminator? If yes, delete it. Age, sex and occupation appear only when they discriminate.
6. **Negatives sparingly.** Real FMGE has about 5% negative stems: aim for about 1 in 20 items, "EXCEPT/NOT" in capitals, never double negatives.
7. **Time anchors.** A historical, programme-status or version-dependent fact needs a time or version qualifier that the PDF supports ("Under the 2016 switch…"), or it is excluded.
8. **Name the population, product or version, but only from the PDF.** When the answer differs by age group, population, product, programme or guideline version, the stem must pin it down using what the PDF itself gives:
   - A qualifier the PDF states: "As per its licensed schedule, Cervavac at 13 years is given as:". The PDF gives Cervavac's own schedule next to the WHO SAGE 1-2 dose range.
   - The figure the PDF shows, when it names no group: "The Anemia Mukt Bharat IFA tablet shown contains:", with the notes' photo of the red tablet.
   - If the PDF gives neither, exclude the item. Never add a population, product or version from memory; that turns the item into E3.
9. **Named authorities are fine; the notes are not.** "According to the Biomedical Waste Management Rules 2016…", "Under the UIP…" or "As per WHO…" are normal FMGE wording when the PDF supports that framework. "According to the notes/source/table" is never allowed.
10. **Length.** Real stems: median about 20 words, vignettes about 30, and almost none over 55. Keep one-liners at 15 words or fewer.

---

# 4. OPTION RULES (hard rules)

- Exactly four options, A-D, one best answer; all options homogeneous (same category, grammatical form and unit style).
- No "all of the above", "none of the above", "both A and B" or combined-letter options.
- No duplicate or near-duplicate options; no two options that are both defensible.
- **Length parity**: the correct option must not regularly be the longest or the most qualified. Across each section, the correct option is the unique longest in no more than about a third of items.
- Distractors come from the same neighbourhood: same disease family, drug class, adjacent management steps, competing investigations, nearby anatomical structures, similar organisms, related complications. A Tier 2/3 distractor should often be right in a nearby scenario but wrong for this stem.
- Every distractor must be plausible **for the setting in the stem** (no walk-in cooler offered for a subcentre outreach session, no tertiary procedure for a field-level question).
- No joke options, irrelevant organ systems, grammatical giveaways or repeated absolute words.
- **Numeric options in ascending order** (doses, years, rates, ranges), as FMGE papers print them.
- **One relationship per item.** No "Which pair/combination correctly gives X and Y?" items that join two unrelated recalls. Only use a matched pair when the pairing itself is the fact being tested (e.g. vaccine -> diluent).
- **Distractor truth check.** Every distractor must be wrong under current guidance too, not merely absent from the PDF. Before accepting an item, check each distractor for:
  - an accepted range that includes it (VIA uses 3-5% acetic acid, so 3% cannot be a distractor to 5%);
  - an old name or synonym of the answer (*Bacillus subtilis* var. *niger* is the old name of *B. atrophaeus*);
  - another real value for the same thing (915 MHz is also a microwave-treatment frequency, so it cannot be a distractor to 2,450 MHz);
  - a neighbouring term the stem also fits (blood-pressure, glucose and vision tests at one visit are multiphasic, but arguably also multipurpose or mass screening);
  - a second option that the stem's wording also satisfies ("Which vitamin is scarce in breast milk?" fits vitamin K as well as vitamin D).
  If any check hits, replace the distractor or tighten the stem.
- **No common-sense giveaways.** Each distractor must tempt a candidate who half-knows the topic. If a layperson could reject it without medical knowledge ("Stop the school meal", "Slow, costly testing"), replace it.
- **Answer-letter balance**: within each section each letter is correct in 20-30% of items, with no run of more than 3 identical letters and no visible pattern. Balance letters by ordering the options **before** writing the answer key; after any reordering, rewrite that item's key heading, closest-distractor letter and explanation. A 6/7/7/8 split is fine. Never move a key to even out a count.

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

SCOPE GATE: a number or rule keeps the exact scope of its source row. If the PDF gives 1,200°C for incinerating **cytotoxic drugs**, the stem must say cytotoxic drugs, not "biomedical-waste incineration". Check the row heading, the population and the product before writing the stem.

OUTCOME GATE: when the PDF claims a clinical benefit ("early breastfeeding reduces postpartum haemorrhage"), check that the evidence supports the outcome itself. If only the mechanism is established (suckling -> oxytocin -> uterine contraction), test the mechanism and do not key the unproven outcome.

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

The exclusion set is: the PDF's own solved questions, every question already generated in this conversation, any QUESTION-DNA LEDGER or bank I paste in, and the gallery in section 1B (plus any further real questions I paste). If I say earlier blocks exist but have not pasted their ledger, ask for it before generating; never claim cross-block deduplication you cannot check.

Question DNA = concept + direction tested + stem archetype + correct-answer relationship + viewer page(s).

A pasted bank or ledger from another session is calibration input only: it may reveal uncovered concepts, archetypes or missed visuals, never examinable facts. Verify and remap its page numbers against this PDF before relying on them; an item without a verifiable page still belongs in the exclusion set.

Reject a candidate when:

1. knowing an existing answer directly reveals the new answer;
2. it asks the opposite, exception, negative or converse of the same relationship;
3. the same option set works with minor edits;
4. the disease -> fact relationship is unchanged despite a reversed stem;
5. only age, sex, numbers, chronology or presentation changed cosmetically;
6. a learner who memorized the old item without understanding the topic could answer the new one.

BANK COHERENCE. The app pools every section and draws fresh mixed mocks from the whole bank, so **any two items may appear together**. Every rule below applies across all sections, not only within one:

- No stem, option **or teaching explanation** may contain another item's answer or deciding fact. Explanations count because practice mode shows them straight after each answer: "800 kcal, higher than the 600 kcal for pregnant women" gives away the pregnant-women item. For example, a calculation that states "vitamin A solution 1 lakh IU/mL" gives away a recall item asking that strength. State the number differently, or drop one of the two.
- No two items on the same micro-fact, even from different directions (e.g. "carrier holds 16-20 vials" and "which device for 16-20 vials").
- Do not reuse an option set: two items must not share three or more options.
- One table row is one micro-fact, whichever item it is asked from. "Metallic implants -> blue" and "contaminated glass vials -> blue" test the same row; "LBW is below 2.5 kg" and "2.4 kg, above the 10th centile -> LBW" test the same cutoff.
- Use each figure once. Two items on the same symbol or photograph (identify it; act on it) count as one micro-fact.
- **Pattern cap across the bank:** at most 2 items per pattern on one table or topic. Seven "disease -> vector" items from one vector table, or three "unit of light" items, break it: pick the two highest-yield rows and leave the rest.
- Give every unit a short **micro-fact key** (for example `BMW colour: blue row`, `light units`, `vector table`, `water hardness`) in the UNIT INVENTORY and the DNA ledger. Two units with the same key, or the same pattern past its cap, are merged or cut **at plan time**, so sections keep their planned size.

Reusing a topic needs a different competency (identification -> management, mechanism -> expected finding, investigation -> interpretation, equipment -> operational decision, schedule recall -> patient-specific selection). Two items may share a disease only if they test different competencies. A dense page may yield several items with different DNA; a thin page may yield none.

---

# 8. THREE TIERS

Assign the tier by the **minimum cognitive operations needed**, not by stem length. A wrapper, long stem or calculation does not raise a tier. After writing each item, challenge it: if one memorized fact solves a Tier 2/3 item, downgrade it; if a Tier 3 item needs an unstated third fact, reject it as E3.

**TIER 1 - Direct / recognition** ("I studied this.")
Mainly E0; one source relationship answers it; direct fact, classic presentation, straightforward image identification, association, or a clearly taught treatment/investigation. Plausible same-category distractors, no artificial trick.

**TIER 2 - Discriminative application** ("I know both possibilities; one clue makes one better.")
E0-E1; exactly one meaningful discrimination or inference; at least two genuinely plausible source-supported options; one decisive discriminator (initial vs definitive, screening vs confirmatory, similar drugs/organisms, adjacent structures, most likely vs merely possible, timing/lab/imaging distinction). If one memorized line answers it without the discriminator, it is Tier 1.

Field and programme subjects (Community Medicine, Forensic Medicine) follow the same tiers:
- Tier 1: "The diluent for BCG vaccine is:"
- Tier 2: "Detention of healthy contacts until the maximum incubation period is:", where quarantine must be told apart from isolation.
- Tier 3: "8 prevalent leprosy cases per 1,00,000 population indicates:", which needs a unit conversion and the elimination threshold.

**TIER 3 - Compressed two-step application** ("The answer was not a sentence in my notes, but the concepts to derive it were.")
E1-E2; two distinct source-supported propositions, both necessary, **both recalled by the learner rather than printed in the stem**; concise stem. Forms: finding -> diagnosis -> expected finding; diagnosis -> next investigation/management; drug action -> change -> adverse effect; lesion -> structure -> deficit; image -> diagnosis -> next step; two PDF concepts -> necessary inference. For each E2 item record Fact A (page X), Fact B (page Y) and the conclusion; reject if A alone answers it, B is decorative, or an unstated Fact C is needed.

HARD LIMIT: Tier 3 is the hardest source-supported FMGE-style item a well-prepared candidate can solve in about a minute. Not a long USMLE case, not super-specialty, not a three-guideline memory test. Prefer two hops; three only when every component is clearly taught.

---

# 9. BANK SIZE, SECTIONS AND MIX

**The PDF sets the size, but only its FMGE-relevant content counts.** There is no default question count. Do not start from a round number such as 20, 25, 50 or 100 and fill it. Notes contain far more testable facts than FMGE asks about; a bank that tests every one is a bank of trivia. Instead:

1. Build the **UNIT INVENTORY** (section 12, Part 1): a numbered list of distinct examinable units. A unit is one fact, relationship, table row, visual or two-fact link that can carry an item passing every gate in this prompt. Merge units that would test the same micro-fact; drop units that fail a gate (and say which gate).
2. **Name the FMGE pattern for every unit**: the gallery item (G number, section 1B) or pattern-library lead-in (section 1C) that a question on it would follow. **If you cannot name one, FMGE does not ask that kind of fact: the unit is Low yield.**
3. **Grade the yield** of every unit:
   - **High**: the chapter core FMGE asks repeatedly (see "Where the questions fall", section 1A): definitions and classifications, "most common" / "of choice", classic signs, associations and eponyms, standard formulas and indices, stable schedules and programme components, landmark facts, classic images and instruments.
   - **Medium**: standard textbook detail a well-prepared candidate is expected to know, especially the neighbouring row or look-alike that FMGE uses as the close distractor.
   - **Low** (never generated): institute-specific mnemonics and teacher remarks; one-year survey figures (a single NFHS/SRS value, a current count); minor dates, committee members and sequence trivia; brand names and packaging detail; state or local schemes; facts under revision; super-specialty or NEET-PG-only depth; any fact that only this PDF would ask about.
4. **Apply the topic budget.** Follow FMGE's breadth: across the bank, no chapter-level topic gets more than about 8 items per 50, and no single pattern repeats within a topic more than twice (at most two "launched in", two schedule-row or two "most common" items on the same programme, disease or table). Year and date items stay under about 10% of the bank; calculations about 5-10% where the PDF supports them. A PDF that is mostly one chapter therefore gives a smaller bank, not a deeper one.
5. **N = all High units + the Medium units that fit the budget.** Read N off the list; do not round it. If N comes out at exactly 50, recount the inventory before using it.
6. Never pad (padding produces stated premises, glued pairs and joke distractors). Never generate a Low unit to reach a size.

**Sections.** A real FMGE section is at most 50 questions in 50 minutes, so 50 is a **ceiling per section, not a target**:

- N ≤ 50: one section of N questions.
- N > 50: k = N / 50 rounded up sections of near-equal size (e.g. 64 -> 32 / 32, 120 -> 40 / 40 / 40, 137 -> 46 / 46 / 45).
- Each section samples the whole PDF: spread every topic's units across the sections in proportion, as a real section mixes topics. Do not make one section per chapter.
- Each section on its own meets the tier, stem-form, negative-stem and answer-letter targets, so it works as a stand-alone timed mock (1 minute per question).
- Number questions from Q1 in every section.

**Stop after the plan.** Deliver Part 1 (ingestion report, unit inventory, bank plan) and then write `PLAN READY — reply "go" to generate Section 1`. Generate no questions until I reply. I may reply with changes (a different count, topics to drop) instead.

If I ask for a specific count or a single section, follow that instead and say what the PDF could have supported.

**Tier targets per section** (a training design, not an official FMGE difficulty distribution):

- Clinical and image-led subjects: Tier 1 / 2 / 3 = about 30% / 40% / 30%.
- Recall-heavy subjects (Community Medicine, Physiology, Biochemistry, Anaesthesiology, Forensic Medicine), where real FMGE is mostly direct recall: about 40% / 40% / 20%.

If the PDF cannot sustain the target honestly, deliver the honest counts and say so. Never inflate a tier; a real Tier 3 needs two facts the learner recalls, not facts printed in the stem. (For example, a Community Medicine section tiered honestly may come out near 46% / 38% / 16%.)

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
4. **Size and plan the bank** (section 9): write the unit inventory with an FMGE pattern and yield for every unit, apply the topic budget, take N from it, fix the sections, allocate units to sections, write the BANK PLAN, and stop for my "go".
5. **Calibrate**: before drafting, note which gallery items (section 1B) match this subject and level, and which patterns (section 1C) the PDF's facts fit.
6. **Candidates**, one section at a time: for each inventory unit allocated to the section, draft one or two candidate DNAs (two where the unit supports different directions) before writing full items; for each note page(s), concept, competency, tier, archetype, answer relationship, closest distractor and discriminator. If a unit yields no candidate that passes QC, replace it with an unused High or Medium unit from the inventory, or deliver the section one item short and say so; never invent a filler item.
7. **Adversarial QC** of every candidate. Reject or rewrite anything that fails:
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
   11. image item has a real, answer-free figure;
   12. key integrity: re-read each key heading against the options exactly as printed. The letter matches the option text, the closest-distractor letter and text match, and the explanation argues for the keyed option, not another one;
   13. explanation hygiene: no "listed", "specified", "here", "the notes/handout/page", and no editorial caveat ("should not be presented as…", "excluded from the options", "this does not make…"). Truth-gate caveats go in the audit's Truth validation line.
8. **Write** the accepted items, recheck them against the gallery level, and deliver the section. Then the next section, against the ledger of every earlier one: before drafting a section, list the micro-fact keys and pattern counts already used; after writing it, confirm no key repeats and no pattern passed its cap. Report any collision in the audit instead of shipping it.

Do not expose private chain-of-thought; give concise teaching reasoning only.

---

# 12. OUTPUT CONTRACT (exact format - it is parsed automatically)

Deliver the parts in this order. Use these headings **exactly**. Do not add answers, tiers-in-stem, bold text or commentary inside the question section.

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

# UNIT INVENTORY
| # | Page(s) | Topic | Unit (fact or relationship, a few words) | Micro-fact key | FMGE pattern (G no. or 1C lead-in) | Yield | Best tier | Image? | Use |
|---|---|---|---|---|---|---|---|---|---|
| 1 | p.12 | Cold chain | Vaccine carrier: capacity and ice packs | carrier capacity | "[Equipment] holds:" | High | 1 | no | yes |
| 2 | p.14 | Cold chain | VVM stages -> use or discard | VVM stage | G-style image identification | High | 2 | yes | yes |
| 3 | p.15 | Cold chain | Brand of ILR used in one state | ILR brand | none | Low | - | no | no |
| … | | | | | | | | | |

Rejected units (failed a gate): <unit — gate>, one per line, or none.

# BANK PLAN
- Units: High <n> · Medium <n> (used <n>, cut by budget <n>) · Low <n> (not used)
- Items per topic, against the budget:
- Bank size N: <number of rows marked Use = yes>
- Sections: <k> (<size of each>)
- Per section: topic spread, and Tier 1 / 2 / 3 targets

PLAN READY — reply "go" to generate Section 1

(After "go":)

# SECTION 1 OF <k> — <n> QUESTIONS

# QUESTION BANK — SECTION 1

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

(The Q16 and Q36 tier starts are illustrative; number continuously according to your actual tier counts.)

Format rules for the question section:

- The question heading is exactly `### Q<number>` with nothing else on the line. Number continuously from Q1 within each section.
- Each section starts with `# SECTION <s> OF <k> — <n> QUESTIONS` and contains Parts 1-3 for its own questions (question bank, answer key, audit and ledger). The ingestion report, unit inventory and BANK PLAN appear once, before Section 1, followed by the stop.
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
- The teaching explanation is the only plain paragraph. It is shown to students, so write it as teaching, not as an audit note. Never write "listed", "specified", "here" or "the notes/handout"; state the fact itself ("Hydroclaving operates at about 132°C", not "Hydroclaving is listed at 132°C").
- No citation markers, links or tool artefacts (for example `:contentReference[...]`, `【…】`) anywhere in the reply. Validation sources are named in words in the audit. Do not add textbook enrichment, external mechanisms, timing rules or guidelines merely because they are true.

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
- Level check: for 3 generated items, one each from Tiers 1-3, name the closest gallery item (G number) and say in one line why the level matches:
- Images needing answer masking:

# QUESTION-DNA LEDGER
| Q | Tier | Concept | Micro-fact key | Direction tested | Archetype | Answer relationship | Pages |
|---|---|---|---|---|---|---|---|
| 1 | 1 | … | … | … | … | … | … |
```

Audit rules: the audit covers the section just delivered; report only counts you can read off it. Do not print "0 ambiguous questions" or any other pass claim you did not actually check item by item. The DNA ledger is how later sections and later blocks avoid repeats, so fill every row; label rows S<s>-Q<n>.

DELIVERY: if the reply would be cut off, stop at the end of a complete question or answer-key entry and write `CONTINUE FROM Q<n>`. When I reply "continue", resume with exactly the next item and the same headings. Do not restart or renumber.

At the end of every section except the last, write `END OF SECTION <s> OF <k> — reply "next section"`. When I reply, start the next section with its `# SECTION` heading. After the last section write `BANK COMPLETE — <N> questions in <k> sections` and list any planned units you dropped, with the reason.

---

# 13. SIMULATION MODE

If I request SIMULATION MODE: produce the same output contract (tier headings are still required for the parser, and the app mixes the tiers when it builds the section). Spread subjects by the blueprint, follow each subject's section 1A stem form, aim at the whole-paper task mix (diagnosis ~35%, fact recall ~28%, management ~14%, investigation ~11%, mechanism ~8%), and write strictly for one-minute decisions.

---

# 14. DEFAULT SETTINGS

Target: FMGE · four-option single best answer · bank size = High + in-budget Medium units of the UNIT INVENTORY (no default, no padding, no round numbers, no Low-yield trivia) · topic budget ~8 per 50 and ≤2 of one pattern per topic · plan first, then STOP for "go" · sections of at most 50 (a ceiling, not a target) · tier mix per section 30/40/30% (recall-heavy subjects ~40/40/20%)
Direct questions: PRESERVE · short clinical framing: WHERE IT DISCRIMINATES · image items: REAL FIGURES WHEN THE PDF SUPPORTS
Stand-alone stems (no reference to notes/source): REQUIRED · stated premises in stems: FORBIDDEN · population/product/version named when the answer depends on it: REQUIRED
Stem form: MATCH THE SUBJECT PROFILE (section 1A) · negatives ~5% · stems at or under ~55 words
Bank coherence across ALL sections (no give-aways in stems, options or explanations; no shared option sets; one item per micro-fact key and per figure; ≤2 items per pattern): REQUIRED
Distractor truth check (ranges, synonyms, other real values, neighbouring terms) and scope/outcome gates: REQUIRED · key integrity re-read after any option reordering: REQUIRED
Option parity, ascending numeric options and answer-letter balance: REQUIRED · all/none of the above and pair/combination items: FORBIDDEN
Existing PDF solved questions and earlier blocks: STRICT SEMANTIC EXCLUSION
Printed text, clear handwriting, tables, diagrams: USE
External examinable knowledge: OFF · external truth validation: VETO/QUALIFY ONLY
Rendered-page authority for scanned PDFs · HIGH-confidence annotation linkage: REQUIRED
Cross-page inference and Tier 3 two-step synthesis: ON · long-vignette inflation: OFF
Answers beside questions: OFF · teaching explanations: ON · viewer-page citations: REQUIRED
Audit: CHECKABLE COUNTS ONLY · hallucination tolerance: ZERO

BEGIN: report the session capability check, ingest and map the complete accessible PDF, then generate. Do not write Question 1 until the concept ledger, exclusion set and coverage matrix are complete.
