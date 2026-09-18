# Human validation round 3 — 2026-08-24

Two blind validation tasks answering the external methodological review's strongest requests:
a human check of title screening and a human check of full-text eligibility. Samples are
random, stratified, and **blind**: the pipeline's decisions are not shown, and the worksheets
and answer keys live outside this folder (`data/extract_v2/qa/round3_keys/` — do not open
while coding). Sacha and Laura code the SAME items independently, giving human-vs-pipeline
error rates AND human-vs-human agreement.

**How to code: open your two HTML pages in a browser** — `code_A_<name>.html` and
`code_B_<name>.html`. Full coding rules (when to INCLUDE / MAYBE / EXCLUDE) are in the box at
the top of each page — they are the pipeline's own screening criteria, verbatim from
`docs/screening_criteria.txt`. Pages autosave in the browser, show progress, link each Task B
paper to its local PDF, and export the `*_FILLED.csv` the scorer reads.

## Task A — title screening (200 titles, ~15–25 min)

The page shows ONE title at a time (with its journal): press 1 / 2 / 3 on the keyboard (INCLUDE / MAYBE / EXCLUDE — or click) and it advances automatically; arrows navigate back; the coloured strip jumps anywhere. Note: the pipeline screened from titles only, so the journal is extra context the machine did not have; we report that when scoring. When in doubt → MAYBE, never EXCLUDE
(the pipeline's recall-protective rule). The sample is stratified (150 pipeline-EXCLUDE,
25 MAYBE, 25 INCLUDE) and shuffled, so position and frequency reveal nothing.

## Task B — abstract screening (60 records, ~45 min)

Same one-at-a-time screener as Task A, with the abstract displayed under the title. With an
abstract you can be decisive: INCLUDE if the study clearly reports a quantitative estimate,
MAYBE only if it genuinely stays open. Keys 1 / 2 / 3.

## Task C — full-text eligibility (50 studies: 25 includes + 25 full-text-stage drops; the longest task, do it last)

The paper opens INSIDE the page (PDF pane on the left; open-in-tab fallback if your browser
refuses the embed). Press 1 / 2 (INCLUDE / EXCLUDE); a note is optional (arrow back to add one).
The question: does the paper report a usable quantitative estimate — a proportion with a stated
denominator — of misinformation prevalence, exposure, sharing, reach, recall, or concentration?
Rows are pre-shuffled, so stopping after the first 20 or 30 rows still yields an unbiased random
subsample — code strictly in order.

## Task D — grey-literature claims (30 claims, ~20 min)

Each card shows one verbatim quantitative claim from a fact-checker, regulator, think tank,
advocacy organisation, or platform report. From the text alone, pick what the number IS
(exposure share, content share, keyword-topical share, recall, concentration, or an absolute
count with no denominator). Click to code; no PDFs needed.

## When done

Click the Download button on each page (produces `*_FILLED.csv`), save the files into this
folder, and tell Claude "round 3 done" — scoring (sensitivity/specificity vs the pipeline,
κ between coders, adjudication queue for disagreements) is scripted from the keys.

Note for Laura: the folder is self-contained — send her the whole `round3_2026-08` folder
(HTML pages + `papers/`, ~70 MB) and both tasks work on any machine.
