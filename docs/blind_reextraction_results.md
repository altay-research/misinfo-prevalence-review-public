> **HISTORICAL, and exempt from the counts drift check (banner added 2026-09-07).** This is the
> pre-repair blind pass — 33 of the 283 full-text studies in the June 2026 corpus, at freeze v1.6.x.
> Its counts describe that corpus, not the released freeze v1.7.16, which is why
> `scripts/make_counts_crosswalk.py` lists it in `ARCHIVAL`. Kept because manuscript §4.8 cites
> this row of the reliability table. The repair's own blind re-extraction is a separate,
> later check (`docs/corpus_repair_2026-09/REPAIR_REPORT.md` §5).

# Blind 10% re-extraction (independent error-rate check)
Seeded random 10% sample (33 of 283 full-text studies). Fresh agents re-extracted from the PDFs with NO access to the frozen coding, applying the protocol + L1-L49.
- Prevalence-inclusion agreement: ~32/33 (97%). (4 raw keep/drop differences; 3 are QUALITY-bucket rows already excluded from the prevalence headline, so not prevalence disagreements; 1 genuine: 2-s2.0-85127622287 CONTENT 3.3% — defensible either way, frozen keeps it.)
- Per-study finding reproduction: 26/29 co-kept studies (90%) had >=1 frozen value reproduced within tolerance.
- Construct agreement on value-matched estimates: 32/34 (94%).
- Estimate-level value reproduction 65% is a conservative floor: most "misses" are granularity (blind gave one pooled row where the frozen set splits per-platform / per-narrative), not value errors. Matched values agreed within +-0.6pp / 5%.
Conclusion: the frozen coding is independently reproducible at the finding level (90%) with high construct agreement (94%); no systematic value errors detected.
