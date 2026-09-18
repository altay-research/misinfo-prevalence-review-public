#!/usr/bin/env python3
"""phaseB_platform_construct.py — platforms studied, by construct (Appendix B5).

Reads the freeze named in the TOP block of docs/FROZEN.md and writes
data/synth/phaseB/platform_by_construct.csv plus a markdown table ready to paste into the SI.

Counting rule: STUDIES, not estimates. A study counts once in every platform it covers for that
construct, so the rows sum to more than the k at the foot of the column. Studies whose platform
field names several platforms ("Facebook/Twitter/Instagram", "Multiple social media (Facebook,
Reddit, Twitter, Pinterest)") are counted in EVERY platform named, which is the point of the table;
"No platform named" holds the studies that say only "social media" or only "survey".
The alternative, one modal platform per study, is tie-dependent (26 of the 323 study-construct
cells have no unique mode) and was rejected for that reason. A study contributing two constructs is
counted in both columns.

Run: python3 scripts/phaseB_platform_construct.py
"""

import collections
import csv
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data/synth/phaseB")
CONSTRUCTS = ["EXPOSURE", "REACH", "SHARING", "CONCENTRATION", "CONTENT", "RECALL"]

# Display row -> the substrings that put a study in it. Matched against the RAW platform string, so
# a study naming four platforms lands in four rows; "YouTube Shorts" and "Instagram Reels" fold into
# their parent platform. Order is display order only; every row is tested independently.
GROUPS = [
    ("Twitter/X", ["twitter", "x/twitter", "x (twitter)"]),
    ("YouTube", ["youtube"]),
    ("TikTok", ["tiktok", "douyin"]),
    ("Facebook", ["facebook"]),
    ("Instagram", ["instagram"]),
    ("Reddit", ["reddit"]),
    ("WhatsApp", ["whatsapp"]),   # WeChat is not WhatsApp; no study names it alone
    ("Telegram", ["telegram"]),
    ("Weibo", ["weibo"]),
    ("Google Search", ["google"]),
    ("News outlets", ["news media", "news website", "digital news", "newspaper", "online outlets",
                      "broadcast", "cnn", "fox news", "msnbc"]),
    ("Forums", ["forum", "4chan", "ptt"]),
    # NB "desktop"/"laptop" are DEVICE words, not designs: they used to sit here and pulled
    # "TikTok (desktop version)" into the browsing bucket. A browsing panel is named by its method.
    ("Web browsing", ["browsing", "web-tracking", "web tracking", "web_tracking", "comscore",
                      "web traffic", "cross-device", "off-platform web", "desktop panel",
                      "desktop and mobile", "desktop tracking"]),
    ("Websites", []),   # assigned only through OVERRIDES: a corpus of sites is not a browsing panel
    ("No platform named", ["survey", "recall"]),   # also the fallback for generic "social media"
]
GENERIC_MULTI = ("social media", "social network", "multi", "mixed", "cross-platform", "any/mixed",
                 "multiple")
# bare broadcaster names, matched exactly rather than as substrings ("abc" hits "abcnews.example")
NETWORKS = {"tv", "abc", "cbs", "nbc", "cnn", "fox", "msnbc", "pbs"}

# Strings whose plain reading the keyword rules get wrong, resolved against the study's own measure.
# Kept explicit rather than tuned into the keyword lists, where each would have caught other rows.
OVERRIDES = {
    "": {"No platform named"},                                   # platform field left blank
    "online": {"No platform named"},                             # survey recall, no platform asked
    "overall (incl. tv)": {"No platform named"},                 # cross-media diet, not a platform
    "overall (tv+desktop+mobile)": {"No platform named"},        # idem; "desktop" made it a browsing panel
    "website": {"Websites"},                                     # corpora of sites, not browsing behaviour
    "websites": {"Websites"},
    "official health websites": {"Websites"},
    "web (general search)": {"Websites"},
    "web pages (arabic-language, search-engine results)": {"Websites"},
    "mainstream media articles (web)": {"News outlets"},
    "fake news websites": {"News outlets"},
    "search": {"Google Search"},                                 # share of search queries
}


def labels_for(raw, norm, construct=""):
    """Every display row this one estimate belongs to. Shared with check_manuscript_stats.py."""
    lc = (raw or "").lower().strip()
    if lc in OVERRIDES:
        return set(OVERRIDES[lc])
    hits = {lab for lab, keys in GROUPS if any(k in lc for k in keys)}
    if lc in NETWORKS:
        hits.add("News outlets")
    if "No platform named" in hits and len(hits) > 1:
        hits.discard("No platform named")   # "survey (mainly Facebook/WhatsApp)" is a platform study
    if not hits and any(g in lc for g in GENERIC_MULTI):
        hits = {"No platform named"}
    if not hits and norm == "web_cross_platform":
        # "web_cross_platform" covers two different things and used to collapse them: a behavioural
        # BROWSING PANEL (a person's traced web use) and a CORPUS OF WEBSITES analysed as content.
        # The repair added several website content analyses, which surfaced the conflation (the
        # manuscript checker asserts browsing panels carry no content studies, and it fired).
        # Route by how the data were collected, not by the platform string.
        # The dividing line is what was measured, not how the sample was drawn: an audience's own
        # web use is a browsing panel; a set of sites judged for their content is a website corpus.
        hits = {"Websites"} if construct in ("CONTENT", "QUALITY") else {"Web browsing"}
    return hits or {"Other"}


def freeze_path():
    block = open(os.path.join(ROOT, "docs/FROZEN.md"), encoding="utf-8").read()
    return os.path.join(ROOT, re.search(r"^- File: (.+)$", block, re.M).group(1).strip())


def main():
    rows = list(csv.DictReader(open(freeze_path(), encoding="utf-8")))
    pool = [r for r in rows
            if r["value_kind"] == "proportion" and not (r["demographic_group"] or "").strip()]

    counts = collections.defaultdict(collections.Counter)
    totals = collections.Counter()
    for c in CONSTRUCTS:
        per_study = collections.defaultdict(list)
        for r in pool:
            if r["construct"] == c:
                per_study[r["id"]].append((r["platform"], r["platform_norm"]))
        totals[c] = len(per_study)
        for est in per_study.values():
            seen = set()
            for raw, norm in est:
                seen |= labels_for(raw, norm, c)   # the study's construct routes web_cross_platform
            for lab in seen:
                counts[lab][c] += 1

    labels = [lab for lab, _ in GROUPS] + ["Other"]
    with open(os.path.join(OUT, "platform_by_construct.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["platform"] + CONSTRUCTS)
        for lab in labels:
            w.writerow([lab] + [counts[lab][c] for c in CONSTRUCTS])
        w.writerow(["TOTAL studies"] + [totals[c] for c in CONSTRUCTS])

    head = ["Platform", "Exposure", "Reach", "Sharing", "Concentration", "Content", "Recall"]
    md = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    for lab in labels:
        md.append("| " + " | ".join([lab] + [str(counts[lab][c] or "–") for c in CONSTRUCTS]) + " |")
    md.append("| **Studies (k)** | " + " | ".join(f"**{totals[c]}**" for c in CONSTRUCTS) + " |")
    open(os.path.join(OUT, "platform_by_construct.md"), "w", encoding="utf-8").write("\n".join(md) + "\n")

    print("\n".join(md))
    print(f"\nstudy-construct pairs: {sum(totals.values())} across {len({r['id'] for r in pool})} studies")


if __name__ == "__main__":
    main()
