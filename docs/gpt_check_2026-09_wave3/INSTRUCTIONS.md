**Your task: read the paper at the bottom of this message and extract its quantitative
estimates according to the rules below. Return the JSON object described under "Output" as a
downloadable file named `<paper_id>.json` (the paper_id is given below the instructions). If you
cannot produce a file, print the JSON in the chat and say so. Either way: the JSON only — no
preamble, no commentary, no explanation around it.**

# Blind extraction — misinformation prevalence review, wave 3

You are extracting quantitative estimates from research papers for a systematic review. You have not
seen anyone else's coding of these papers and you should not try to guess it. Extract what the paper
says.

**Use one fresh session per paper.** Do not carry context between papers.

## What counts as an estimate

A number is in scope when it is a **quantitative estimate, with a denominator, of one of these six
constructs**. The denominator decides the construct — ask "a share of WHAT?", not what the numerator
is called.

| Construct | The denominator is | Example |
|---|---|---|
| CONTENT | items in a defined content sample | 12% of sampled tweets were false |
| EXPOSURE | content a person saw or consumed | 1.1% of the median user's viewed content |
| REACH | people | 39% of panellists visited at least one untrustworthy site |
| SHARING | observed real-world shares | 2% of shared URLs were false |
| RECALL | survey respondents, self-reporting | 56% said they had seen false news |
| CONCENTRATION | a top-N or top-X% group's share of the total | top 20% of users got 76% of exposure |

## What does NOT count

- Belief in, or susceptibility to, misinformation. Believing something false is not encountering it.
- Hypothetical or experimental sharing intentions ("would you share this?").
- Detection or classifier accuracy.
- Effect sizes, regression coefficients, correlations, odds ratios, variance decompositions.
- Composition WITHIN misinformation (which platform referred it, which topic it was about).
- Numbers the paper cites from ANOTHER paper. Only this paper's own results.
- Counts with no denominator ("1.3 billion views").
- Labels that a wholly TRUE item could carry — "AI-generated", "extremist", "hyperpartisan",
  "conspiracy theme". Flag these as `adjacent_construct` rather than extracting them as prevalence.

## Rules on values

- Copy the value **exactly as printed**. Never compute a complement (if the paper says 34% did not,
  do not write 66% did), never sum across categories, never round.
- An exact part/whole from two printed numbers IS allowed (paper says N=2131 of 3240 → 65.8%),
  but say so in `notes`.
- If the value is a bound ("less than 0.01%", "14% or more"), set `value_kind` to `bound` and record
  the printed figure.
- If it is a mean count or a duration rather than a share, set `value_kind` to `not_a_proportion`.
- `source_quote` must be a **contiguous verbatim span** from the text containing the number.
  No ellipses, no stitching two sentences together. This is checked mechanically.

## Output

**Save your answer as a downloadable file named exactly `<paper_id>.json`** — the paper_id is given
just below the instructions, e.g. `scholar_01.json`. If you cannot produce a file, print the JSON in
the chat instead and say so; either way the content must be the JSON object below and nothing else.

Reply with JSON only, no prose around it:

```json
{
  "paper_id": "...",
  "eligible": true,
  "eligibility_reason": "one or two sentences",
  "estimates": [
    {"construct": "EXPOSURE", "value": "1.1", "value_kind": "proportion",
     "denominator": "all content the median Facebook user saw in 2020",
     "measure": "share of viewed content from untrustworthy sources",
     "misinfo_definition": "how THIS paper defines the bad content",
     "country": "US", "platform": "Facebook", "period": "Aug-Sep 2020",
     "source_quote": "contiguous verbatim sentence containing the number",
     "notes": ""}
  ],
  "considered_but_excluded": [
    {"figure": "68.8%", "why": "channel composition within untrustworthy exposure, not prevalence"}
  ]
}
```

`considered_but_excluded` matters as much as `estimates`. It is how we tell a number you judged out
of scope from a number you did not see.

If the text is truncated (`"truncated": true`), say so in `eligibility_reason` and extract what is
present.
