# fuzz.py
import random, json, subprocess, sys, tempfile, os
from dotenv import dotenv_values

ALPHABET = ["K", "=", " ", "#", "'", '"', "$", "{", "}", "\\", "v", "1", "export "]

def gen():
    n = random.randint(2, 10)
    return "".join(random.choice(ALPHABET) for _ in range(n)) + "\n"

def py(path):
    try:
        return dict(dotenv_values(path))
    except Exception as e:
        return {"error": type(e).__name__}

def node(path):
    code = "const d=require('dotenv');console.log(JSON.stringify(d.parse(require('fs').readFileSync(process.argv[1]))))"
    p = subprocess.run(["node", "-e", code, path], capture_output=True, text=True)
    return json.loads(p.stdout) if p.returncode == 0 else {"error": "node"}

READERS = {"python": py, "node": node}

random.seed(int(sys.argv[1]) if len(sys.argv) > 1 else 0)
found = {}
for _ in range(2000):
    line = gen()
    with tempfile.NamedTemporaryFile("w", suffix=".env", delete=False) as f:
        f.write(line)
    results = {name: fn(f.name) for name, fn in READERS.items()}
    os.unlink(f.name)
    if len({json.dumps(r, sort_keys=True) for r in results.values()}) > 1:
        found[line] = results

for line, res in sorted(found.items(), key=lambda kv: len(kv[0]))[:20]:
    print(repr(line), json.dumps(res))
print(f"\n{len(found)} disagreeing lines out of 2000")
