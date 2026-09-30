# Day 3 PSM corrections

Updated on 2026-09-30. The saved Day 3 bank already includes earlier corrections
to overlapping screening options, the unsupported 400 IU vitamin D rewrite,
microwave distractors and the breastfeeding outcome claim. This update repairs
the remaining teaching and audit issues without discarding distinct valid facts.

| Item | Correction | Source |
| --- | --- | --- |
| S3-Q7 | Preserved the conditional incineration threshold in the explanation. Incineration above 1,200°C is a permitted route, not a requirement that every cytotoxic drug use that route. | PDF pp.70–71; national IPC guidelines, Annex 5 |
| S4-Q21 | Specified metal recovery through an authorized foundry and explained the shredding/mutilation step for that pathway. Other permitted disposal routes are not ruled out. | PDF p.69; national IPC guidelines, Annex 5 |
| S4-Q20 | Removed the blanket assertion that screening is always less accurate than diagnostic testing. Retained quick/inexpensive initial screening and subsequent diagnostic assessment. | PDF pp.37–38 |
| S2-Q15, Q22, Q26; S3-Q15, Q16, Q22, Q25 | Reclassified single-relationship recognition from Tier 2 to Tier 1. Updated tier blocks, answer-key archetypes, ledgers and packaged difficulty metadata; retained IDs and tested facts. | Each item's existing PDF citation |
| S1-Q8, Q9 | Reordered nonnumeric options and rebuilt key/distractor letters to remove a four-answer run introduced by the revised tier interleaving. Tested relationships and answers are unchanged. | PDF pp.71, 90 |
| All sections | Recomputed tiers, answer distributions, unique-longest correct options, negative stems and structural stem-form counts from final items. Earlier counts are superseded. | Final Markdown and generated banks |

The conditional disposal alternatives were checked against the Government of
India's [National Guidelines for Infection Prevention and Control in Healthcare
Facilities, Annex 5](https://cdn.who.int/media/docs/default-source/searo/india/antimicrobial-resistance/ipcguidelines-web-sep2020.pdf).
The sharps table includes encapsulation as an alternative to shredding or
mutilation; the PDF-only question tests the metal-recovery route taught on p.69.

## Final bank and checks

After the v9.5 additions below, the pool contains 129 questions in sections of
34 / 32 / 32 / 31. Final Tier 1 / 2 / 3 counts are 76 / 40 / 13. The public mock
no longer draws a random 54-question attempt: like Days 1 and 4, each section is
now a fixed mock (`/lms/fmge/day3/mock?section=N`). Four sections are kept (v9.5
would allow three at 50 each) so live bank IDs, quiz names and links stay stable.

Audits use explicitly defined mechanical stem categories: image first, then the
builder's vignette rule, then a 15-word one-liner cutoff, with the remainder
classified as longer direct. These are reproducible format counts, not an
independent measure of cognitive difficulty. Unique-longest counts use cleaned
option-text character lengths and list the question IDs.

Strict builds and key/option matching checks passed for all four sections.
One advisory remains: S4-Q12 and S4-Q13 share several vector options while
testing different disease–vector relationships. They are retained as distinct
coverage. The existing vector group limits their concentration within a mock.

This is a targeted correction of identified defects. Changed source-dependent
wording was checked against rendered source material; the earlier full-source
review is recorded in the bank's reference-verification section. This update
does not claim a new independent medical revalidation of all 106 original items.

## v9.5 gap review (2026-10-01)

A v9.5 pass over the PDF found 135 candidate High/Medium units; 23 passed the
gates and were added (S1-Q29–Q34, S2-Q29–Q34, S3-Q29–Q34, S4-Q29–Q33). They cover
disaster-management ministry, hospital noise limits, intellectual-disability
bands, minus-desk design, positive predictive value, problem-village criteria,
International Day for Disaster Risk Reduction, noise thresholds, classroom area norms, I-131,
mammography, Bhopal, Renuka Ray committee, medical X-ray exposure, auditory
fatigue, Down syndrome and BRCA1 screening.

Excluded: questions solved in the PDF itself (p.58, 133–134, 136–138), gallery duplicates
(p.4, 122), items failing the truth gate (p.15, 20, 94, 119, 121), and pages too
thin to support a question (p.18–19, 47, 74–75, 108). New items were checked
against the rendered pages only; no live web verification was run. Concept groups
keep related new items (ID bands, noise, problem village, breast screening,
classroom area) from clustering in one mock.
