#!/usr/bin/env bash
# readers/docker_env.sh
# Usage: readers/docker_env.sh <compose|run> <file-or-dir>   (prints JSON on stdout)
#   compose : Docker Compose reads the file via env_file, then we print the container's env
#   run     : `docker run --env-file` reads the file, then we print the container's env
# Needs: docker (and the compose plugin for "compose"). The image is pulled on first use.
set -u
IMAGE=${IMAGE:-alpine:3.20}

mode=${1:-}; target=${2:-}
if [[ $mode != compose && $mode != run || -z $target ]]; then
  echo "usage: $0 <compose|run> <file-or-dir>" >&2; exit 2
fi
command -v docker >/dev/null || { echo "docker not found" >&2; exit 2; }
target=${target%/}

json_escape() {
  local s=$1
  s=${s//\\/\\\\}; s=${s//\"/\\\"}
  s=${s//$'\n'/\\n}; s=${s//$'\r'/\\r}; s=${s//$'\t'/\\t}
  printf '%s' "$s"
}

load_env() {
  local -n _arr=$1
  local kv
  while IFS= read -r -d '' kv; do
    [[ $kv == *=* ]] && _arr[${kv%%=*}]=${kv#*=}
  done
}

# Variables the image/container sets by itself (HOSTNAME changes on every run)
declare -A IGNORE=([HOSTNAME]=1 [__RC__]=1)
declare -A BASE=()
load_env BASE < <(docker run --rm "$IMAGE" env -0)

# Run one fixture through the chosen reader; prints "env -0" of the container.
reader_cmd() {
  local file=$1
  if [[ $mode == run ]]; then
    docker run --rm --env-file "$file" "$IMAGE" env -0
  else
    local abs proj; abs=$(realpath "$file"); proj=$(mktemp -d)
    cat > "$proj/compose.yml" <<YAML
services:
  t:
    image: $IMAGE
    network_mode: none
    env_file: ["$abs"]
YAML
    docker compose -p dotenv_diff -f "$proj/compose.yml" run --rm --no-deps -T t env -0
    local rc=$?
    rm -rf "$proj"
    return $rc
  fi
}

read_one() {
  local file=$1 errfile err key rc first=1 abs
  declare -A after=()
  abs=$(realpath "$file"); errfile=$(mktemp)

  load_env after < <( { reader_cmd "$file" 2>"$errfile"; printf '__RC__=%s\0' "$?"; } )
  rc=${after[__RC__]:-?}
  err=$(<"$errfile"); rm -f "$errfile"
  err=${err//"$abs"/$file}          # keep absolute paths (and usernames) out of the output
  err=${err//"$HOME"/\~}

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

if [[ -d $target ]]; then
  printf '{'
  sep=''
  for f in "$target"/*.env; do
    printf '%s\n  "%s": ' "$sep" "$(basename "$f" .env)"
    read_one "$f" | sed '2,$s/^/  /'
    sep=','
  done
  printf '\n}\n'
else
  read_one "$target"; printf '\n'
fi
