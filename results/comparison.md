| Fixture | python-dotenv | Node dotenv | Node + expand | bash `source` | Compose | `docker run --env-file` |
|---|---|---|---|---|---|---|
| `<BOM>K=v` | `\ufeffK="v"` | `K="v"` | `K="v"` | `(nothing set) ⚠ error` | `K="v"` | `K="v"` |
| `K=v<CR> ⏎ L=w<CR>` | `K="v", L="w"` | `K="v", L="w"` | `K="v", L="w"` | `K="v\r", L="w\r"` | `K="v", L="w"` | `K="v", L="w"` |
| `API_KEY=   # fill this in later` | `API_KEY="# fill this in later"` | `API_KEY=""` | `API_KEY=""` | `API_KEY=""` | `API_KEY="# fill this in later"` | `API_KEY="   # fill this in later"` |
| `EMPTY_C2= #c` | `EMPTY_C2="#c"` | `EMPTY_C2=""` | `EMPTY_C2=""` | `EMPTY_C2=""` | `EMPTY_C2="#c"` | `EMPTY_C2=" #c"` |
| `A="a\nb" ⏎ B='a\nb'` | `A="a\nb", B="a\\nb"` | `A="a\nb", B="a\\nb"` | `A="a\nb", B="a\\nb"` | `A="a\\nb", B="a\\nb"` | `A="a\nb", B="a\\nb"` | `A="\"a\\nb\"", B="'a\\nb'"` |
| `HOST=db ⏎ URL=${HOST}:5432` | `HOST="db", URL="db:5432"` | `HOST="db", URL="${HOST}:5432"` | `HOST="db", URL="db:5432"` | `HOST="db", URL="db:5432"` | `HOST="db", URL="db:5432"` | `HOST="db", URL="${HOST}:5432"` |
| `export KEY=v` | `KEY="v"` | `KEY="v"` | `KEY="v"` | `KEY="v"` | `KEY="v"` | `(nothing set) ⚠ error` |
| `HASH=Tr0ub4dor#3` | `HASH="Tr0ub4dor#3"` | `HASH="Tr0ub4dor"` | `HASH="Tr0ub4dor"` | `HASH="Tr0ub4dor#3"` | `HASH="Tr0ub4dor#3"` | `HASH="Tr0ub4dor#3"` |
| `COLOR=#ff0000` | `COLOR="#ff0000"` | `COLOR=""` | `COLOR=""` | `COLOR="#ff0000"` | `COLOR="#ff0000"` | `COLOR="#ff0000"` |
| `PEM="-----BEGIN ⏎ abc ⏎ -----END"` | `PEM="-----BEGIN\nabc\n-----END"` | `PEM="-----BEGIN\nabc\n-----END"` | `PEM="-----BEGIN\nabc\n-----END"` | `PEM="-----BEGIN\nabc\n-----END"` | `PEM="-----BEGIN\nabc\n-----END"` | `PEM="\"-----BEGIN"` |
| `KEY = v  ⏎ K2=v   ` | `K2="v", KEY="v"` | `K2="v", KEY="v"` | `K2="v", KEY="v"` | `K2="v"` | `K2="v", KEY="v"` | `(nothing set) ⚠ error` |
| `K="unterminated ⏎ L=next` | `L="next"` | `K="\"unterminated", L="next"` | `K="\"unterminated", L="next"` | `(nothing set) ⚠ error` | `(nothing set) ⚠ error` | `K="\"unterminated", L="next"` |
| `V_C=x # c` | `V_C="x"` | `V_C="x"` | `V_C="x"` | `V_C="x"` | `V_C="x"` | `V_C="x # c"` |

13 of 16 fixtures give different results across readers.
Identical everywhere: `bare`, `dup`, `empty_file`.
