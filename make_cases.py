# make_cases.py
from pathlib import Path

CASES = {
    "empty_comment":  b"API_KEY=   # fill this in later\n",
    "empty_comment2": b"EMPTY_C2= #c\n",
    "value_comment":  b"V_C=x # c\n",
    "hash_in_value":  b"HASH=Tr0ub4dor#3\n",
    "hash_start":     b"COLOR=#ff0000\n",
    "bare":           b"BARE=\n",
    "export":         b"export KEY=v\n",
    "expand":         b"HOST=db\nURL=${HOST}:5432\n",
    "escapes":        b'A="a\\nb"\nB=\'a\\nb\'\n',
    "dup":            b"K=1\nK=2\n",
    "spaces":         b"KEY = v \nK2=v   \n",
    "multiline":      b'PEM="-----BEGIN\nabc\n-----END"\n',
    "crlf":           b"K=v\r\nL=w\r\n",
    "bom":            b"\xef\xbb\xbfK=v\n",
    "empty_file":     b"",
    "unterminated":   b'K="unterminated\nL=next\n',
}

out = Path("cases")
out.mkdir(exist_ok=True)
for name, data in CASES.items():
    (out / f"{name}.env").write_bytes(data)
