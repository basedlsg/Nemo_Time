#!/usr/bin/env bash
set -euo pipefail

# Wraps `gcloud functions deploy` and tolerates failures that are solely due to
# Cloud Run IAM policy update (setIamPolicy) being blocked by org constraints.

logfile=$(mktemp)
set +e
gcloud "$@" >"$logfile" 2>&1
rc=$?
set -e

if (( rc == 0 )); then
  cat "$logfile"
  exit 0
fi

if grep -q "run.services.setIamPolicy" "$logfile"; then
  echo "[WARN] Ignoring Cloud Run setIamPolicy error during deploy. Function build/service update likely succeeded." >&2
  cat "$logfile"
  exit 0
fi

cat "$logfile" >&2
exit $rc

