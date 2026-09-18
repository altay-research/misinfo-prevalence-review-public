# Systematic grey-literature protocol (2026-06-22)

Supersedes the ad-hoc producer scan. Grey lit is coded as a **parallel track** (NOT pooled
with peer-reviewed estimates) and reported as a structured comparison.

## Source frame (pre-specified producer list, 4 categories)
1. **Fact-checkers & monitors:** IFCN signatories, Duke Reporters' Lab, Poynter, Snopes,
   FullFact, AFP Factuel, Maldita, Africa Check, Duke Tech&Check.
2. **Regulators & IGOs:** Ofcom (UK), ACMA (AU), EU Commission/EDMO, UNESCO, OECD, WHO
   (infodemic), Eurobarometer, FCC/FTC.
3. **Academic & think-tank centres:** Reuters Institute (Digital News Report), Oxford
   Internet Institute/ComProp, Stanford Internet Observatory, Shorenstein, Data & Society,
   Pew Research, RAND, Knight Foundation.
4. **Advocacy & platform transparency:** Avaaz, ISD, CCDH, Global Disinformation Index,
   NewsGuard, Meta/Facebook, X/Twitter, TikTok, YouTube transparency & "widely-viewed" reports.

## Method
- Search each producer's site + Google with: `<producer> (misinformation OR disinformation
  OR "fake news" OR "false news") (prevalence OR exposure OR reach OR engagement OR share OR
  "how much")`. Record the search string and access date per claim.
- No date bound. English. Include only documents stating a QUANTITATIVE claim.
- For each claim record: producer, category, year, claim_text (verbatim figure), number,
  denom_class, method, url, access_date.
- `denom_class` includes **REACH_ABSOLUTE** (raw counts with no denominator) — a category
  largely unique to grey lit and itself a finding.

## Use in the paper
Grey lit is a **case study in the denominator problem**, not a pooled estimate set:
the contrast between advocacy "X billion views / 65% of content" framing and platform/
behavioural "0.05–0.15% of views" measures is the exhibit (CCDH vs Meta).
Output: data/grey/grey_master.csv (deduped across the ad-hoc + systematic passes).
