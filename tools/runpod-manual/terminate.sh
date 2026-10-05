#!/usr/bin/env bash
# Last step: terminate the pod (deletes everything on it, stops billing). Usage: ./terminate.sh <pod-id>
set -euo pipefail
~/.local/bin/runpodctl pod delete "$1"
~/.local/bin/runpodctl pod list
