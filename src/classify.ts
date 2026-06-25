/** Pure intent classifier — no I/O, no agent-specific formats.
 *
 * Call classify(prompt) → array of {label, skills}.
 * Empty array = pure conversation (no nudge needed).
 * Single _fallback entry = generic task signal with no specific bucket match.
 * Extend by adding rows to BUCKETS or editing the regex constants below.
 */

export interface Match {
  label: string;
  skills: string;
}

type Bucket = [label: string, pattern: RegExp, skills: string];

// ── intent buckets ────────────────────────────────────────────────────────────

export const BUCKETS: Bucket[] = [
  [
    "debugging",
    /\b(bug|debug|error|exception|stack ?trace|traceback|crash|broken|failing|fails?|isn.?t working|not working|regression|race condition|flaky)\b/i,
    "superpowers:systematic-debugging (first), debug, root-cause-tracing",
  ],
  [
    "feature work",
    /\b(new feature|add (a |the )?feature|feature for|let.?s build|build (a|the|me|out)\b|greenfield)\b/i,
    "superpowers:brainstorming (first), feature-development, superpowers:test-driven-development",
  ],
  [
    "testing",
    /\b(unit tests?|write tests?|add tests?|test coverage|coverage|vitest|jest|test suite|failing tests?)\b/i,
    "superpowers:test-driven-development, test-master, qa",
  ],
  [
    "ship / review",
    /\b(ship|merge|deploy|release|publish|pull request|pre-?flight|ready to ship|open a pr)\b|\bpr\b/i,
    "ship-preflight, review, security-review, superpowers:verification-before-completion",
  ],
  [
    "security",
    /\b(security|secure|auth(entication|orization)?|vulnerab|cve|xss|csrf|sql ?injection|secret|owasp|sanitiz)\b/i,
    "security-check, security-scan, security-reviewer",
  ],
  [
    "performance",
    /\b(performance|slow|optimi[sz]e|latency|bundle size|memory leak|n\+1|profil|janky)\b/i,
    "performance-optimization, dec-web-performance",
  ],
  [
    "refactor / cleanup",
    /\b(refactor|clean ?up|simplify|tidy|dead code|code smell|tech debt)\b/i,
    "refactor-clean, enforcing-code-size, code-simplifier",
  ],
];

// ── design intent ─────────────────────────────────────────────────────────────

const DESIGN_INTENT =
  /\b(websites?|web ?app|webpage|web page|landing page|home ?page|ui|ux|user interface|front[- ]?end|components?|screens?|layout|redesign|design system|stylesheet|css|tailwind|typography|colou?r|navbar|sidebar|dashboard|swiftui|figma)\b|\b(build|create|make|design|prototype|style|implement|polish)\b.{0,40}\b(app|page|site|screen|ui|interface|components?|layout|view|dashboard|form|button|modal)\b/i;

const IOS_INTENT = /\b(swiftui|swift|ios|iphone|ipad|sf ?symbols|app ?store)\b/i;

const DESIGN_WEB =
  "design-tokens, layout-and-composition, color-and-elevation, components-and-states, grid-and-spacing, interaction-and-motion, accessibility-and-inclusive-design, dec-* canon, make-interfaces-feel-better, hallmark (marketing/landing only)";

const DESIGN_IOS =
  "ios-typography, ios-color-and-materials, ios-layout-and-grid, ios-components, ios26-hig-patterns, ios-accessibility, make-interfaces-feel-better";

// ── fallback + meta-suppression ───────────────────────────────────────────────

const TASK_INTENT =
  /\b(build|create|make|write|add|implement|fix|change|update|set ?up|configure|wire|integrate|migrate|generate|scaffold|design|code)\b/i;

const META_INTENT =
  /\b(hook|matcher|the regex|settings\.json|skill router|this nudge|all skills)\b/i;

const META_CODE_VERB =
  /\b(build|create|implement|fix|debug|refactor|write|add|wire)\b/i;

export const FALLBACK: Match = {
  label: "_fallback",
  skills:
    "This looks like a build/code task. Before acting, scan the available skills and invoke any that apply via the Skill tool (process skills first: brainstorming for new work, systematic-debugging for bugs) — don't work from memory.",
};

// ── public API ────────────────────────────────────────────────────────────────

export function classify(prompt: string): Match[] {
  if (META_INTENT.test(prompt) && !META_CODE_VERB.test(prompt)) return [];

  const matched: Match[] = [];

  if (DESIGN_INTENT.test(prompt)) {
    const isIOS = IOS_INTENT.test(prompt);
    matched.push({
      label: isIOS ? "native iOS design" : "design",
      skills: isIOS ? DESIGN_IOS : DESIGN_WEB,
    });
  }

  for (const [label, pattern, skills] of BUCKETS) {
    if (pattern.test(prompt)) matched.push({ label, skills });
  }

  if (matched.length) return matched;
  if (TASK_INTENT.test(prompt)) return [FALLBACK];
  return [];
}
