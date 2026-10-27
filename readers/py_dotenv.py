# readers/py_dotenv.py
import sys, json
from dotenv import dotenv_values
print(json.dumps(dict(dotenv_values(sys.argv[1])), ensure_ascii=False))
