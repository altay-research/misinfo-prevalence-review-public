#!/usr/bin/env bash
# serve_site.sh — look at the built site locally.
# The pages fetch their data as JSON modules, which a file:// open blocks, so they need a server.
#   bash scripts/serve_site.sh          # http://localhost:8777
#   bash scripts/serve_site.sh 9000     # another port
set -euo pipefail
PORT="${1:-8777}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
[ -d "$ROOT/site" ] || [ -d "$ROOT/companion/site" ] || { echo "no site/ yet — run: python3 scripts/build_site.py"; exit 1; }
[ -d "$ROOT/site" ] || ROOT="$ROOT/companion"    # the public package publishes the site under companion/
echo "serving $ROOT/site at http://localhost:$PORT  (ctrl-C to stop)"
command -v open >/dev/null && (sleep 1 && open "http://localhost:$PORT") &
exec python3 -m http.server "$PORT" --directory "$ROOT/site"
