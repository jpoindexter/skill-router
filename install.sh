#!/usr/bin/env bash
# skill-router install — builds and wires the right adapter for your agent.
# Usage: ./install.sh [claude-code|vanta|stdout]
# Default: claude-code
# Requires: node >= 22, npm

set -e
REPO="$(cd "$(dirname "$0")" && pwd)"
AGENT="${1:-claude-code}"

echo "Building..."
cd "$REPO" && npm install --silent && npm run build --silent
echo "Built ✓"

case "$AGENT" in
  claude-code)
    TARGET="$HOME/.claude/hooks/skill-router.js"
    cp "$REPO/dist/adapters/claude-code.js" "$TARGET"
    # copy the classify module it imports
    mkdir -p "$HOME/.claude/hooks/dist"
    cp -r "$REPO/dist/" "$HOME/.claude/hooks/dist/"
    echo "Installed: $HOME/.claude/hooks/dist/"
    echo ""
    echo "Wire in ~/.claude/settings.json under hooks.UserPromptSubmit:"
    cat <<'JSON'
{
  "matcher": "",
  "hooks": [{"type": "command", "command": "node ~/.claude/hooks/dist/adapters/claude-code.js"}]
}
JSON
    echo ""
    echo "Then open /hooks in Claude Code (or restart) to reload config."
    ;;
  vanta)
    TARGET="$HOME/.vanta/hooks"
    mkdir -p "$TARGET"
    cp -r "$REPO/dist/" "$TARGET/dist/"
    echo "Installed: $TARGET/dist/"
    echo ""
    echo "Wire in .vanta/hooks.json:"
    cat <<'JSON'
{"event": "UserPromptSubmit", "type": "command",
 "command": "node ~/.vanta/hooks/dist/adapters/vanta.js"}
JSON
    ;;
  stdout)
    TARGET="/usr/local/bin/skill-router"
    # write a thin launcher so node can resolve the dist/ imports
    cat > "$TARGET" <<SCRIPT
#!/usr/bin/env bash
node "$REPO/dist/adapters/stdout.js"
SCRIPT
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
