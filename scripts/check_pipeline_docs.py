#!/usr/bin/env python3
"""Assert that the pipeline's run order is the same in both places that state it.

`scripts/run_phaseB.sh` executes the pipeline; `docs/PIPELINE.md` documents it, and its own header
says the two must agree. Nothing enforced that, and they had drifted: `make_si_characteristics.py`
ran in the shell script and appeared nowhere in the document, so a reader following the document
regenerated everything except Supplementary Data 1 (found 2026-09-16).

Compares the set of scripts each side names and reports what only one of them has. A script may be
deliberately documented outside the bash blocks (the two R stages, the optional ones): list it in
DOC_ONLY_OK with the reason.

Run: python3 scripts/check_pipeline_docs.py
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Scripts the document mentions in prose or a side note rather than in a run-order block, on purpose.
DOC_ONLY_OK = {
    "phaseB_metareg.R": "an R stage, run by hand between the two halves",
    "phaseB_metareg_robustness.R": "an R stage, run by hand; hours, not minutes",
}


def shell_steps():
    txt = open(os.path.join(ROOT, "scripts/run_phaseB.sh"), encoding="utf-8").read()
    return {m.group(1) for m in re.finditer(r"^\s*step\s+(\S+\.py)", txt, re.M)}


def doc_steps():
    txt = open(os.path.join(ROOT, "docs/PIPELINE.md"), encoding="utf-8").read()
    steps = set()
    for block in re.findall(r"```bash\n(.*?)```", txt, re.S):
        steps |= {m.group(1) for m in
                  re.finditer(r"^\s*python3\s+scripts/(\S+\.py)", block, re.M)}
    return steps


def main():
    sh, doc = shell_steps(), doc_steps()
    only_sh = sorted(sh - doc)
    only_doc = sorted(d for d in doc - sh if d not in DOC_ONLY_OK)
    print(f"run_phaseB.sh names {len(sh)} scripts; PIPELINE.md names {len(doc)}")
    for s in only_sh:
        print(f"  RUNS BUT UNDOCUMENTED   {s}")
    for s in only_doc:
        print(f"  DOCUMENTED BUT NOT RUN  {s}")
    if only_sh or only_doc:
        print(f"\nFAIL — {len(only_sh) + len(only_doc)} script(s) in one run order and not the other.")
        return 1
    print("\nPASS — the two run orders name the same scripts.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
