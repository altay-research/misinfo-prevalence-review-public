#!/usr/bin/env python3
"""
Tune the Scopus search: for each candidate filter, report (corpus size, recall vs
the Berriche seed set). Lets us choose the precision/recall trade-off on real numbers.

Reuses query() and SEEDS (exact-title identifiers) from recall_check.py.
Key read from $SCOPUS_KEY. Output saved to ../searches/tune_search_<stamp>.json.

Note: Scopus proximity `W/n` operates between terms/phrases; whether it accepts
parenthesised OR-groups as operands is tested empirically here (variant `prox`).
"""
import json, os, sys, time, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from recall_check import query, SEEDS  # noqa: E402

TOPIC = ('( misinformation OR disinformation OR "fake news" OR "false news" '
         'OR "unreliable news" OR "untrustworthy websites" OR "low-quality news" '
         'OR "junk news" )')
MEASURE = ('( exposure OR consumption OR consume* OR reach OR audience OR "news diet" '
           'OR "information diet" OR prevalence OR circulation OR sharing OR shared '
           'OR spread OR diffusion OR dissemination OR quantif* OR "how much" '
           'OR supersharer* OR "super-sharer*" OR traffic OR visits OR engagement OR scale )')
NOTCS_TITLE = (' AND NOT TITLE ( detection OR classifier OR classification '
               'OR "deep learning" OR "neural network" OR transformer )')
EMPIRICAL = ('( empirical OR survey OR panel OR sample OR respondents OR dataset '
             'OR proportion OR percent OR "share of" OR users OR participants )')
# proximity core (smaller operand lists; tests whether OR-groups are accepted with W/n)
TOPIC_CORE = '( misinformation OR disinformation OR "fake news" OR "false news" )'
MEAS_CORE = ('( exposure OR consumption OR sharing OR shared OR spread OR diffusion '
             'OR prevalence OR reach OR audience OR circulation OR supersharer* )')

# consumption-only measurement family (NO sharing/spread/diffusion/supersharer terms)
# — to quantify how much the sharing side adds to corpus size and recall.
MEASURE_CONS = ('( exposure OR consumption OR consume* OR reach OR audience OR "news diet" '
                'OR "information diet" OR prevalence OR circulation OR traffic OR visits )')

VARIANTS = {
    "consumption_only": "TITLE-ABS-KEY ( %s AND %s )%s" % (TOPIC, MEASURE_CONS, NOTCS_TITLE),
    "v2_baseline":  "TITLE-ABS-KEY ( %s AND %s )%s" % (TOPIC, MEASURE, NOTCS_TITLE),
    "prox_W5":      "TITLE-ABS-KEY ( %s W/5 %s )%s" % (TOPIC_CORE, MEAS_CORE, NOTCS_TITLE),
    "empirical":    "TITLE-ABS-KEY ( %s AND %s AND %s )%s" % (TOPIC, MEASURE, EMPIRICAL, NOTCS_TITLE),
    "prox_AND_emp": "TITLE-ABS-KEY ( ( %s W/5 %s ) AND %s )%s" % (TOPIC_CORE, MEAS_CORE, EMPIRICAL, NOTCS_TITLE),
}


def corpus_size(q):
    n, _ = query(q)
    return n


def recall(filt):
    indexed = caught = 0
    for label, idq in SEEDS:
        n_idx, _ = query(idq); time.sleep(0.6)
        if n_idx >= 1:
            indexed += 1
            c, _ = query("( %s ) AND %s" % (idq, filt)); time.sleep(0.6)
            if c >= 1:
                caught += 1
    return caught, indexed


def main():
    out = {}
    print("%-14s %12s   %s" % ("variant", "corpus", "recall"))
    print("-" * 50)
    for name, q in VARIANTS.items():
        size = corpus_size(q); time.sleep(0.6)
        if size == -1:
            print("%-14s %12s   (query rejected by Scopus)" % (name, "ERR"))
            out[name] = {"query": q, "corpus": "ERR"}
            continue
        c, idx = recall(q)
        print("%-14s %12d   %d/%d seeds" % (name, size, c, idx))
        out[name] = {"query": q, "corpus": size, "recall_caught": c, "recall_indexed": idx}
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d_%H%M%S")
    path = os.path.join(HERE, "..", "searches", "tune_search_%s.json" % stamp)
    with open(path, "w") as f:
        json.dump({"run_utc": stamp, "variants": out}, f, indent=2, ensure_ascii=False)
    print("saved ->", os.path.relpath(path, HERE))


if __name__ == "__main__":
    main()
