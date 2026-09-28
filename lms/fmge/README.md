# FMGE quiz layer

This module keeps FMGE-specific content and import logic separate from Frappe Learning's core quiz implementation.

## Current section

`psm_block_1.json` is a 50-question Community Medicine/PSM section generated from the reviewed `research/pdf_extracted_questions_data/Day2_PSM_combined.md` bank.

It maps the FMGE-style section to native Frappe records:

- `LMS Question` for reusable single-best-answer questions;
- `LMS Quiz` for the 50-question timed section;
- 50 minutes;
- 1 mark per question;
- one attempt per imported mock;
- 50% practice threshold for this mock (not an official FMGE sectional qualifying rule);
- no negative marking;
- no live answer reveal;
- fixed question order;
- Frappe's existing question navigation and Mark for Review UI.

Generate or validate the packaged bank:

    python3 scripts/fmge/build_question_bank.py
    python3 scripts/fmge/build_question_bank.py --check

`--check` also prints a one-line summary of the FMGE style lint. The currently live PSM block predates the lint and still reports its known style errors; it builds unchanged.

## Making a new or replacement block

1. Run the v6 prompt (`research/fmge-source-material/analysis/prompt-calibration.md`) in a web session that can see the PDF's page images, and save the whole reply as `research/pdf_extracted_questions_data/<Source>_combined.md`. The prompt's output contract is exactly the Markdown this builder parses.
2. Crop each `**Image source:** p.N | …` figure and paste the printed lines under it:

       uv run scripts/fmge/extract_pdf_image.py --page N --preview /tmp/page.png   # pick the box
       uv run scripts/fmge/extract_pdf_image.py --page N --crop L,T,R,B --name psm-b2-q012 --alt "…"

   Images land in `lms/public/fmge/images/` and are served from `/assets/lms/fmge/images/`. The build fails while any `**Image source:**` line has no `**Image:**` line.
3. Lint, fix every ERROR (send it back to the same web session or edit by hand), then build strictly (tiers are mixed through the section by default, as in the real exam; `--order source` keeps Markdown order):

       python3 scripts/fmge/build_question_bank.py --source <md> --lint
       python3 scripts/fmge/build_question_bank.py --source <md> --strict

   The lint blocks stems that point at the notes ("shown in the notes", "according to the source"), stems that state the deciding fact, duplicate options and all/none-of-the-above. It warns on long stems, a correct option much longer than its distractors, a skewed or streaky answer key, and a block with no image items. For a new block, also pass `--bank-id`, `--id-prefix`, `--title` and `--subject`.
4. Keep the reply's `# QUESTION-DNA LEDGER` and paste it into the next session so the next block does not repeat questions.

Replacing PSM Block 1 in place: keep the default `--bank-id fmge-psm-block-1` and `--id-prefix PSM-B1`, then rerun the installer below. Questions are matched by `PSM-B1-Q###`, so each number's content is overwritten.

Builder tests: `python3 -m unittest scripts/fmge/test_build_question_bank.py`.

Once this app is installed in a Frappe Bench/site, create the quiz and its native course lesson with:

    bench --site <site> execute lms.fmge.importer.install_psm_block_1

The importer reconciles by stable FMGE IDs, never by quiz title alone. Re-running it updates the quiz settings, question order, stems, options, answer keys, source metadata, tier/difficulty metadata, and teaching explanations to match the packaged bank. A legacy stem-only question is claimed only when it is already in the ID-matched quiz and its type, four options, and answer key match.

Teaching explanations are stored in the dedicated `LMS Question.fmge_explanation` field instead of the correct option's `explanation_N` field. For quizzes with `show_answers = 0`, the learner quiz API also omits all option-explanation fields, so explanation presence cannot reveal the keyed option during an attempt. After submission, FMGE result rows snapshot the correct answer and explanation; the completed-attempt page shows the correct answer for wrong responses and the teaching explanation for both correct and wrong responses.

## Image question source convention

Image metadata belongs in the Markdown source, immediately before the A-D options:

    **Image:** /files/fmge/example.png
    **Image alt:** Chest radiograph showing the relevant finding

The builder carries those lines into `image_url` / `image_alt` in the generated JSON. The importer accepts public Frappe/app asset paths under `/files/` or `/assets/` and appends the image to the rich-text question stem. Manual edits to generated JSON are intentionally overwritten by regeneration.

## Taking the mock

The installer creates a published `FMGE Mock Exams` course, a Community Medicine chapter, and a lesson with Frappe Learning's native quiz block. Signed-in students can enroll and take the quiz through the normal course flow. The installer preserves that placement on rerun.

Anyone can instead open `/lms/fmge/mock` and take this section without signing in, even on a site that keeps the rest of the LMS behind a login. This public route reuses Frappe Learning's quiz screen and serves only questions from the published FMGE bank. It offers two modes:

- **Practice**: no timer. After choosing an option, the learner can check it straight away and see whether it was right, the correct answer, the teaching explanation, and the page in the Day 2 PSM notes with a link that opens the PDF at that page.
- **Timed mock**: exam conditions for the quiz duration. Nothing is revealed until the attempt is finished.

Both modes allow first/last navigation, Mark for Review, and finishing from any question, and end with a per-question review (with a "only mistakes" filter) showing the same explanation and page reference. Answers are scored on the server. Anonymous results are not saved and the mock can be retaken freely. The link works for other people only when the Frappe site is hosted on a network-accessible domain; `fmge.localhost` is local to each person's own computer.

The notes PDF is served from `lms/public/fmge/day2-psm-notes.pdf`, a symlink to `research/pdf_extracted_questions_data/Day2_PSM_combined.pdf`, so page references in the bank (`p.60`, `pp.78–79`) are PDF page numbers.

The public copy is served through a Cloudflare Tunnel; see [HOSTING.md](HOSTING.md) for the setup, what must be running, and how to change it safely.

This is currently a 50-question PSM section, not a complete 300-question FMGE exam.
