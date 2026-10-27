#!/usr/bin/env python3
"""Build the reader-comparison table from results/*.json.

Usage:
  python3 compare.py                 # only the cases where readers differ
  python3 compare.py --all           # every case
  python3 compare.py --cases cases/  # label rows with the fixture's content
"""
import argparse, json, sys
from pathlib import Path

# column name -> (results file, how to pull the values out of one case entry,
#                 whether the entry has an "exit" status to flag)
COLUMNS = {
    "python-dotenv":           ("python-dotenv.json", lambda e: e,              False),
    "Node dotenv":             ("node-dotenv.json",   lambda e: e["plain"],     False),
    "Node + expand":           ("node-dotenv.json",   lambda e: e["expanded"],  False),
    "bash `source`":           ("bash-source.json",   lambda e: e["values"],    True),
    "Compose":                 ("compose.json",       lambda e: e["values"],    True),
    "`docker run --env-file`": ("docker-run.json",    lambda e: e["values"],    True),
}


def load(results_dir):
    files = {}
    for fname, _, _ in COLUMNS.values():
        if fname not in files:
            files[fname] = json.loads((results_dir / fname).read_text(encoding="utf-8"))
    return files


def values_of(files, col, case):
    fname, pick, _ = COLUMNS[col]
    return pick(files[fname][case])


def failed(files, col, case):
    fname, _, has_exit = COLUMNS[col]
    return has_exit and files[fname][case]["exit"] != 0


def vis(s):
    # Make invisible characters visible (CR, LF, BOM) and escape quotes
    return json.dumps(s)[1:-1]


def cell(values, is_failed):
    if values:
        text = ", ".join(f'{vis(k)}="{vis(v)}"' for k, v in values.items())
    else:
        text = "(nothing set)"
    text = text.replace("|", "\\|")
    if is_failed:
        text += " ⚠ error"
    return f"`{text}`"


def label(cases_dir, case):
    if not cases_dir:
        return f"`{case}`"
    raw = (cases_dir / f"{case}.env").read_bytes().decode("utf-8", errors="replace")
    raw = raw.replace("\ufeff", "<BOM>").replace("\r", "<CR>").rstrip("\n")
    raw = raw.replace("\n", " ⏎ ") or "(empty file)"
    return f"`{raw}`".replace("|", "\\|")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="results")
    ap.add_argument("--cases")
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()

    # Skip readers whose results file doesn't exist yet
    for name in [n for n, (f, _, _) in COLUMNS.items() if not (Path(a.results) / f).exists()]:
        print(f"note: skipping {name} (no results file yet)", file=sys.stderr)
        del COLUMNS[name]

    files = load(Path(a.results))
    cases = sorted(files["python-dotenv.json"])
    cases_dir = Path(a.cases) if a.cases else None

    rows, agree = [], []
    for case in cases:
        vals = {c: values_of(files, c, case) for c in COLUMNS}
        fails = {c: failed(files, c, case) for c in COLUMNS}
        signature = {json.dumps(v, sort_keys=True) for v in vals.values()}
        differs = len(signature) > 1 or any(fails.values())
        row = [label(cases_dir, case)] + [cell(vals[c], fails[c]) for c in COLUMNS]
        (rows if (differs or a.all) else agree).append((case, row, differs))

    print("| Fixture | " + " | ".join(COLUMNS) + " |")
    print("|---|" + "---|" * len(COLUMNS))
    for _, row, _ in rows:
        print("| " + " | ".join(row) + " |")

    n_diff = sum(1 for _, _, d in rows if d)
    print(f"\n{n_diff} of {len(cases)} fixtures give different results across readers.")
    if agree:
        print("Identical everywhere: " + ", ".join(f"`{c}`" for c, _, _ in agree) + ".")


if __name__ == "__main__":
    main()
