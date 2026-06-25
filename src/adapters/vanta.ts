#!/usr/bin/env node
/** Vanta adapter — .vanta/hooks.json command hook.
 *
 * Reads Vanta's hook payload {"prompt":"...","session_id":"..."},
 * classifies, and emits {"additionalContext":"..."}.
 *
 * Wire in .vanta/hooks.json:
 *   {"event":"UserPromptSubmit","type":"command",
 *    "command":"node /path/to/dist/adapters/vanta.js"}
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
  prompt = parsed?.prompt ?? parsed?.message ?? "";
} catch {
  prompt = raw;
}

const results = classify(prompt);
if (!results.length) process.exit(0);

const isFallback = results.length === 1 && results[0]!.label === "_fallback";
const directive = isFallback
  ? FALLBACK.skills
  : "Relevant skills detected. Before acting invoke the matching skills " +
    "(process skills like brainstorming/debugging FIRST, then implementation). " +
    results.map((r) => `${r.label} -> ${r.skills}`).join("; ") +
    ". Invoke the ones that fit and name which you used.";

process.stdout.write(JSON.stringify({ additionalContext: directive }) + "\n");
