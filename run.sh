#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR/compose"

cmd="${1:-}"
case "$cmd" in
  up)
    podman-compose -f podman-compose.yml up -d --build
    ;;
  down)
    podman-compose -f podman-compose.yml down
    ;;
  index)
    podman exec -it traceit-api python -m indexers.run --repos /app/config/repos.csv
    ;;
  dbmeta)
    podman exec -it traceit-api python -c "from indexers import db_oracle as d; d.run()"
    ;;
  graphload)
    podman exec -it traceit-api python /app/graphdb/load.py
    ;;
  eval)
    podman exec -it traceit-api python /app/eval/run_eval.py --file /app/eval/golden.jsonl
    ;;
  *)
    echo "Usage: ./run.sh {up|down|index|dbmeta|graphload|eval}"
    exit 1
    ;;
esac
