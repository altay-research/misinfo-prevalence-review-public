#!/usr/bin/env python3
"""
PRISMA reconciliation gate.

Every record that ever ADVANCED (was INCLUDE/MAYBE at any screening stage, or was
staged as a candidate, or is a seed/supplementary) must map to EXACTLY ONE terminal
state. Records that advanced but have no terminal state are ORPHANS — the thing a
PRISMA auditor looks for ("screened-in records that silently vanished"). This script
makes that machine-checkable and in-git.

It normalizes the 6 ID schemes used across the project (2-s2.0-…, W…, OA-W…,
PMID-…/bare pmid, SEED-/SUPP-/NEW-) to canonical keys, unions the split drop
ledgers, and reports the funnel + orphans.

Read-only. Usage: python3 scripts/validate_prisma.py [--json]
Exit 1 if any orphan is found.
"""
import csv, json, os, re, sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = lambda *a: os.path.join(ROOT, *a)


def canon(x):
    """Normalize any ID scheme to one canonical key."""
    if x is None:
        return ""
    x = str(x).strip()
    x = x.replace("https://openalex.org/", "")
    if x.startswith("OA-"):
        x = x[3:]
    if x.startswith("PMID-"):
        return x
    if re.fullmatch(r"\d+", x):          # bare PubMed id
        return "PMID-" + x
    return x                              # W…, 2-s2.0-…, SEED-/SUPP-/NEW-


def read_csv(path):
    return list(csv.DictReader(open(P(path)))) if os.path.exists(P(path)) else []


def read_jsonl(path):
    out = []
    if os.path.exists(P(path)):
        for l in open(P(path)):
            l = l.strip()
            if l:
                try: out.append(json.loads(l))
                except: pass
    return out


def ids_from(rows, field):
    return {canon(r.get(field)) for r in rows if r.get(field)}


def main():
    as_json = "--json" in sys.argv

    # ---------- terminal-state sets (canonical keys) ----------
    # PRISMA_FROZEN env var lets a pre-freeze dry-run point the frozen set at a release
    # candidate (e.g. estimates_v1.2_frozen.csv) without touching the file this reads by default.
    # Read the CURRENT freeze from docs/FROZEN.md, exactly as every phaseB script does.
    # This previously defaulted to a hardcoded estimates_v1.4.0_frozen.csv, so the gate silently
    # validated a stale snapshot from v1.4.1 onward -- it reported PASS against 329 studies while
    # the live freeze had moved to 317. A gate that green-lights the wrong file is worse than no
    # gate, so the default now follows the pointer and the env var remains only as an override.
    import re as _re
    _spec = open(os.path.join(ROOT, "docs/FROZEN.md"), encoding="utf-8").read()
    _m = _re.search(r"File:\s*(\S+)", _spec)
    # No fallback: an unreadable pointer raises. The comment above records what the old fallback
    # cost, and a hardcoded default is the same bug wearing a different version number.
    if not (_m or os.environ.get("PRISMA_FROZEN")):
        raise SystemExit("validate_prisma: cannot read the 'File:' line from docs/FROZEN.md")
    frozen_path = os.environ.get("PRISMA_FROZEN") or _m.group(1).strip("`")
    frozen = ids_from(read_csv(frozen_path), "id")

    abs_only_raw = json.load(open(P("data/extract_v2/qa/abstract_only_list.json")))
    abstract_only = {canon(d.get("id")) for d in abs_only_raw}

    dropped = set()
    for f, fld in [("data/extract_v2/qa/dropped_studies.csv", "id"),
                   ("data/extract_v2/qa/stepb_drops_queue.csv", "id"),
                   ("data/extract_v2/qa/decided_drops.csv", "id"),
                   ("data/extract_v2/qa/review_pooled_drops.csv", "id")]:
        dropped |= ids_from(read_csv(f), fld)
    dropped |= {canon(d.get("id")) for d in
                json.load(open(P("data/extract_v2/qa/drop_audit.json"))) if d.get("id")}

    dedup = ids_from(read_csv("data/extract_v2/qa/oa_dups_dropped.csv"), "oaid")

    # v1.2-specific terminal ledger (studies that were in frozen v1.1 but dropped/merged in v1.2,
    # each with a documented reason — so they don't fall to the DROPPED_V2_UNLEDGERED catch-all).
    for r in read_csv("data/extract_v2/qa/v1.2_drops_ledger.csv"):
        k = canon(r.get("id"))
        if not k:
            continue
        if r.get("terminal") == "DEDUP_COLLAPSED":
            dedup.add(k)
        else:
            dropped.add(k)

    not_retrieved = (ids_from(read_csv("data/extract_v2/qa/included_not_retrieved.csv"), "id")
                     | ids_from(read_csv("data/extract_v2/qa/openalex_not_retrieved.csv"), "id"))

    # PRISMA dispositions ledger (the 126 screened-in-but-unledgered records, each given a
    # terminal disposition in data/extract_v2/qa/prisma_dispositions.csv — punch-list F).
    dispositioned = {canon(r.get("id")): r.get("disposition", "DISPOSITIONED")
                     for r in read_csv("data/extract_v2/qa/prisma_dispositions.csv") if r.get("id")}

    # The September behavioural arm, folded into the funnel by ruling P1 (2026-09-14). Its 562
    # advanced records each carry a terminal state from the arm's own stage files, built by
    # scripts/make_behavioural_arm_dispositions.py. Before this, the arm's 20 studies entered the
    # assessed pool through `advanced |= frozen` with no screening path a reader could follow.
    arm_disp = {canon(r["id"]): r["disposition"]
                for r in read_csv("data/extract_v2/qa/behavioural_arm_dispositions.csv") if r.get("id")}
    arm_funnel = json.load(open(P("data/extract_v2/qa/behavioural_arm_funnel.json")))

    # ---------- screening dispositions ----------
    abs_rows = read_csv("data/screen_abstract_2026-06-21.csv")
    st5_rows = read_csv("data/screen_stage5_2026-06-21.csv")
    excluded_later = ({canon(r["eid"]) for r in abs_rows if r.get("label") == "EXCLUDE"}
                      | {canon(r["eid"]) for r in st5_rows if r.get("label") == "EXCLUDE"})

    # verify/triage per-item verdicts (eid,verdict,reason). REJECT/EXCLUDE are terminal.
    import glob
    screen_rejected = set()
    for f in (glob.glob(P("data/verify/v_*.csv")) + glob.glob(P("data/verify/adj_*.csv"))
              + glob.glob(P("data/extract_v2/qa/triage_*.csv"))
              + glob.glob(P("data/extract_v2/qa/fn*.csv"))
              + glob.glob(P("data/extract_v2/qa/excl*.csv"))):
        for r in csv.DictReader(open(f)):
            if (r.get("verdict") or "").strip() in ("REJECT", "EXCLUDE"):
                screen_rejected.add(canon(r.get("eid") or r.get("id")))

    # v1 extraction master (690 rows / 408 studies) — anything here but not in frozen v2
    # was dropped at the v1->v2 re-freeze; if it has no ledger entry that drop is UNLEDGERED.
    master_v1 = ids_from(read_csv("data/extract_v2/estimates_master_final.csv"), "id") \
                | ids_from(read_csv("data/extract_v2/estimates_master_final.csv"), "eid")

    # ---------- the set that must reach a terminal state ----------
    # ONLY records that were actually INCLUDED (passed screening) or staged for
    # extraction. A MAYBE that never became an INCLUDE was *not selected* at the
    # next gate — that is itself a terminal screening outcome, NOT a vanished
    # include, so MAYBEs are excluded here and reported separately below.
    included_at_screen = (
        {canon(r["eid"]) for r in abs_rows if r.get("label") == "INCLUDE"}
        | {canon(r["eid"]) for r in st5_rows if r.get("label") == "INCLUDE"}
        | {canon(d.get("oaid")) for d in read_jsonl("data/openalex_adjudicate.jsonl")
           if d.get("label") == "INCLUDE"}
        | {canon(d.get("pmid")) for d in read_jsonl("data/pubmed_adjudicate.jsonl")
           if d.get("label") == "INCLUDE"})
    advanced = set()
    advanced |= included_at_screen
    advanced |= ids_from(read_csv("data/extract/include635_tagged.csv"), "eid")
    advanced |= ids_from(read_csv("data/extract_v2/qa/openalex_candidates_STAGED.csv"), "id")
    advanced |= set(arm_disp)     # the behavioural arm's 562 screened-in records
    advanced |= frozen            # seeds/supp/new enter the funnel directly at extraction
    advanced.discard("")

    # MAYBEs that never became an INCLUDE and aren't in any terminal set =
    # "not selected at screening" (informational; a terminal outcome, not orphans)
    all_maybe = ({canon(r["eid"]) for r in abs_rows if r.get("label") == "MAYBE"}
                 | {canon(r["eid"]) for r in st5_rows if r.get("label") == "MAYBE"}
                 | {canon(d.get("oaid")) for d in read_jsonl("data/openalex_adjudicate.jsonl")
                    if d.get("label") == "MAYBE"}
                 | {canon(d.get("pmid")) for d in read_jsonl("data/pubmed_adjudicate.jsonl")
                    if d.get("label") == "MAYBE"})
    maybe_not_selected = all_maybe - advanced
    maybe_not_selected.discard("")

    # ---------- assign exactly one terminal state (precedence) ----------
    state = {}
    for k in advanced:
        if k in frozen:            state[k] = "INCLUDED_FROZEN"
        elif k in dropped:         state[k] = "DROPPED"
        elif k in dedup:           state[k] = "DEDUP_COLLAPSED"
        elif k in not_retrieved:   state[k] = "INCLUDED_NOT_RETRIEVED"
        elif k in excluded_later:  state[k] = "EXCLUDED_AT_SCREENING"
        elif k in screen_rejected: state[k] = "VERIFY_REJECTED"
        elif k in dispositioned:   state[k] = "DISP_" + dispositioned[k]
        elif k in arm_disp:        state[k] = arm_disp[k]
        elif k in master_v1:       state[k] = "DROPPED_V2_UNLEDGERED"
        else:                      state[k] = "ORPHAN"

    hist = Counter(state.values())
    orphans = sorted(k for k, v in state.items() if v == "ORPHAN")

    # attach titles to orphans where findable (STAGED file has titles)
    staged = read_csv("data/extract_v2/qa/openalex_candidates_STAGED.csv")
    title_by = {}
    for r in staged:
        title_by.setdefault(canon(r["id"]), r.get("title", ""))
    for d in abs_only_raw:
        title_by.setdefault(canon(d.get("id")), d.get("title", ""))

    # ---------- funnel top-line (for the PRISMA diagram) ----------
    title_rows = read_csv("data/screen_title_2026-06-20.csv")
    tl = Counter(r.get("label") for r in title_rows)
    ab = Counter(r.get("label") for r in abs_rows)
    st = Counter(r.get("label") for r in st5_rows)

    stats = {
        "identified": {
            "scopus_corpus": len(read_jsonl("data/corpus_strict_v2_2026-06-20.jsonl")),
            "openalex_netnew": len(read_jsonl("data/openalex_netnew.jsonl")),
            "pubmed_netnew": len(read_jsonl("data/pubmed_netnew.jsonl")),
            "snowball_advancing": len(read_jsonl("data/snowball/advancing.jsonl")),
            "behavioural_arm_netnew": arm_funnel["records_netnew"],
        },
        "behavioural_arm": arm_funnel,
        # Sorted, not insertion-ordered: these Counters are built by iterating SETS of record ids,
        # so their key order changes with Python's per-process hash seed and the file churned on
        # every run with identical values. A diff that is noise cannot be read as a signal.
        "title_screen": dict(sorted(tl.items())), "abstract_screen": dict(sorted(ab.items())),
        "stage5_screen": dict(sorted(st.items())),
        "included_or_staged_to_reconcile": len(advanced),
        "maybe_not_selected": len(maybe_not_selected),
        "terminal_states": dict(sorted(hist.items(), key=lambda kv: (-kv[1], kv[0]))),
        "frozen_studies": len(frozen),
        "abstract_only": len(abstract_only & frozen),
        "dropped_union": len(dropped),
        "not_retrieved": len(not_retrieved),
        "dedup_collapsed": len(dedup),
        "orphans": [{"id": o, "title": title_by.get(o, "")} for o in orphans],
    }

    # Persist the reconciled counts so the PRISMA diagram is GENERATED from them rather than
    # hardcoded. The diagram previously carried its own literal counts and drifted to a v1.1-era
    # funnel (408 studies / 695 estimates) while the manuscript said 317/679 -- and its arithmetic
    # did not reconcile. One source of truth removes that whole class of error.
    with open(P("data/synth/prisma_counts.json"), "w") as f:
        json.dump(stats, f, indent=2)

    # Persist the per-record states. make_si_lists.py used to re-derive this whole partition from
    # the same ledgers and assert its answer matched; two copies of a fifteen-source precedence
    # chain is one copy too many, and folding in the September arm broke the copy. One table, one
    # derivation, everything downstream reads it.
    with open(P("data/synth/prisma_terminal_states.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "terminal_state"])
        for k in sorted(state):
            w.writerow([k, state[k]])

    # persist orphan + unledgered lists as dispositioning worklists
    if orphans:
        with open(P("data/extract_v2/qa/prisma_orphans.csv"), "w", newline="") as f:
            w = csv.writer(f); w.writerow(["id", "title", "state"])
            for o in orphans:
                w.writerow([o, title_by.get(o, ""), "ORPHAN"])
            for k, v in state.items():
                if v == "DROPPED_V2_UNLEDGERED":
                    w.writerow([k, title_by.get(k, ""), v])

    ok = not orphans
    if as_json:
        print(json.dumps({"ok": ok, **stats}, indent=2))
        sys.exit(0 if ok else 1)

    print("=" * 70)
    print("PRISMA RECONCILIATION")
    print("=" * 70)
    print("Identified (dedup'd streams):")
    for k, v in stats["identified"].items():
        print(f"    {k:22} {v:>7}")
    print(f"Title screen   : {dict(tl)}")
    print(f"Abstract screen: {dict(ab)}")
    print(f"Stage-5 screen : {dict(st)}")
    print("-" * 70)
    print(f"Included/staged records to reconcile: {len(advanced)}  "
          f"(MAYBE-not-selected, terminal: {len(maybe_not_selected)})")
    for s, n in hist.most_common():
        print(f"    {s:26} {n:>6}")
    print("-" * 70)
    print(f"frozen studies {len(frozen)} | abstract-only {stats['abstract_only']} | "
          f"dropped {len(dropped)} | not-retrieved {len(not_retrieved)} | "
          f"dedup {len(dedup)}")
    print("-" * 70)
    if orphans:
        print(f"\n❌ {len(orphans)} ORPHAN(s) — advanced but no terminal state "
              f"(record a per-item disposition):")
        for o in orphans:
            print(f"   - {o}  {title_by.get(o,'')[:60]}")
        print("\n❌ FAIL — reconcile the orphan(s) above.")
    else:
        print("\n✅ PASS — every advanced record maps to a terminal state.")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
