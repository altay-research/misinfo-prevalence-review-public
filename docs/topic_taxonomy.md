# Topic taxonomy — misinfo prevalence review (Phase B moderator)

One PRIMARY topic per study (the subject-matter domain of the misinformation studied).
Assign the single best fit. Use `general_news` for broad/whole-diet studies with no single subject.

| code | scope |
|---|---|
| `covid19` | COVID-19 pandemic broadly — disease, origins, treatments, masks, lockdowns, **and COVID-19 vaccines** |
| `vaccines` | Vaccines NOT centred on COVID (childhood/HPV/MMR, general vaccine hesitancy) |
| `health_other` | Non-COVID, non-vaccine health/medical (cancer, ADHD, dermatology, oral/dental, epilepsy, diet/nutrition, mental health, reproductive health, drugs) |
| `politics_elections` | Elections, election integrity, partisan/political misinformation, government, candidates, political scandals |
| `climate_environment` | Climate change, environment, energy |
| `war_geopolitics` | Armed conflict, war, foreign influence operations, geopolitics (e.g. Russia–Ukraine, NATO, state propaganda) |
| `immigration` | Immigration, migrants, refugees |
| `science_other` | Non-health science/technology (GMO, evolution, 5G, nuclear, space, AI/ChatGPT as a subject) |
| `crime_society` | Crime, terrorism, race, gender, social/cultural issues |
| `economy_finance` | Economy, finance, crypto, markets, business |
| `general_news` | **No single subject** — whole-diet / untrustworthy-domain-list / general news-quality / cross-topic studies where misinfo is measured across all news, not one topic |
| `other` | Niche specific subject not above (e.g. herpetology/wildlife, celebrity, sports, a specific consumer product) |

## Coding rules
- **Primary topic only.** If a study spans two, pick the dominant; if it is genuinely broad news
  with no dominant subject → `general_news` (do NOT force a subject onto whole-diet studies).
- COVID **vaccines** → `covid19` (not `vaccines`). Non-COVID vaccines → `vaccines`.
- A study about "untrustworthy domains / fake-news domains / NewsGuard sites" **in general**
  (not restricted to a topic) → `general_news`.
- Preserve an `existing_topic` if present and correct; only override if clearly wrong.
- Anchor every code to a short evidence phrase from the provided context or the full text.

## Output (JSON to the path in your dispatch prompt)
```
{"batch":K,"topics":[
  {"id":"<study id>","topic":"<one code from the table>","confidence":"high|medium|low",
   "evidence":"<short phrase justifying the topic>","note":"<optional: multi-topic / uncertainty>"}
]}
```
Code EVERY study in your slice; never skip one. Read the full text (text_path) when the short context is ambiguous.
