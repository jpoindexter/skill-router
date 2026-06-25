#!/usr/bin/env node
/** Stdout adapter — plain text, any agent that reads shell output.
 *
 * Reads prompt from stdin (raw text or {"prompt":"..."} JSON).
 * Silent (exit 0, no output) when no task signal detected.
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
if (isFallback) {
  process.stdout.write(FALLBACK.skills + "\n");
} else {
  process.stdout.write(
    "Relevant skills detected. Before acting invoke the matching skills " +
    "(process skills like brainstorming/debugging FIRST, then implementation). " +
    results.map((r) => `${r.label} -> ${r.skills}`).join("; ") + "\n"
  );
}
