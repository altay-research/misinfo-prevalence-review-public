# Wave 5 — scores and the adjudication of every disagreement

38 estimates across the 22 studies no cross-family pass had read, coded blind in one fresh session
of a different model family, on the SWEEP's instrument (construct, definitional breadth, denominator
class from the reported quantity and the paper's own definition). With these, the cross-family check
reaches every study in the released corpus.

| dimension | n scored | raw agreement | κ | for comparison: the 647-row sweep |
|---|---:|---:|---:|---|
| construct | 38 | 97.4% | **0.959** | 0.802 |
| definitional breadth | 26 | 88.5% | 0.761 | 0.477 |
| denominator class | 17 | 41.2% | 0.183 | 0.469 |

Construct is the dimension the paper reports and it is the strongest of the three, here and in the
sweep. Denominator class is the weakest, here and in the sweep, and wave 5's 17 scoreable rows are
too few for the κ to carry weight on its own: ten of them are ONE definitional boundary, argued
below, and a single boundary decided the other way would move the figure most of the way back.

## Every disagreement, ruled against the source

Fourteen rows. The independent coder's call was adopted on one, ours upheld on twelve, and one is a
genuine boundary case left open for the author.

| row | study | dimension | ours | theirs | ruling |
|---|---|---|---|---|---|
| W50022 | `W7117302408` | breadth | false | misleading | **theirs adopted** |
| W50023 | `W7162938155` | denom_class | curated_sample | topical | **open — author's call** |
| W50036 | `W7171843315` | construct | CONTENT | OTHER | ours upheld, flagged |
| W50018 | `W4409319996` | breadth | misleading | false | ours upheld |
| W50025 | `W7166447493` | breadth | false | misleading | ours upheld |
| W50008-10 | `W4306960737` | denom_class | curated_sample | topical | ours upheld |
| W50018 | `W4409319996` | denom_class | curated_sample | topical | ours upheld (tie-break) |
| W50021 | `W4417119300` | denom_class | curated_sample | topical | ours upheld |
| W50029/31/33/35 | `W7170181457` | denom_class | curated_sample | topical | ours upheld |

**W50022 — breadth on `W7117302408`, theirs adopted.** We coded the 69% exposure figure as `false`.
The paper's operative sentence is "About 69% of respondents indicated that **misleading or false**
information circulating on social media platforms created confusion regarding the [NIN-SIM] policy",
under a table row labelled "Exposure to misinformation and fake news". A band that admits misleading
content is `misleading`, not `false`, and the paper names both. This is the catch the wave was for.

**W50023 — denominator class on `W7162938155`, left open.** 5,385 TikTok and Facebook comments
crawled through Apify, "restricted to discussions about the Prabowo-era government in Indonesia".
There is no rank truncation and no seeding from known misinformation, which is what rule 4 asks for,
so the reading turns entirely on whether a national government is ONE issue (`topical`, their call)
or a domain spanning several unrelated issues (`curated_sample`, ours, and what the instructions'
own "prefer the narrower category" tie-break gives). Both readings are defensible from the paper.
One row, on the moderator that sits at the bottom of the variance ladder.

**W50036 — construct on `W7171843315`, ours upheld and flagged.** The denominator is 480 OBSERVED
FACE-TO-FACE interactions between community health workers and community members during home visits,
41.3% of which carried a health-misinformation claim. Under the denominator-sets-construct rule this
is a share of communication events each individually judged, which is what CONTENT means, and the
row is coded `unit = item`, `classification_level = claim_level`, `ground_truth = researcher_coding`
consistently with that. Their `OTHER` reflects a fair discomfort: every other CONTENT study in the
corpus counts posts, videos or articles, and this one counts conversations that were never online.
It is 1 of 275 CONTENT studies and moves no median, but a reader may reasonably ask whether an
offline observational study belongs in this pool at all. **For the author.**

**W50008-10, W50021 — rank truncation, ours upheld.** `W4306960737` takes "the FIRST 120 videos
returned by a default-relevance YouTube search for 'kidney cancer'" out of more than 4,000 returned;
`W4417119300` takes those of "the FIRST 200 results" for a Portuguese keyword that also fall between
one and fifteen minutes. The instructions are explicit that rank truncation defines the set itself
and makes it `curated_sample`, and both sets are rank-truncated before any topic filter is applied.

**W50029/31/33/35 — a researcher relevance filter, ours upheld.** `W7170181457` is coded on two
denominators on purpose: four rows on the whole hashtag retrieval and four on the subset the authors
judged to be about alopecia areata treatment, with the other 75 (of 98) and 170 (of 222) excluded.
The disputed four are the SUBSET rows, where the set exists because researchers decided which videos
counted. The whole-platform rows are a different question and are not in dispute.

**W50018 — both dimensions, ours upheld.** The denominator is the 21 of 34 retrieved sources that
happened to cover away rotations, a topic-conditional subset of an already hand-assembled set of
TikTok, Reddit and SDN sources; the tie-break gives `curated_sample`. On breadth, the paper's own
word for the material is that it "can be misleading", and advice that contradicts a professional
guideline is not thereby false.

**W50025 — breadth, ours upheld.** The accuracy test is whether an audio file actually contains the
Hz value its title promises, measured by Fourier analysis. That is a hard factual check, so `false`
is right even though the items are also, in the ordinary sense, misleading.

## A finding this wave produced that is not a disagreement

Twenty-one of the 38 rows could not be scored on denominator class because OUR OWN cell is empty.
Across the whole freeze 39 main-set rows have `denom_class` and `denom_type` blank, and every one of
them is a late arrival: 21 from the behavioural-arm search and 18 from the blind re-extraction. They
all carry `denom_scope`, so the gap is a field that was never filled rather than a judgement that
was never made. In the regression those 36 rows (of 839) become `denom_fine = "unspecified"` and
`denom = "other"`, a bucket that exists for no substantive reason. See the research log for the
decision this is waiting on.
