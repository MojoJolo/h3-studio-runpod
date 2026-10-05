#!/usr/bin/env bash
# H3 Studio setup check (macOS / Linux / WSL). Safe to re-run; it only installs runpodctl if you say yes.
set -u
cd "$(dirname "$0")/.."
ok=0; warn=0
pass() { echo "  ✓ $1"; }
fail() { echo "  ✗ $1"; ok=1; }
note() { echo "  • $1"; warn=1; }
OS=$(uname -s); ARCH=$(uname -m)
echo "H3 Studio setup check ($OS $ARCH)"

echo "Tools:"
command -v python3 >/dev/null && pass "python3 $(python3 -c 'import sys;print(".".join(map(str,sys.version_info[:2])))')" || fail "python3 missing"
python3 -c 'import PIL' 2>/dev/null && pass "Pillow" || fail "Pillow missing: pip3 install pillow"
command -v ffmpeg >/dev/null && pass "ffmpeg" || fail "ffmpeg missing (macOS: brew install ffmpeg · Linux/WSL: sudo apt install ffmpeg)"
command -v ssh >/dev/null && pass "ssh" || fail "ssh missing"

RPC=${RUNPODCTL:-$(command -v runpodctl || echo "$HOME/.local/bin/runpodctl")}
if [ -x "$RPC" ]; then pass "runpodctl ($("$RPC" version 2>/dev/null | head -1))"
else
  echo "  ✗ runpodctl not found"
  read -r -p "    Install runpodctl into ~/.local/bin now? [y/N] " a
  if [ "${a:-n}" = y ]; then
    case "$OS" in Darwin) asset="runpodctl-darwin-all.tar.gz";; Linux) [ "$ARCH" = aarch64 ] && asset="runpodctl-linux-arm64.tar.gz" || asset="runpodctl-linux-amd64.tar.gz";; *) asset="";; esac
    url=$(curl -s https://api.github.com/repos/runpod/runpodctl/releases/latest | python3 -c "import json,sys;print(next((x['browser_download_url'] for x in json.load(sys.stdin)['assets'] if x['name']=='$asset'),''))")
    if [ -n "$url" ]; then mkdir -p ~/.local/bin && curl -sL "$url" | tar -xz -C ~/.local/bin runpodctl && chmod +x ~/.local/bin/runpodctl && pass "installed ~/.local/bin/runpodctl (add ~/.local/bin to PATH)"; RPC=~/.local/bin/runpodctl
    else fail "no runpodctl release asset found for $OS $ARCH; install manually from github.com/runpod/runpodctl/releases"; fi
  else ok=1; fi
fi

echo "Keys:"
[ -f .env ] && set -a && . ./.env && set +a
if [ -n "${RUNPOD_API_KEY:-}" ] || grep -qE "apikey *= *['\"][^'\"]+" ~/.runpod/config.toml 2>/dev/null; then pass "Runpod API key"; else fail "Runpod API key missing: cp .env.example .env and set RUNPOD_API_KEY"; fi
[ -n "${HF_TOKEN:-}" ] || [ -s ~/.cache/huggingface/token ] && pass "Hugging Face token" || note "no Hugging Face token (optional; downloads may be slower)"
[ -f ~/.runpod/ssh/runpodctl-ssh-key ] && pass "runpodctl SSH key" || fail "no runpodctl SSH key: run 'runpodctl doctor'"
if [ -x "$RPC" ] && { [ -n "${RUNPOD_API_KEY:-}" ] || [ -f ~/.runpod/config.toml ]; }; then
  "$RPC" pod list -o json >/dev/null 2>&1 && pass "Runpod API reachable" || fail "Runpod API call failed (check the key)"
fi

echo "Optional:"
command -v claude >/dev/null && pass "Claude Code CLI (Auto mode available)" || note "Claude Code CLI not installed: Auto mode unavailable (everything else works)"

echo
[ $ok -eq 0 ] && echo "Ready. Run: python3 gui/server.py" || echo "Fix the ✗ items above, then re-run this script."
exit $ok
