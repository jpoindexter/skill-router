#!/usr/bin/env python3
"""Vanta adapter — prompt hook via .vanta/hooks.json.

Reads Vanta's hook payload JSON, classifies, and emits the additionalContext
format Vanta's `prompt`-type hooks inject into the agent's next turn.

Wire in .vanta/hooks.json:
  {"event": "UserPromptSubmit", "type": "command",
   "command": "python3 /path/to/adapters/vanta.py"}

Vanta hook payload shape (subset): {"prompt": "...", "session_id": "..."}
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from core.classify import classify, FALLBACK_HINT

raw = sys.stdin.read()
try:
    data   = json.loads(raw)
    prompt = data.get("prompt") or data.get("message") or ""
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
        "Relevant skills detected. Before acting invoke the matching skills "
        "(process skills like brainstorming/debugging FIRST, then implementation). "
        + rows
        + ". Invoke the ones that fit and name which you used."
    )

print(json.dumps({"additionalContext": directive}))
