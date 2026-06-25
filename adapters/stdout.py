#!/usr/bin/env python3
"""Stdout adapter — agent-agnostic plain text output.

Any agent that can run a shell command and read stdout can use this.
Reads prompt from stdin (raw text or {"prompt": "..."} JSON).
Exits 0 with no output when no task signal is detected.
Exits 0 with plain directive text when skills are relevant.

Example (Vanta hook, generic CI, any shell-invocable agent):
  prompt=$(cat) && echo "$prompt" | python3 /path/to/adapters/stdout.py
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
    print(FALLBACK_HINT)
else:
    rows = "; ".join(f"{label} -> {skills}" for label, skills in results)
    print(
        "Relevant skills detected. Before acting invoke the matching skills "
        "(process skills like brainstorming/debugging FIRST, then implementation). "
        + rows
    )
