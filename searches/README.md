# searches/ — queries and run dates, not retrieved records

Every database query is a parameterised script in `scripts/` and every run was logged with its
date. What is here is the **query string, the run date and the result count** for each run:

- `scopus_query_log.tsv` — one row per Scopus run: UTC timestamp, name, total results, query.
- `query_log.md` — the OpenAlex and PubMed runs, with their terms and counts.
- `tune_search_*.json` — the search-tuning comparison behind the final Boolean (query variants,
  corpus size, recall caught/indexed). No records.
- `recall_check_*.json` — the seed-paper recall check: per seed, the identifier query, whether
  the seed was indexed, whether the search caught it, and the verdict.

**The retrieved records themselves are not redistributed.** Scopus results fall under Elsevier's
API terms, and the OpenAlex/PubMed dumps are full record payloads. Re-run the query strings above
against the same databases to regenerate them; counts are only reproducible as of the run date,
which is why every date is recorded. `data/identifiers/included_studies.csv` gives the identifier
and DOI of every included study so the corpus itself can be re-retrieved from source.
