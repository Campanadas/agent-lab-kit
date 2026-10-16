---
name: check-the-ledger
description: Use before investigating, measuring, deriving or re-running anything - the moment you have a question and are about to open a file to answer it. Also use before quoting any number, ratio or constant from the project's record, before asking the owner for a paper or a dataset, and whenever you are unsure whether a result is still live.
---

# Look before you derive

```
RE-DERIVING A SETTLED RESULT IS THE MOST EXPENSIVE MISTAKE AVAILABLE.
IT COSTS A SESSION AND PRODUCES NOTHING.
```

In a long project no session can hold the whole record, so every session is tempted to walk in circles: rebuild a mechanism that
was built months ago, ask the owner for a paper that is already on disk, cite a number that was retracted.

## The move (before the first file read, not after the third)

```bash
python3 tools/labkit.py grep "<the quantity>|<the method>|<the source's first author>"
python3 tools/labkit.py status N        # for every #N you are about to rely on
```

- Search by **every name** the thing has: the quantity, its symbol, the method, the dataset, the paper's first author.
- Search for the **mechanism or build** too, not just the number: "has this loop / model / pipeline been built before?"
- Before asking for a file or paper, search the project's files index or papers folder for it.

## Reading what you find

- `DEAD` means the number or claim is dead. Do not cite it; if you find it still in use somewhere, that is a finding.
- A tag such as `REFINED` or `WEAKENED` means the finding stands with a qualification: read the finding that tagged it.
- `labkit check FILE` lists every #N a document relies on with its standing. Run it before anything leaves the project.

## When it is not in the ledger

Then it is genuinely open: proceed, pre-register (`prereg` skill), and record the result as a new finding with
`labkit add`. Cite what you found earlier in the script's header, including the near-misses, so the next session sees the chain.
