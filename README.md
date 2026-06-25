# skill-router

Intent-based skill router for AI agent harnesses. Classifies a user prompt and injects a directive naming the relevant skills to invoke — so the agent pulls the right skills automatically instead of relying on buried system-prompt instructions.

**No dependencies. Pure Python 3.9+. ~100 lines of classifier logic.**

## How it works

1. Your agent harness runs the adapter as a hook on each user prompt
2. The classifier detects intent (debugging, feature work, design, ship, security, perf, refactor…)
3. The adapter injects a fresh, high-salience directive naming the matching skills
4. The agent invokes those skills before acting — every time, not just when it remembers to

The classifier core (`core/classify.py`) is agent-agnostic. Adapters handle the harness-specific I/O format.

## Install

```bash
git clone https://github.com/jpoindexter/skill-router
cd skill-router
./install.sh              # Claude Code (default)
./install.sh vanta        # Vanta agent
./install.sh stdout       # plain stdout — any agent that reads shell output
```

## Supported adapters

| Adapter | Agent | Hook event | Output format |
|---------|-------|-----------|---------------|
| `adapters/claude-code.py` | [Claude Code](https://claude.ai/code) | `UserPromptSubmit` | `hookSpecificOutput.additionalContext` JSON |
| `adapters/vanta.py` | [Vanta](https://github.com/jpoindexter/Vanta) | `UserPromptSubmit` | `{"additionalContext": "..."}` JSON |
| `adapters/stdout.py` | Any | any | Plain text on stdout |

## Claude Code wiring

After `./install.sh`, add to `~/.claude/settings.json`:

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "matcher": "",
        "hooks": [{"type": "command", "command": "python3 ~/.claude/hooks/skill-router.py"}]
      }
    ]
  }
}
```

Open `/hooks` in Claude Code (or restart) to reload.

## Extending

Add a row to `BUCKETS` in `core/classify.py`:

```python
("my domain",
 r"\b(keyword|another ?keyword)\b",
 "skill-name-1, skill-name-2"),
```

Label = display name. Regex = intent signal. Skills = comma-separated hints injected into the directive.

## Behavior

- **Silent on conversation** — no output when no task signal is detected, so there's no noise on pure Q&A
- **Multiple buckets can match** — "fix this failing CSS" hits both debugging and design
- **Meta-suppression** — talking *about* the router/hook itself doesn't trigger it
- **Generic fallback** — any build/code verb that doesn't hit a specific bucket gets a "scan your skills" nudge

## Structure

```
skill-router/
├── core/
│   └── classify.py      # pure classifier — no I/O, no agent deps
├── adapters/
│   ├── claude-code.py   # Claude Code UserPromptSubmit hook
│   ├── vanta.py         # Vanta hook
│   └── stdout.py        # plain stdout
├── examples/            # sample hook payloads for testing
└── install.sh           # wires the right adapter
```

## Testing the classifier

```bash
echo '{"prompt": "fix this failing test"}' | python3 adapters/claude-code.py
echo '{"prompt": "build a landing page"}' | python3 adapters/claude-code.py
echo 'whats the difference between map and forEach' | python3 adapters/stdout.py  # silent
```

## License

MIT
