# RA validation — instructions (misinformation prevalence review)

## What this is
We are systematically reviewing how common misinformation is in people's information environments. You will independently code a random sample of **60 items** to validate our coding. **Code blind**: do NOT look at our decisions — read each paper and decide yourself. We compare afterward (your codes vs ours, and if two RAs, against each other).

## Files
- `RA_coding_sheet.csv` — the 60 items. Fill the four `RA_...` columns. (If two RAs: each takes a fresh copy, code independently, do not confer.)
- PDFs are in the project `PDFs/` folder; open the file named in the `pdf_file` column.

## The constructs (assign ONE per estimate)
- **CONTENT** — % of content items that are false/misinfo, vs a NEUTRAL denominator (a topic/keyword/popularity/random/whole sample). e.g. "12% of vaccine tweets were false."
- **EXPOSURE** — % of a person's information *diet* that is misinfo. e.g. "0.15% of people's news diet."
- **REACH** — % of *people* who encountered/visited/shared misinfo **>=1 time** in a period (needs a time window). e.g. "44% visited >=1 untrustworthy site."
- **SHARING** — observed/behavioural sharing (% of actors who share, or % of shared content that is misinfo).
- **RECALL** — *self-reported* (survey) seeing/sharing misinfo. (sub-note exposure vs sharing if you can.)
- **CONCENTRATION** — share of exposure/sharing by the top X% of the AUDIENCE/users (not by sources/creators).
- **QUALITY** — accuracy/usefulness/reliability ratings (e.g. DISCERN, GQS) — NOT the same as falsity. (We exclude these from prevalence.)
- **OTHER** — none of the above.

## The KEY rule — sampling-frame neutrality (decides keep vs drop)
An estimate is a real prevalence ONLY if the sample was drawn NEUTRALLY (by topic / keyword / popularity / random / full census). 
**DROP (not a prevalence)** if any of these:
- The sample was selected BY misinformation status (e.g. "we collected 300 known-false posts / fact-checked items / rumors" -> any % is circular).
- It measures QUALITY/reliability, not falsity; or STANCE/sentiment (e.g. "anti-vaccine", "negative tone") rather than false vs true.
- It is source/website-level (rating outlets), not content people see.
- It is composition WITHIN misinfo (e.g. "43% of the false posts were about vaccines").
- It is concentration among CREATORS/sources (not the audience), or relative virality ("false spreads faster").

### IMPORTANT clarifications (added 2026-07-14 — these caused confusion in the first RA round)
- **CONCENTRATION is an EXCEPTION to "within-misinfo → drop".** If a study reports how concentrated
  the AUDIENCE/user behaviour is — "the top X% of users account for Y% of the misinfo exposure/sharing"
  — that is a **KEEP** (construct = CONCENTRATION), *even when the sample is misinfo-only*. The
  within-misinfo drop rule applies only to CONTENT prevalence, not to concentration. Requirement: the
  estimate must give BOTH the group size (e.g. "1% of users") AND the share (e.g. "→ 70% of exposures").
  A bare "35 accounts = 28.6%" with no population size is not usable — note it and flag.
  (Concentration among *producers/creators* only, with no audience/user denominator, still drops.)
- **Specific populations are KEPT, not dropped.** Estimates about politicians/elites, or professionals
  (pharmacists, physicians), or a defined panel are valid — just note the population in RA_notes. We tag
  and report them separately from the general public; do not drop them for being non-general.
- **Content-falsity within a misinfo-source sample:** still DROP from the main analysis, but note it —
  we retain these for a brief appendix analysis, so flag them rather than discarding silently.
- **Definitional strictness is interesting to us:** if a paper gives several figures under stricter vs
  broader definitions (e.g. "entirely false" 27% vs "contains any misinfo" 79%; source-level vs
  content-level), record them ALL and say which is which — the spread across definitions is a key output.
- **Quality ≠ misinformation** (reinforced): DISCERN/GQS/mDISCERN reliability scores are NOT misinfo.
  "Lacks source attribution" or "no reference to uncertainty" are quality flaws, not false content.
- **Prefer one estimate you are 100% sure of** over many uncertain ones — but keep genuinely distinct,
  clearly-reported country/platform/topic/definition breakdowns.

## How to code each row
1. Open the `pdf_file`. Find the statistic.
2. **RA_value_correct(Y/N)**: does the `reported_value` match what the paper actually says? (For `type=dropped_study`, leave blank.)
3. **RA_construct**: which construct is it? (your independent call from the list above)
4. **RA_keep(Y/N)**: is it a genuine prevalence estimate with a NEUTRAL denominator (Y), or should it be dropped per the rules above (N)? For `type=dropped_study` rows, we found NO valid estimate — put **Y** if you AGREE there's no usable prevalence (i.e., agree to drop), **N** if you think there IS one we missed (and say what in notes).
5. **RA_notes**: anything unclear, or the correct value/construct if you disagree.

## One or two RAs?
- **Two is better**: gives a human inter-rater reliability (kappa) — the strongest validation. Two RAs code the SAME 60 items independently (separate copies, no conferring).
- One RA is sufficient for the core check (your codes vs our frozen codes).
Return the filled CSV(s); we compute agreement (and kappa) automatically.

Thank you — this ~2-3h of coding is what lets us report a human-validated reliability figure.
