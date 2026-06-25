#!/usr/bin/env python3
"""Claude Code adapter — UserPromptSubmit hook.

Reads the CC hook's stdin JSON ({"prompt": "..."}), classifies it, and
emits the hookSpecificOutput JSON that CC injects as additionalContext.

Wire in ~/.claude/settings.json:
  "UserPromptSubmit": [{"matcher": "", "hooks": [{"type": "command",
    "command": "python3 /path/to/adapters/claude-code.py"}]}]
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from core.classify import classify, FALLBACK_HINT

raw = sys.stdin.read()
try:
    prompt = json.loads(raw).get("prompt") or ""
except (ValueError, AttributeError):
    prompt = raw

results = classify(prompt)
if not results:
    sys.exit(0)

if results == [("_fallback", FALLBACK_HINT)]:
    directive = FALLBACK_HINT
else:
    rows = "; ".join(f"{label} -> {skills}" for label, skills in results)
    directive = (
        "Relevant skills detected. Before acting you MUST invoke the matching skills via "
        "the Skill tool (process skills like brainstorming/debugging FIRST, then "
        "implementation) — don't work from memory. "
        + rows
        + ". Invoke the ones that fit and name which you used."
    )

print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "UserPromptSubmit",
        "additionalContext": directive,
    }
}))
