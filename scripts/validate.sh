#!/usr/bin/env bash
set -euo pipefail

python3 -m unittest discover -s tests -v
python3 -m compileall -q src tests
python3 -m json.tool config/policy.json >/dev/null
python3 -m json.tool examples/approved-request.json >/dev/null
python3 -m json.tool examples/denied-request.json >/dev/null

first="$(python3 src/control_plane.py --request examples/approved-request.json)"
second="$(python3 src/control_plane.py --request examples/approved-request.json)"
test "$first" = "$second"

if python3 src/control_plane.py --request examples/denied-request.json >/dev/null; then
  echo 'Denied fixture unexpectedly passed.' >&2
  exit 1
fi

git diff --check
git check-ignore -q goal.md

if command -v bicep >/dev/null 2>&1; then
  bicep build infra/main.bicep --stdout >/dev/null
else
  echo 'Bicep compiler unavailable; compile remains a documented external gate.'
fi
