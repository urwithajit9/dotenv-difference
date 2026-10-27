# readers/py_dotenv_all.py
import argparse, json, sys
from pathlib import Path
from dotenv import dotenv_values


def read(path):
    try:
        return dict(dotenv_values(path))
    except Exception as e:
        # Record the failure instead of crashing the whole run
        return {"error": f"{type(e).__name__}: {e}"}


def main():
    ap = argparse.ArgumentParser(description="Parse .env files with python-dotenv and emit JSON")
    ap.add_argument("path", help="a .env file, or a directory of .env files")
    ap.add_argument("--out", help="write JSON to this file instead of stdout")
    args = ap.parse_args()

    p = Path(args.path)
    if p.is_dir():
        result = {f.stem: read(f) for f in sorted(p.glob("*.env"))}
    else:
        result = read(p)

    text = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    main()
