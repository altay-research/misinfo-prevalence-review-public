#!/usr/bin/env python3
"""
validate_frozen.py — automated integrity gate over the FROZEN estimate dataset.

Inspired by the Claude Science "reviewer agent that checks every citation and
calculation, flagging errors" — reimplemented here as a plain, auditable,
git-versioned script so the guarantee stays inside the repo and needs no human
to eyeball docs/Old/spotcheck.html (archived; round closed 2026-07).

It re-derives what CAN be re-derived and asserts the frozen invariants:
  FAIL  = a hard invariant is broken (the gate should stop the pipeline)
  WARN  = a soft/known-exception condition worth a human glance, not a stop

Reads the expected file / MD5 / counts straight from docs/FROZEN.md so this
script and the freeze spec can never silently drift apart.

Usage:
    python3 scripts/validate_frozen.py            # human report, exit 1 on FAIL
    python3 scripts/validate_frozen.py --json     # machine-readable report
Exit code 0 = all invariants hold, 1 = at least one FAIL.
"""
import csv, json, re, os, sys, hashlib
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = lambda *a: os.path.join(ROOT, *a)

# Tolerance for X-of-Y vs value_pct reconciliation (percentage points).
PCT_TOL = 0.6
# Constructs known/allowed as of freeze v1.1. Unknown -> WARN (typo guard).
KNOWN_CONSTRUCTS = {
    "CONTENT", "RECALL", "SHARING", "QUALITY",
    "EXPOSURE", "CONCENTRATION", "REACH", "OTHER",
}
# Provenance jsonl files used to resolve study ids back to a real record.
CORPUS_SOURCES = [
    "data/corpus_strict_v2_2026-06-20.jsonl",
    "data/snowball/advancing.jsonl",
    "data/openalex_netnew.jsonl",
    "data/pubmed_netnew.jsonl",
]

fails, warns = [], []
def FAIL(msg): fails.append(msg)
def WARN(msg): warns.append(msg)


def parse_frozen_spec():
    """Pull expected file, md5, rows, studies out of docs/FROZEN.md."""
    txt = open(P("docs", "FROZEN.md")).read()
    spec = {}
    m = re.search(r"File:\s*(\S+)", txt);            spec["file"] = m.group(1) if m else None
    m = re.search(r"MD5:\s*([0-9a-f]{32})", txt);    spec["md5"] = m.group(1) if m else None
    m = re.search(r"Rows:\s*([\d,]+)\s*estimates?\s*/\s*([\d,]+)\s*studies", txt)
    if m:
        spec["rows"] = int(m.group(1).replace(",", ""))
        spec["studies"] = int(m.group(2).replace(",", ""))
    return spec


def md5_of(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def to_num(s):
    """'2,474,046' -> 2474046.0 ; '' / non-numeric -> None."""
    if s is None:
        return None
    s = s.strip().replace(",", "")
    if re.fullmatch(r"-?\d+(?:\.\d+)?", s):
        return float(s)
    return None


def load_resolvable_ids():
    """All ids we can trace to a provenance record, with prefix normalization."""
    keys = set()
    def add(k):
        if not k:
            return
        k = str(k)
        keys.add(k)
        # normalize common prefixes so OA-W123 / W123 / https://openalex.org/W123 all match
        for pre in ("OA-", "PMID-", "NEW-", "https://openalex.org/", "https://doi.org/"):
            if k.startswith(pre):
                keys.add(k[len(pre):])
        keys.add(re.sub(r"^\D+", "", k))  # bare trailing number/id
    for src in CORPUS_SOURCES:
        p = P(src)
        if not os.path.exists(p):
            continue
        for line in open(p):
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except Exception:
                continue
            for f in ("eid", "oaid", "oa_id", "id", "pmid", "doi"):
                add(d.get(f))
    return keys


def id_resolves(rid, keys):
    if rid in keys:
        return True
    for pre in ("OA-", "PMID-", "NEW-"):
        if rid.startswith(pre) and rid[len(pre):] in keys:
            return True
    if re.sub(r"^\D+", "", rid) in keys:
        return True
    return False


def main():
    as_json = "--json" in sys.argv
    spec = parse_frozen_spec()
    data_path = P(spec.get("file") or "data/extract_v2/estimates_reextracted.csv")

    # ---- 1. file exists + MD5 matches the freeze spec (catches ANY silent edit)
    if not os.path.exists(data_path):
        FAIL(f"frozen file missing: {data_path}")
        return report(spec, {}, as_json)
    actual_md5 = md5_of(data_path)
    if spec.get("md5") and actual_md5 != spec["md5"]:
        FAIL(f"MD5 mismatch: file={actual_md5} spec={spec['md5']} "
             f"(the frozen CSV was modified without re-freezing)")

    rows = list(csv.DictReader(open(data_path)))
    ids = [r["id"] for r in rows]
    n_rows, n_studies = len(rows), len(set(ids))

    # ---- 2. row / study counts match the freeze spec
    if spec.get("rows") and n_rows != spec["rows"]:
        FAIL(f"row count drift: file={n_rows} spec={spec['rows']}")
    if spec.get("studies") and n_studies != spec["studies"]:
        FAIL(f"study count drift: file={n_studies} spec={spec['studies']}")

    # ---- 3. required fields present; each row has an id + at least one value
    for i, r in enumerate(rows, start=2):  # line 2 = first data row
        if not (r.get("id") or "").strip():
            FAIL(f"row {i}: empty id")
        if not (r.get("value_pct") or "").strip() and not (r.get("value_raw") or "").strip():
            FAIL(f"row {i} (id={r.get('id')}): both value_pct and value_raw empty")

    # ---- 4. value_pct in [0,100] when a plain number; ranges (e.g. 73-78) -> WARN
    range_pcts = []
    for i, r in enumerate(rows, start=2):
        raw = (r.get("value_pct") or "").strip()
        if not raw:
            continue
        v = to_num(raw)
        if v is None:
            range_pcts.append((i, r["id"], raw))
        elif not (0 <= v <= 100):
            FAIL(f"row {i} (id={r['id']}): value_pct out of [0,100]: {v}")
    for i, rid, raw in range_pcts:
        WARN(f"row {i} (id={rid}): value_pct non-numeric (range?): {raw!r}")

    # ---- 5. X-of-Y reconciliation: numerator/denominator*100 must match value_pct
    xy = re.compile(r"^([\d,\.]+)\s+of\s+([\d,\.]+)$")
    checked = 0
    for i, r in enumerate(rows, start=2):
        m = xy.match((r.get("value_raw") or "").strip())
        if not m:
            continue
        num, den = to_num(m.group(1)), to_num(m.group(2))
        pct = to_num(r.get("value_pct"))
        if num is None or den is None or not den:
            continue
        derived = num / den * 100
        if num > den:
            FAIL(f"row {i} (id={r['id']}): numerator>denominator in value_raw "
                 f"{r['value_raw']!r}")
        checked += 1
        if pct is not None and abs(derived - pct) > PCT_TOL:
            FAIL(f"row {i} (id={r['id']}): value_raw implies {derived:.2f}% but "
                 f"value_pct={pct} (Δ={abs(derived-pct):.2f} > {PCT_TOL})")

    # ---- 6. no exact-duplicate rows (identical across EVERY column). Rows that
    # share id/country/measure/value but differ in definition/source_quote are
    # legitimately distinct estimates (e.g. different narratives), so the key
    # must be the full row, not a subset of fields.
    seen = defaultdict(list)
    for i, r in enumerate(rows, start=2):
        seen[tuple(sorted(r.items()))].append(i)
    for _, lines in seen.items():
        if len(lines) > 1:
            rid = rows[lines[0] - 2]["id"]
            FAIL(f"identical duplicate rows at lines {lines}: id={rid}")

    # ---- 7. construct vocabulary guard (typos)
    for c, n in Counter(r.get("construct") for r in rows).items():
        if c not in KNOWN_CONSTRUCTS:
            WARN(f"unknown construct value {c!r} on {n} row(s)")

    # ---- 8. id -> provenance resolution (WARN: provenance is the real guarantee)
    keys = load_resolvable_ids()
    unresolved = sorted({rid for rid in set(ids) if not id_resolves(rid, keys)})
    if unresolved:
        WARN(f"{len(unresolved)} study id(s) not resolvable to a provenance record "
             f"(likely snowball/grey additions): {unresolved[:10]}"
             + (" ..." if len(unresolved) > 10 else ""))

    stats = {
        "file": os.path.relpath(data_path, ROOT),
        "md5": actual_md5,
        "rows": n_rows,
        "studies": n_studies,
        "xy_reconciled": checked,
        "constructs": dict(Counter(r.get("construct") for r in rows)),
        "unresolved_ids": len(unresolved),
    }
    return report(spec, stats, as_json)


def report(spec, stats, as_json):
    ok = not fails
    if as_json:
        print(json.dumps({"ok": ok, "fails": fails, "warns": warns,
                          "stats": stats, "spec": spec}, indent=2))
    else:
        print("=" * 66)
        print("FROZEN DATASET VALIDATION")
        print("=" * 66)
        if stats:
            print(f"file      : {stats.get('file')}")
            print(f"md5       : {stats.get('md5')}")
            print(f"rows      : {stats.get('rows')}   studies: {stats.get('studies')}")
            print(f"X-of-Y reconciled : {stats.get('xy_reconciled')} rows")
            print(f"id unresolved     : {stats.get('unresolved_ids')}")
        print("-" * 66)
        if fails:
            print(f"\n❌ {len(fails)} FAIL(s):")
            for m in fails:
                print(f"   - {m}")
        if warns:
            print(f"\n⚠️  {len(warns)} WARN(s):")
            for m in warns:
                print(f"   - {m}")
        print()
        print("✅ PASS — all frozen invariants hold." if ok
              else f"❌ FAIL — {len(fails)} invariant(s) broken.")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
