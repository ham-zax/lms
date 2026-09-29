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

1. In a web session whose model can see the PDF's page images, upload the notes PDF and paste `research/fmge-source-material/analysis/prompt-calibration.md` (everything below its first line). The prompt is self-contained: it includes the measured FMGE pattern, a gallery of real recalled questions with levels and traps, and a pattern library. Optionally paste extra real questions for the subject below it (`python3 scripts/fmge/reference_set.py --subject "Community Medicine"` draws about 15 from the local recall corpus; `--seed N` gives a different set). The session first lists every examinable unit in the PDF (UNIT INVENTORY), sets the question count to that list's length, and stops; check the plan and reply "go". It then delivers the bank as sections of up to 50 questions, each headed `# SECTION s OF k`; reply "next section" to get each one. Save the whole thread's reply as `research/pdf_extracted_questions_data/<Source>_combined.md`. Its output contract is exactly the Markdown this builder parses.
2. Crop each `**Image source:** p.N | …` figure and paste the printed lines under it:

       uv run scripts/fmge/extract_pdf_image.py --page N --preview /tmp/page.png   # pick the box
       uv run scripts/fmge/extract_pdf_image.py --page N --crop L,T,R,B --name psm-b2-q012 --alt "…"

   Images land in `lms/public/fmge/images/` and are served from `/assets/lms/fmge/images/`. The build fails while any `**Image source:**` line has no `**Image:**` line.
3. Lint, fix every ERROR (send it back to the same web session or edit by hand), then build strictly (tiers are mixed through the section by default, as in the real exam; `--order source` keeps Markdown order):

       python3 scripts/fmge/build_question_bank.py --source <md> --lint
       python3 scripts/fmge/build_question_bank.py --source <md> --strict

   The lint blocks stems that point at the notes ("shown in the notes", "according to the source"), stems that state the deciding fact, duplicate options and all/none-of-the-above. It warns on long stems, a correct option much longer than its distractors, a skewed or streaky answer key, and a block with no image items. For a new block, also pass `--bank-id`, `--id-prefix`, `--title` and `--subject`. The question count and timer (1 minute per question) come from the file; `--expected N` makes the build fail on any other count. When the file holds several sections, build each one separately as its own block:

       python3 scripts/fmge/build_question_bank.py --source <md> --section 2 --bank-id fmge-psm-block-2 --id-prefix PSM-B2 --title "FMGE PSM Mock 1 - Section 2" --output lms/fmge/data/psm_block_2.json

   The installer and public mock currently serve only PSM Block 1, so extra sections need an installer entry before students can take them.
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

The installer creates a published `FMGE PSM Day 2` course at the existing `/lms/courses/fmge-mock-exams` URL, a Day 2 PSM Practice chapter, and a lesson with Frappe Learning's native quiz block. Signed-in students can enroll and take the quiz through the normal course flow. The installer preserves that placement and URL on rerun.

Anyone can instead open `/lms/fmge/mock` and take this section without signing in, even on a site that keeps the rest of the LMS behind a login. This public route reuses Frappe Learning's quiz screen and serves only questions from the published FMGE bank. It offers two modes:

- **Practice**: no timer. After choosing an option, the learner can check it straight away and see whether it was right, the correct answer, the teaching explanation, and the page in the Day 2 PSM notes with a link that opens the PDF at that page.
- **Timed mock**: exam conditions for the quiz duration. Nothing is revealed until the attempt is finished.

Both modes allow first/last navigation, Mark for Review, and finishing from any question, and end with a per-question review (with a "only mistakes" filter) showing the same explanation and page reference. Answers are scored on the server. Anonymous results are not saved and the mock can be retaken freely. The link works for other people only when the Frappe site is hosted on a network-accessible domain; `fmge.localhost` is local to each person's own computer.

The notes PDF is served from `lms/public/fmge/day2-psm-notes.pdf`, a symlink to `research/pdf_extracted_questions_data/Day2_PSM_combined.pdf`, so page references in the bank (`p.60`, `pp.78–79`) are PDF page numbers.

The public copy is served through a Cloudflare Tunnel; see [HOSTING.md](HOSTING.md) for the setup, what must be running, and how to change it safely.

This is currently a 50-question PSM section, not a complete 300-question FMGE exam.

## Day 3 compact course

`lms.fmge.day3_course.install_day3_psm_course` imports the four Day 3 section banks as a 106-question pool and creates one course lesson, **FMGE PSM Day 3 Mock**. The course page links to `/lms/fmge/day3/mock`, which works without signing in while the course is published.

Each new page load or **Try Again** draws 54 questions from the full pool: 27 Tier 1, 21 Tier 2, and 6 Tier 3. The tier slots follow a fixed repeating pattern, while the questions within each tier change. The other 52 questions are set aside for that attempt. Timed and practice modes grade only the selected questions; a signed selection token binds the answer request to that draw. Results are anonymous and not saved.

On the local bench, start the services described in [HOSTING.md](HOSTING.md), then run:

    /home/hamza/repo/AVO/frappe-bench/env/bin/python -m frappe.utils.bench_helper frappe --site fmge.localhost execute lms.fmge.day3_course.install_day3_psm_course

Run that command from the bench's `sites/` directory. The local mock is `http://fmge.localhost:8000/lms/fmge/day3/mock`. The source bank is `research/pdf_extracted_questions_data/Day3_PSM.md`; page links open the matching Day 3 PDF.
