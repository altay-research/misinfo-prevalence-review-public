#!/usr/bin/env python3
"""Regenerate the freeze table in docs/dataset_provenance.md FROM docs/FROZEN.md.

The ledger is meant to be the auditable chain of every dataset version, but it was hand-maintained
alongside FROZEN.md and fell 21 freezes behind — the two documents that both claim to record the
chain had silently diverged. FROZEN.md is the source of truth (every script resolves the live
dataset from its `File:` line), so the ledger's table is now derived from it and marked generated.

The ledger's hand-written narrative for the older versions is preserved untouched above the
generated block; only the block between the markers is rewritten.

Run after any re-freeze: python3 scripts/sync_provenance_ledger.py
"""
import os, re, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FZ = open(os.path.join(ROOT, "docs/FROZEN.md")).read()
LEDGER = os.path.join(ROOT, "docs/dataset_provenance.md")
BEGIN = "<!-- BEGIN generated freeze table — scripts/sync_provenance_ledger.py -->"
END = "<!-- END generated freeze table -->"

frs = re.findall(r"# FROZEN DATASET (v[\d.]+) \(([\d-]+)\).*?- File: (\S+)\n- Rows: ([^\n]+)\n- MD5: (\w+)"
                 r".*?- Built by: ([^\n]+)", FZ, re.S)
tags = set(subprocess.run(["git", "tag"], cwd=ROOT, capture_output=True, text=True).stdout.split())

lines = [BEGIN,
         "",
         "## Freeze table (generated from `docs/FROZEN.md` — do not hand-edit)",
         "",
         f"{len(frs)} freezes recorded. The **top row is the live dataset**; every script resolves it",
         "from the `File:` line of `FROZEN.md`, never from this table.",
         "",
         "| version | date | rows / studies | MD5 | git tag | built by |",
         "|---|---|---|---|---|---|"]
for v, d, f, rows, md5, built in frs:
    tag = f"dataset-frozen-{v}"
    lines.append(f"| **{v}** | {d} | {rows.strip()} | `{md5[:12]}…` | "
                 f"{'`'+tag+'`' if tag in tags else '—'} | {built.strip()} |")
lines += ["", END]

s = open(LEDGER).read()
block = "\n".join(lines)
if BEGIN in s and END in s:
    s = re.sub(re.escape(BEGIN) + r".*?" + re.escape(END), block, s, flags=re.S)
else:
    s = s.rstrip() + "\n\n" + block + "\n"
open(LEDGER, "w").write(s)
missing = [v for v, *_ in frs if f"dataset-frozen-{v}" not in tags]
print(f"ledger synced: {len(frs)} freezes")
if missing:
    print(f"  WARNING — freezes with no git tag: {missing}")
