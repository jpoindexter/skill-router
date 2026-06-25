#!/usr/bin/env node
/** Claude Code adapter — UserPromptSubmit hook.
 *
 * Reads CC's stdin JSON {"prompt":"..."}, classifies, emits hookSpecificOutput.
 *
 * Wire in ~/.claude/settings.json:
 *   "UserPromptSubmit": [{"matcher":"","hooks":[{"type":"command",
 *     "command":"node /path/to/dist/adapters/claude-code.js"}]}]
 */
import { classify, FALLBACK } from "../classify.js";

const raw = await new Promise<string>((res) => {
  let buf = "";
  process.stdin.setEncoding("utf8");
  process.stdin.on("data", (d) => (buf += d));
  process.stdin.on("end", () => res(buf));
});

let prompt = "";
try {
  const parsed = JSON.parse(raw);
  prompt = parsed?.prompt ?? "";
} catch {
  prompt = raw;
}

const results = classify(prompt);
if (!results.length) process.exit(0);

const isFallback = results.length === 1 && results[0]!.label === "_fallback";
const directive = isFallback
  ? FALLBACK.skills
  : "Relevant skills detected. Before acting you MUST invoke the matching skills via the Skill tool " +
    "(process skills like brainstorming/debugging FIRST, then implementation) — don't work from memory. " +
    results.map((r) => `${r.label} -> ${r.skills}`).join("; ") +
    ". Invoke the ones that fit and name which you used.";

process.stdout.write(
  JSON.stringify({
    hookSpecificOutput: {
      hookEventName: "UserPromptSubmit",
      additionalContext: directive,
    },
  }) + "\n"
);
