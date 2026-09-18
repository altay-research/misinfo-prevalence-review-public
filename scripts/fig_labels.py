#!/usr/bin/env python3
"""fig_labels.py — the one map from coded values to the prose used on figure labels.

Every figure generator reads its categories straight out of the freeze, whose values are
snake_case codebook levels (`crime_society`, `self_perceived`, `web_cross_platform`). Those are
internal identifiers, not English, and any level missing from this map used to be printed raw in
the rendered SVG. The map lives here, in one file, so a level added to the codebook is given a
human label once and every figure picks it up.

`pretty()` is the only accessor: it falls back to the raw value, so a new codebook level still
renders rather than crashing, and `missing()` reports anything a figure drew without a label.

Covers: topic, ground_truth, classification_level, sampling_frame, breadth, denominator scope and
the residual platform codes (real platform names come from phaseB_platform_construct's
`labels_for`, and country names are already prose; neither goes through this map).
"""

import re

PRETTY = {
    # --- topic -------------------------------------------------------------
    "health_other": "Health, non-COVID",
    "covid19": "COVID-19",
    "vaccines": "Vaccines",
    "general_news": "General news",
    "politics_elections": "Politics, elections",
    "war_geopolitics": "War, geopolitics",
    "science_other": "Science, other",
    "crime_society": "Crime, society",
    "economy_finance": "Economy, finance",
    "climate": "Climate",
    "other": "Other",

    # --- ground truth (who decided the item was false) ----------------------
    "researcher_coding": "Researcher coding",
    "domain_list": "Domain list",
    "NewsGuard": "NewsGuard",
    "fact_checker": "Fact-checker",
    "classifier": "Classifier",
    "self_report": "Respondents themselves",

    # --- denominator scope --------------------------------------------------
    "topical": "Topical corpus",
    "population": "Whole population",
    "political_news": "Political news",
    "news_diet": "News diet",
    "all_media": "All media",
    "n/a": "Not applicable",

    # --- sampling frame -----------------------------------------------------
    "panel_trace": "Panel of tracked users",
    "full_census": "Full census",
    "keyword_topical": "Keyword or topic sample",
    "survey_sample": "Survey sample",
    "random_platform": "Random platform sample",
    "convenience": "Convenience sample",
    "convenience_snowball": "Convenience or snowball sample",
    "curated_seed": "Curated seed set",
    "purposive": "Purposive sample",

    # --- definitional breadth ----------------------------------------------
    "fabricated": "Fabricated only",
    "false": "False",
    "misleading": "Also misleading",
    "unreliable_source": "Unreliable source",
    "low_quality": "Low quality",

    # --- identification level ----------------------------------------------
    "claim_level": "Claim or item level",
    "post_level": "Post level",
    "topic_level": "Topic level",
    "source_level": "Whole source",
    "self_perceived": "Respondent's own judgement",
    "mixed": "Mixed",

    # --- platform residual codes (named platforms come from labels_for) ------
    "multi_platform": "Multiple platforms",
    "web_cross_platform": "Web, cross-platform",
    "survey": "Survey question frame",
}

_UNLABELLED = set()
# A codebook level is all-lowercase with underscores; anything with a capital or a space is
# already a display string (a platform or country name) that legitimately passes through.
_CODE = re.compile(r"^[a-z][a-z0-9_]*$")


def pretty(value, empty="Not stated"):
    """Prose label for a coded value. Unlabelled codebook levels are recorded by missing()."""
    if value is None or str(value).strip() == "":
        return empty
    value = str(value).strip()
    if value not in PRETTY:
        if _CODE.match(value):
            _UNLABELLED.add(value)
        return value
    return PRETTY[value]


def missing():
    """Values a generator asked for that this map does not cover (sorted, for a build warning)."""
    return sorted(_UNLABELLED)


def warn_missing(where):
    if _UNLABELLED:
        print(f"  ! {where}: no prose label for {', '.join(missing())} (add it to fig_labels.PRETTY)")
