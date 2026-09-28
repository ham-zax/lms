# Question-level extraction schema

One row/object should represent one reconstructed question or one clearly separable recalled item.

## Provenance

- `question_id` - stable local ID
- `canonical_session` - normalized sitting ID after alias verification
- `source_session_label` - provider's original month/year label
- `source_provider`
- `source_document`
- `source_question_number`
- `source_page`
- `source_evidence_class` - O/R1/R2/R3/R4/R5
- `duplicate_group`
- `source_confidence` - low/medium/high

## Content classification

- `subject`
- `topic`
- `subtopic`
- `stem_type` - direct / short-clinical / long-clinical / statement / image-led / calculation
- `question_archetype` - recall / diagnosis / investigation / management / mechanism / consequence / anatomy-localization / interpretation / calculation / other
- `image_based` - boolean
- `image_type` - radiology / pathology / dermatology / anatomy / instrument / graph / waveform / other
- `negative_stem` - boolean
- `cross_subject` - boolean
- `reasoning_hops` - 0 / 1 / 2 / 3+
- `stem_word_count`

## Option/difficulty structure

- `option_count`
- `distractor_closeness` - low / medium / high
- `closest_distractor_type`
- `discriminator_type` - age / timing / anatomy / lab / imaging / mechanism / management-order / specificity / other
- `difficulty_observed` - direct / moderate / hard
- `difficulty_reason` - concise coded reason, not subjective prose only

## Answer/quality fields

- `provider_answer_present`
- `provider_answer`
- `answer_verified` - no / partial / yes
- `answer_verification_source`
- `ambiguous` - boolean
- `notes`

Do not store a large copyrighted question corpus in derived reports. Pattern-analysis outputs should primarily contain classifications, counts, short identifiers, and independently written summaries.
