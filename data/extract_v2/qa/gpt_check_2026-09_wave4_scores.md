# Independent cross-check, wave 4 — studies the main sweep never reached

The sweep's worklist required a percentage, so a study whose rows carry none was never in it. It covered 306 of the 315 studies the corpus held when it ran (baseline `v1.7.14`); this wave reads what it skipped.

A different model family, one fresh session per paper, wave 3's instructions verbatim, the paper text and nothing else: no sight of our coding. Rows are matched on the value within a paper, since two coders word the same measure differently.

Scored against `data/extract_v2/estimates_v1.7.21_frozen.csv`, over 2 studies.

| | rows |
|---|---|
| matched on value | 7 |
| construct agrees | 7 |
| denominator base agrees | 7 |
| **candidate omissions** (a proportion the freeze does not hold) | **0** |
| the freeze carries, GPT did not | 0 |

## Row by row

| study | value | construct (ours / theirs) | denominator base (ours / theirs) | our measure |
|---|---|---|---|---|
| `105026630069` | 6 | CONTENT / CONTENT | 100 / 100 | % of videos coded inaccurate (content items) |
| `85136545530` | 33.8 | RECALL / RECALL | 589 / 589 | recall-sharing: % of past-month political-news sharers who amplified exaggerated |
| `85136545530` | 14.8 | RECALL / RECALL | 589 / 589 | recall-sharing: shared news that was exaggerated, and was not aware of this |
| `85136545530` | 9.9 | RECALL / RECALL | 2005 / 2005 | recall-sharing: % of UK social media users who in the past month shared exaggera |
| `85136545530` | 8.8 | RECALL / RECALL | 589 / 589 | recall-sharing: shared news that seemed accurate at the time but was later found |
| `85136545530` | 7.6 | RECALL / RECALL | 589 / 589 | recall-sharing: shared news the respondent thought was made up when they shared  |
| `85136545530` | 2.5 | RECALL / RECALL | 589 / 589 | recall-sharing: shared news that was exaggerated, and was aware of this |

## To adjudicate

Nothing. The second coder proposed no prevalence proportion the freeze does not hold, and the freeze carries none it missed.

## What the second coder considered and rejected

| study | figure | why |
|---|---|---|
| `105026630069` | 74% | Positive attitude toward sunscreen, not misinformation prevalence. |
| `105026630069` | 35% | Videos classified as accurate; this is not prevalence of misinformation. |
| `105026630069` | 2% | Videos classified as mixed accuracy; the paper does not define this category as misinformation or quantify its misinformation share separately. |
| `105026630069` | 57% | Opinion-based or not applicable for factual accuracy evaluation; not equivalent to misinformation prevalence. |
| `105026630069` | 40%, 31%, 2% | Global Quality Score categories, measuring content quality rather than misinformation prevalence. |
| `105026630069` | 27% | Promotional content, an adjacent construct rather than misinformation prevalence. |
| `105026630069` | 18% | Creators identifying as health care professionals, a creator characteristic rather than misinformation prevalence. |
| `105026630069` | 85% | Videos containing sunscreen product recommendations, not misinformation prevalence. |
| `105026630069` | 71% | Videos receiving poor or below-average quality scores, measuring quality rather than misinformation prevalence. |
| `85136545530` | 25.4% | Regression effect size: a one-unit increase in Instagram use for news, not a prevalence estimate |
| `85136545530` | 53.6% | Regression effect size for identity-performative motivations, not a prevalence estimate |
| `85136545530` | 27.1% | Regression effect size for ideology, not a prevalence estimate |
| `85136545530` | 61.2% | Regression effect size for negative affect, not a prevalence estimate |
| `85136545530` | 46%, 27%, 13%, 11% | Background figures cited from another source about worldwide platform use for news, not this paper's own results |
| `85136545530` | 65.5%, 29.4%, 5.1% | Political-news-sharing status and missingness, not misinformation prevalence |
| `85136545530` | 66.2% | Respondents who did not report amplifying exaggerated or false news; not a positive misinformation prevalence estimate |
