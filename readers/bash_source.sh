#!/usr/bin/env bash
# readers/bash_source.sh
# Usage: readers/bash_source.sh <file-or-dir>   (prints JSON on stdout)
# WARNING: this EXECUTES each file with bash. Only run it on fixtures you trust.
set -u

# Escape a string for use inside a JSON "..." value
json_escape() {
  local s=$1
  s=${s//\\/\\\\}
  s=${s//\"/\\\"}
  s=${s//$'\n'/\\n}
  s=${s//$'\r'/\\r}
  s=${s//$'\t'/\\t}
  printf '%s' "$s"
}

# Load NUL-separated KEY=VALUE records from stdin into the array named $1
load_env() {
  local -n _arr=$1
  local kv
  while IFS= read -r -d '' kv; do
    [[ $kv == *=* ]] && _arr[${kv%%=*}]=${kv#*=}
  done
}

# Variables bash sets by itself, plus our helper variables
declare -A IGNORE=([SHLVL]=1 [_]=1 [PWD]=1 [OLDPWD]=1 [rc]=1 [__RC__]=1)

# Baseline: what an empty-environment bash already has
declare -A BASE=()
load_env BASE < <(env -i bash -c 'env -0')

read_one() {
  local file=$1 errfile err key rc=0 first=1
  declare -A after=()
  errfile=$(mktemp)

  # Run in an empty environment; set -a exports everything the file assigns.
  load_env after < <(
    env -i bash -c 'set -a; source "$1"; rc=$?; set +a; env -0; printf "__RC__=%s\0" "$rc"' _ "$file" 2>"$errfile"
  )
  rc=${after[__RC__]:-?}
  err=$(<"$errfile"); rm -f "$errfile"

  printf '{\n  "exit": %s,\n' "$rc"
  [[ -n $err ]] && printf '  "stderr": "%s",\n' "$(json_escape "$err")"
  printf '  "values": {'
  while IFS= read -r key; do
    [[ -z $key || -n ${IGNORE[$key]:-} ]] && continue
    [[ ${BASE[$key]-__unset__} == "${after[$key]}" ]] && continue
    (( first )) || printf ','
    first=0
    printf '\n    "%s": "%s"' "$(json_escape "$key")" "$(json_escape "${after[$key]}")"
  done < <(printf '%s\n' "${!after[@]}" | sort)
  (( first )) && printf '}\n}' || printf '\n  }\n}'
}

target=${1:-}
[[ -z $target ]] && { echo "usage: $0 <file-or-dir>" >&2; exit 2; }
target=${target%/}   # avoid "cases//x.env" in error messages

if [[ -d $target ]]; then
  printf '{'
  sep=''
  for f in "$target"/*.env; do
    name=$(basename "$f" .env)
    printf '%s\n  "%s": ' "$sep" "$name"
    read_one "$f" | sed '2,$s/^/  /'
    sep=','
  done
  printf '\n}\n'
else
  read_one "$target"; printf '\n'
fi
