#!/usr/bin/env bash
# skill-router install — wires the right adapter for your agent.
# Usage: ./install.sh [claude-code|vanta|stdout]
# Default: claude-code

set -e
REPO="$(cd "$(dirname "$0")" && pwd)"
AGENT="${1:-claude-code}"

case "$AGENT" in
  claude-code)
    TARGET="$HOME/.claude/hooks/skill-router.py"
    cp "$REPO/adapters/claude-code.py" "$TARGET"
    chmod +x "$TARGET"
    echo "Installed: $TARGET"
    echo ""
    echo "Wire in ~/.claude/settings.json under hooks.UserPromptSubmit:"
    cat <<'JSON'
{
  "matcher": "",
  "hooks": [{"type": "command", "command": "python3 ~/.claude/hooks/skill-router.py"}]
}
JSON
    echo ""
    echo "Then open /hooks in Claude Code (or restart) to reload config."
    ;;
  vanta)
    TARGET="$HOME/.vanta/hooks/skill-router.py"
    mkdir -p "$(dirname "$TARGET")"
    cp "$REPO/adapters/vanta.py" "$TARGET"
    chmod +x "$TARGET"
    echo "Installed: $TARGET"
    echo ""
    echo "Wire in .vanta/hooks.json:"
    cat <<'JSON'
{"event": "UserPromptSubmit", "type": "command",
 "command": "python3 ~/.vanta/hooks/skill-router.py"}
JSON
    ;;
  stdout)
    TARGET="/usr/local/bin/skill-router"
    cp "$REPO/adapters/stdout.py" "$TARGET"
    chmod +x "$TARGET"
    echo "Installed: $TARGET"
    echo "Usage: echo 'build a landing page' | skill-router"
    ;;
  *)
    echo "Unknown agent: $AGENT"
    echo "Usage: $0 [claude-code|vanta|stdout]"
    exit 1
    ;;
esac
