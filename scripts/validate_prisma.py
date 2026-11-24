#!/usr/bin/env python3
"""PRISMA reconciliation gate: every identified record ends in exactly one terminal box.

Builds the record ledger (scripts/prisma_ledger.py), checks it, and writes what the flow diagram and
the supplementary lists read. It FAILS (exit 1) when:
  * a full-text ledger names a record id that no identification source returned;
  * a record has no terminal state, or a state outside the allowed set;
  * a study in the freeze is not exactly one INCLUDED record, or an INCLUDED record is not in it;
  * a record counted as another report of an included study points at a study that is not included;
  * any box of any source, column or the whole flow fails to close (the identities below).

Box identities, per source and per column:
  identified  = duplicates removed at search + duplicates found at rebuild + screened + awaiting screening
  screened    = excluded at first screen + advanced at first screen
  excluded at screening (final) = excluded at first screen - recovered by a later re-screen
  sought      = advanced + recovered
  sought      = not retrieved + awaiting full-text decision + assessed
  assessed    = excluded at full text + included studies + other reports of included studies

"Awaiting" is an explicit terminal box for records whose decision is being taken now (November 2026
screening of undecided records); fill data/extract_v2/qa/prisma_rebuild_2026-11/merged_outcomes.csv
and re-run. The gate reports how many remain.

Outputs: data/synth/prisma_terminal_states.csv   one row per identified record
         data/synth/prisma_counts.json           every box, per source and per column
         data/extract_v2/qa/prisma_rebuild_2026-11/awaiting_decision.csv
         data/extract_v2/qa/prisma_rebuild_2026-11/merged_outcomes.csv (header only, if absent)
         data/extract_v2/qa/prisma_rebuild_2026-11/duplicates_found_at_rebuild.csv
         data/extract_v2/qa/prisma_rebuild_2026-11/e2_openalex_duplicate_check.csv

Run: python3 scripts/validate_prisma.py [--json]
"""
import csv
import json
import os
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prisma_ledger as PL  # noqa: E402

P = PL.P
STATES = {"DUPLICATE", "AWAITING_SCREENING", "EXCLUDED_SCREENING", "NOT_RETRIEVED", "AWAITING_FT",
          "EXCLUDED_FT", "INCLUDED", "OTHER_REPORT"}
ROUTES = ("september_repair", "november_rescreen", "november_rules_pass", "other_check")


def box_counts(rows, rawdups):
    """Every box for one set of records (one source, one column, or the whole flow)."""
    c = Counter(r["state"] for r in rows)
    live = [r for r in rows if r["state"] != "DUPLICATE"]
    first_excl = [r for r in live if r["screen"] in ("EXCLUDED", "NOT_SCREENED") and r["state"] != "AWAITING_SCREENING"]
    advanced = [r for r in live if r["screen"] == "ADVANCED"]
    recovered = [r for r in first_excl if r["recovered_by"]]
    excl_stage = Counter(r["screen_stage"] for r in first_excl if not r["recovered_by"])
    b = dict(
        identified=len(rows) + len(rawdups),
        dup_at_search=len(rawdups),
        dup_rebuild=c["DUPLICATE"],
        awaiting_screening=c["AWAITING_SCREENING"],
        screened=len(first_excl) + len(advanced),
        first_pass_excluded=len(first_excl),
        recovered=len(recovered),
        recovered_by={k: sum(1 for r in recovered if r["recovered_by"] == k) for k in ROUTES},
        excluded_screening=c["EXCLUDED_SCREENING"],
        excluded_screening_by_stage=dict(sorted(excl_stage.items())),
        advanced=len(advanced),
        sought=len(advanced) + len(recovered),
        not_retrieved=c["NOT_RETRIEVED"],
        awaiting_ft=c["AWAITING_FT"],
        excluded_ft=c["EXCLUDED_FT"],
        included=c["INCLUDED"],
        other_reports=c["OTHER_REPORT"],
    )
    b["assessed"] = b["excluded_ft"] + b["included"] + b["other_reports"]
    b["excluded_ft_by_reason"] = {cat: sum(1 for r in rows if r["state"] == "EXCLUDED_FT" and r["reason_category"] == cat)
                                  for cat, _ in PL.REASON_CATEGORIES}
    return b


def check(name, b, errors):
    def eq(lhs, rhs, what):
        if lhs != rhs:
            errors.append(f"{name}: {what}: {lhs} != {rhs}")
    eq(b["identified"], b["dup_at_search"] + b["dup_rebuild"] + b["screened"] + b["awaiting_screening"],
       "identified = duplicates + screened + awaiting screening")
    eq(b["screened"], b["first_pass_excluded"] + b["advanced"], "screened = first-pass excluded + advanced")
    eq(b["excluded_screening"], b["first_pass_excluded"] - b["recovered"], "excluded at screening = first-pass excluded - recovered")
    eq(sum(b["recovered_by"].values()), b["recovered"], "recovered = sum of routes")
    eq(sum(b["excluded_screening_by_stage"].values()), b["excluded_screening"], "excluded at screening = sum of stages")
    eq(b["sought"], b["not_retrieved"] + b["awaiting_ft"] + b["assessed"], "sought = not retrieved + awaiting + assessed")
    eq(sum(b["excluded_ft_by_reason"].values()), b["excluded_ft"], "excluded at full text = sum of reasons")


def main():
    as_json = "--json" in sys.argv
    B = PL.build()
    L, frozen = B["L"], B["frozen"]
    errors, warnings = [], []

    rows = list(L.rec.values())
    for r in rows:
        r["column"] = PL.STREAM_COL[r["stream"]]
        r["reason_category"] = PL.reason_category(r) if r["state"] == "EXCLUDED_FT" else ""
        if r.get("state") not in STATES:
            errors.append(f"{r['stream']}:{r['record_id']} has no valid terminal state ({r.get('state')!r})")
    for d in L.rawdup:
        d["column"] = PL.STREAM_COL[d["stream"]]

    # --- identity of the included set ---------------------------------------------------------
    inc = Counter(r["record_id"] for r in rows if r["state"] == "INCLUDED")
    if set(inc) != frozen:
        errors.append(f"INCLUDED records != freeze: missing {sorted(frozen - set(inc))[:10]}, "
                      f"extra {sorted(set(inc) - frozen)[:10]}")
    if any(n > 1 for n in inc.values()):
        errors.append(f"study included twice: {[k for k, n in inc.items() if n > 1]}")
    for r in rows:
        if r["state"] == "OTHER_REPORT" and r["ft_extra"] not in frozen:
            errors.append(f"{r['record_id']} is another report of {r['ft_extra']!r}, which is not an included study")
    if B["unknown"]:
        errors.append(f"{len(B['unknown'])} id(s) in full-text ledgers match no identified record: {B['unknown'][:20]}")

    # --- boxes ---------------------------------------------------------------------------------
    streams = {}
    for key, col, label, date in PL.STREAMS:
        b = box_counts([r for r in rows if r["stream"] == key], [d for d in L.rawdup if d["stream"] == key])
        b.update(label=label, column=col, date=date)
        check(key, b, errors)
        streams[key] = b
    cols = {}
    for col in ("db", "other"):
        b = box_counts([r for r in rows if r["column"] == col], [d for d in L.rawdup if d["column"] == col])
        check(col, b, errors)
        cols[col] = b
    total = box_counts(rows, L.rawdup)
    check("all", total, errors)
    if total["included"] != len(frozen):
        errors.append(f"included box {total['included']} != {len(frozen)} studies in the freeze")
    for f in ("identified", "screened", "sought", "assessed", "included", "excluded_ft", "not_retrieved"):
        if cols["db"][f] + cols["other"][f] != total[f]:
            errors.append(f"columns do not add up on {f}")

    abstract_only = {PL.canon(r["study_id"]) for r in PL.rc("data/rob/risk_of_bias_v3_master.csv")
                     if r.get("source_read") == "abstract_only"} & {PL.canon(x) for x in frozen}
    n_est = len(B["frozen_rows"])
    ver = re.search(r"v([\d.]+)_frozen", PL.freeze_path()).group(1)
    awaiting = [r for r in rows if r["state"] in ("AWAITING_SCREENING", "AWAITING_FT")]
    if awaiting:
        warnings.append(f"{len(awaiting)} record(s) awaiting a decision ({Counter(r['state'] for r in awaiting)}); "
                        "fill prisma_rebuild_2026-11/merged_outcomes.csv when the screening returns")

    counts = dict(
        freeze=ver, studies=len(frozen), estimates=n_est,
        studies_assessed_on_abstract_only=len(abstract_only),
        reason_labels=dict(PL.REASON_CATEGORIES),
        route_labels={"september_repair": "September 2026 re-screen under corrected criteria (corpus repair)",
                      "november_rescreen": "November 2026 re-screen by a third model family",
                      "november_rules_pass": "November 2026 full-text re-read of earlier exclusions",
                      "other_check": "other checks (false-negative audits, human validation, dispositioning)"},
        streams=streams, columns=cols, total=total,
        states=dict(sorted(Counter(r["state"] for r in rows).items())),
        merged_outcomes_applied=len(B["merged"]),
        # Per-source facts read by make_counts_crosswalk.py and check_manuscript_stats.py: each source's
        # records after the de-duplication done when it was searched, and the September arm's own funnel.
        # They describe the searches, not the boxes of the flow (those are under "streams").
        identified=dict(scopus_corpus=streams["scopus"]["identified"] - streams["scopus"]["dup_at_search"],
                        openalex_netnew=streams["openalex"]["identified"] - streams["openalex"]["dup_at_search"],
                        pubmed_netnew=streams["pubmed"]["identified"] - streams["pubmed"]["dup_at_search"],
                        snowball_advancing=streams["snowball"]["advanced"] + sum(
                            1 for r in rows if r["stream"] == "snowball" and r["state"] == "DUPLICATE"
                            and r["screen"] == "ADVANCED"),
                        behavioural_arm_netnew=len(PL.rc(PL.ARM + "/screen_all.csv"))),
        behavioural_arm=json.load(open(P(PL.QA + "/behavioural_arm_funnel.json"), encoding="utf-8")),
        notes=dict(scopus_api_total=20409, scopus_downloaded=streams["scopus"]["identified"],
                   pubmed_hits=5179, pubmed_fetched=streams["pubmed"]["identified"]),
    )

    # --- write -----------------------------------------------------------------------------------
    with open(P("data/synth/prisma_counts.json"), "w", encoding="utf-8") as f:
        json.dump(counts, f, indent=2)
    cols_out = ["record_id", "stream", "column", "terminal_state", "screen", "screen_stage", "recovered_by",
                "reason_category", "reason", "reason_source", "dup_of", "dup_basis", "title", "doi", "year"]
    with open(P("data/synth/prisma_terminal_states.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols_out)
        w.writeheader()
        out = []
        for r in rows:
            reason = r["ft_reason"] if r["state"] in ("EXCLUDED_FT", "NOT_RETRIEVED", "OTHER_REPORT") else \
                (r.get("screen_reason", "") if r["state"] == "EXCLUDED_SCREENING" else "")
            src = r["ft_source"] if r["state"] in ("EXCLUDED_FT", "NOT_RETRIEVED", "OTHER_REPORT", "INCLUDED") else \
                (r.get("screen_source", "") if r["state"] == "EXCLUDED_SCREENING" else "")
            out.append(dict(record_id=r["record_id"], stream=r["stream"], column=r["column"],
                            terminal_state=r["state"], screen=r["screen"], screen_stage=r["screen_stage"],
                            recovered_by=r["recovered_by"], reason_category=r["reason_category"],
                            reason=" ".join(reason.split())[:600], reason_source=src,
                            dup_of=r.get("dup_of", "") or (r["ft_extra"] if r["state"] == "OTHER_REPORT" else ""),
                            dup_basis=r.get("dup_basis", ""), title=r["title"], doi=r["doi"], year=r["year"]))
        for d in L.rawdup:
            out.append(dict(record_id=d["record_id"], stream=d["stream"], column=d["column"],
                            terminal_state="DUPLICATE", screen="", screen_stage="", recovered_by="",
                            reason_category="", reason="", reason_source="", dup_of="",
                            dup_basis=d["dup_basis"], title=d["title"], doi=d["doi"], year=""))
        out.sort(key=lambda x: (PL.STREAM_ORDER[x["stream"]], x["terminal_state"], x["record_id"]))
        w.writerows(out)

    RB = P(PL.RB)
    with open(os.path.join(RB, "awaiting_decision.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["record_id", "stream", "awaiting", "screen_stage", "title", "doi", "outcome", "note"])
        for r in sorted(awaiting, key=lambda r: (r["state"], r["stream"], r["record_id"])):
            w.writerow([r["record_id"], r["stream"], "screening" if r["state"] == "AWAITING_SCREENING" else "full_text",
                        r["screen_stage"], r["title"], r["doi"], "", ""])
    mpath = os.path.join(RB, "merged_outcomes.csv")
    if not os.path.exists(mpath):
        with open(mpath, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(["record_id", "outcome", "note"])
    with open(os.path.join(RB, "duplicates_found_at_rebuild.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["stream", "record_id", "duplicate_of", "basis", "state_before_dedup", "title", "doi"])
        for r in sorted((r for r in rows if r["state"] == "DUPLICATE"), key=lambda r: (r["stream"], r["record_id"])):
            w.writerow([r["stream"], r["record_id"], r["dup_of"], r["dup_basis"], r.get("prior_state", ""), r["title"], r["doi"]])

    # E2: the 32 OpenAlex records once dropped as duplicates of one-word Scopus titles.
    by_id = defaultdict(list)
    for r in rows:
        by_id[r["record_id"]].append(r)
    with open(os.path.join(RB, "e2_openalex_duplicate_check.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["oaid", "title", "doi", "june_match", "verdict", "duplicate_of", "basis", "terminal_state",
                    "reason"])
        seen = set()
        for d in PL.rc(PL.QA + "/oa_dups_dropped.csv"):
            k = PL.canon(d["oaid"])
            if k in seen:
                continue
            seen.add(k)
            r = next((x for x in by_id[k] if x["stream"] == "openalex"), by_id[k][0])
            if r["state"] == "DUPLICATE":
                verdict, dup, basis = "duplicate record", r["dup_of"], r["dup_basis"]
            elif r["state"] == "OTHER_REPORT":
                verdict, dup, basis = "another report of an included study", r["ft_extra"], r["ft_reason"]
            else:
                verdict, dup, basis = "not a duplicate (no DOI or full-title match in any source)", "", ""
            w.writerow([k, r["title"], r["doi"], d["matched_existing"], verdict, dup, basis, r["state"],
                        " ".join((r["ft_reason"] or "").split())[:300]])

    ok = not errors
    if as_json:
        print(json.dumps({"ok": ok, "errors": errors, "warnings": warnings, **counts}, indent=2))
        sys.exit(0 if ok else 1)
    print("=" * 78)
    print(f"PRISMA RECORD LEDGER  (freeze v{ver}: {len(frozen)} studies / {n_est:,} estimates)")
    print("=" * 78)
    hdr = f"{'source':<14}{'ident':>7}{'dupS':>6}{'dupR':>5}{'awS':>5}{'scrn':>7}{'excl':>7}{'rec':>5}{'sght':>6}{'NR':>5}{'awF':>5}{'asd':>6}{'xFT':>5}{'inc':>5}{'rep':>4}"
    print(hdr)
    for name, b in list(streams.items()) + [("DB column", cols["db"]), ("OTHER column", cols["other"]), ("ALL", total)]:
        print(f"{name:<14}{b['identified']:>7}{b['dup_at_search']:>6}{b['dup_rebuild']:>5}{b['awaiting_screening']:>5}"
              f"{b['screened']:>7}{b['excluded_screening']:>7}{b['recovered']:>5}{b['sought']:>6}{b['not_retrieved']:>5}"
              f"{b['awaiting_ft']:>5}{b['assessed']:>6}{b['excluded_ft']:>5}{b['included']:>5}{b['other_reports']:>4}")
    print("-" * 78)
    print("recovered by:", total["recovered_by"])
    print("full-text exclusions by reason:")
    for cat, lab in PL.REASON_CATEGORIES:
        print(f"   {total['excluded_ft_by_reason'][cat]:>5}  {lab}")
    print(f"included studies {total['included']} (assessed on the abstract only: {len(abstract_only)}); "
          f"other reports of included studies {total['other_reports']}")
    print(f"merged outcomes applied: {len(B['merged'])}")
    for wmsg in warnings:
        print("WARNING:", wmsg)
    if errors:
        print(f"\nFAIL: {len(errors)} problem(s)")
        for e in errors:
            print("  -", e)
    else:
        print("\nPASS: every identified record has exactly one terminal state and every box closes.")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
