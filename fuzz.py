#!/usr/bin/env python3
"""Differential fuzzing: random one-line .env files through python-dotenv and Node dotenv.

Usage: python3 fuzz.py [seed] [count]      (defaults: seed 0, 2000 lines)
"""
import io, json, logging, random, subprocess, sys
from collections import Counter
from dotenv import dotenv_values

# python-dotenv logs "could not parse statement" for every malformed line; silence it
logging.getLogger("dotenv.main").setLevel(logging.CRITICAL)

ALPHABET = ["K", "=", " ", "#", "'", '"', "$", "{", "}", "\\", "v", "1", "export "]

NODE_BATCH = """
const d = require('dotenv');
const lines = JSON.parse(require('fs').readFileSync(0, 'utf8'));
console.log(JSON.stringify(lines.map(l => d.parse(Buffer.from(l)))));
"""


def gen():
    n = random.randint(2, 10)
    return "".join(random.choice(ALPHABET) for _ in range(n)) + "\n"


def py(line):
    try:
        return dict(dotenv_values(stream=io.StringIO(line)))
    except Exception as e:
        return {"error": type(e).__name__}


def node_all(lines):
    p = subprocess.run(["node", "-e", NODE_BATCH], input=json.dumps(lines),
                       capture_output=True, text=True, check=True)
    return json.loads(p.stdout)


def features(line):
    f = []
    if "#" in line: f.append("#")
    if "$" in line or "{" in line: f.append("$ or {")
    if '"' in line: f.append('"')
    if "'" in line: f.append("'")
    if "\\" in line: f.append("backslash")
    if line.startswith("export ") or " export " in line: f.append("export")
    return f or ["(none of these)"]


def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 2000
    random.seed(seed)
    lines = sorted({gen() for _ in range(count)})        # unique lines only
    node = node_all(lines)

    found = {}
    for line, n in zip(lines, node):
        p = py(line)
        if json.dumps(p, sort_keys=True) != json.dumps(n, sort_keys=True):
            found[line] = {"python": p, "node": n}

    # Lines with no "=" are a class of their own: python-dotenv reports the bare name
    # with value None, Node ignores the line. Count them, then look at everything else.
    no_eq = {l: r for l, r in found.items() if "=" not in l}
    found = {l: r for l, r in found.items() if "=" in l}

    print(f"seed={seed}: {len(lines)} unique lines, {len(no_eq) + len(found)} disagree")
    print(f"  {len(no_eq)} have no '=' (python-dotenv: name -> None, Node: line ignored)")
    print(f"  {len(found)} contain '=' and still disagree")
    print("\nShortest disagreements among lines with '=':")
    for line, res in sorted(found.items(), key=lambda kv: (len(kv[0]), kv[0]))[:25]:
        print(f"  {line!r:22} python={json.dumps(res['python'])}  node={json.dumps(res['node'])}")

    c = Counter(ft for line in found for ft in features(line))
    print("\nDisagreeing lines with '=' that contain each feature:")
    for ft, k in c.most_common():
        print(f"  {ft:16} {k:5}  ({100 * k / len(found):.0f}%)")


if __name__ == "__main__":
    main()
