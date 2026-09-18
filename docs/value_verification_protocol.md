# 100%-confidence value verification protocol (quote-anchored)

STANDARD (Sacha, 2026-06-22): **no reported value may be wrong.** Every value entering the
synthesis must be anchored to a verbatim quote from the source stating that exact number.

PROCESS per value:
1. Search the FULL source text (untruncated) for the figure + its context.
2. Return the EXACT verbatim sentence/table text containing the number (the `source_quote`),
   plus where it appears.
3. Verdict:
   - CONFIRM — quote states the value as extracted (for that construct/denominator).
   - CORRECT:<newval> — quote states a different number; fix to the quoted value.
   - DROP — the number is NOT in the source verbatim (guessed, rounded, or a secondary
     citation of another study). The value is removed from the reported set.
4. Two independent passes; both must CONFIRM the same value with a supporting quote.
   Any disagreement is adjudicated against the quote (source = ground truth).
5. `source_quote` is stored in the dataset → every reported value is human-checkable.

Result: the reported dataset contains ONLY quote-anchored values. Fewer values, zero
unverifiable ones. Abstract-only studies are anchored to the abstract if the figure is
verbatim there, else dropped.
