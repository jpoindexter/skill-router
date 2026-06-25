#!/usr/bin/env python3
"""Pure intent classifier — no I/O, no agent-specific formats.

Call classify(prompt) -> list of (label, skill_hint_string).
Empty list means no task signal detected (pure conversation).
Each agent adapter imports this and wraps output in its own format.

Extend by adding rows to BUCKETS or editing the regex constants below.
"""
import re

# ── helpers ──────────────────────────────────────────────────────────────────

def hit(pattern: str, text: str) -> bool:
    return bool(re.search(pattern, text, re.IGNORECASE))


# ── intent buckets ────────────────────────────────────────────────────────────
# Each entry: (label, intent_regex, comma-separated skill hints)
# Order matters for display; multiple buckets can match.

BUCKETS = [
    ("debugging",
     r"\b(bug|debug|error|exception|stack ?trace|traceback|crash|broken|failing|fails?|"
     r"isn.?t working|not working|regression|race condition|flaky)\b",
     "superpowers:systematic-debugging (first), debug, root-cause-tracing"),

    ("feature work",
     r"\b(new feature|add (a |the )?feature|feature for|let.?s build|build (a|the|me|out)\b|"
     r"greenfield)\b",
     "superpowers:brainstorming (first), feature-development, superpowers:test-driven-development"),

    ("testing",
     r"\b(unit tests?|write tests?|add tests?|test coverage|coverage|vitest|jest|test suite|"
     r"failing tests?)\b",
     "superpowers:test-driven-development, test-master, qa"),

    ("ship / review",
     r"\b(ship|merge|deploy|release|publish|pull request|pre-?flight|ready to ship|"
     r"open a pr)\b|\bpr\b",
     "ship-preflight, review, security-review, superpowers:verification-before-completion"),

    ("security",
     r"\b(security|secure|auth(entication|orization)?|vulnerab|cve|xss|csrf|sql ?injection|"
     r"secret|owasp|sanitiz)\b",
     "security-check, security-scan, security-reviewer"),

    ("performance",
     r"\b(performance|slow|optimi[sz]e|latency|bundle size|memory leak|n\+1|profil|janky)\b",
     "performance-optimization, dec-web-performance"),

    ("refactor / cleanup",
     r"\b(refactor|clean ?up|simplify|tidy|dead code|code smell|tech debt)\b",
     "refactor-clean, enforcing-code-size, code-simplifier"),
]

# ── design intent (split web vs native iOS) ───────────────────────────────────

_DESIGN_INTENT = (
    r"\b(websites?|web ?app|webpage|web page|landing page|home ?page|ui|ux|user interface|"
    r"front[- ]?end|components?|screens?|layout|redesign|design system|stylesheet|css|tailwind|"
    r"typography|colou?r|navbar|sidebar|dashboard|swiftui|figma)\b"
    r"|\b(build|create|make|design|prototype|style|implement|polish)\b.{0,40}"
    r"\b(app|page|site|screen|ui|interface|components?|layout|view|dashboard|form|button|modal)\b"
)
_IOS_INTENT = r"\b(swiftui|swift|ios|iphone|ipad|sf ?symbols|app ?store)\b"

_DESIGN_WEB = (
    "design-tokens, layout-and-composition, color-and-elevation, components-and-states, "
    "grid-and-spacing, interaction-and-motion, accessibility-and-inclusive-design, "
    "dec-* canon, make-interfaces-feel-better, hallmark (marketing/landing only)"
)
_DESIGN_IOS = (
    "ios-typography, ios-color-and-materials, ios-layout-and-grid, ios-components, "
    "ios26-hig-patterns, ios-accessibility, make-interfaces-feel-better"
)

# ── broad task fallback ───────────────────────────────────────────────────────

_TASK_INTENT = (
    r"\b(build|create|make|write|add|implement|fix|change|update|set ?up|configure|"
    r"wire|integrate|migrate|generate|scaffold|design|code)\b"
)

# ── meta-conversation suppression ─────────────────────────────────────────────
# Suppress when user is talking ABOUT the router/hook itself (not doing work).

_META_INTENT    = r"\b(hook|matcher|the regex|settings\.json|skill router|this nudge|all skills)\b"
_META_CODE_VERB = r"\b(build|create|implement|fix|debug|refactor|write|add|wire)\b"


# ── public API ────────────────────────────────────────────────────────────────

FALLBACK_HINT = (
    "This looks like a build/code task. Before acting, scan the available skills and invoke any "
    "that apply via the Skill tool (process skills first: brainstorming for new work, "
    "systematic-debugging for bugs) — don't work from memory."
)


def classify(prompt: str) -> list[tuple[str, str]]:
    """Return list of (label, skill_hints) for the prompt.

    Returns [] for pure conversation (no nudge needed).
    Returns [("_fallback", FALLBACK_HINT)] when a task signal is detected
    but no specific bucket matches.
    """
    if hit(_META_INTENT, prompt) and not hit(_META_CODE_VERB, prompt):
        return []

    matched = []

    if hit(_DESIGN_INTENT, prompt):
        is_ios = hit(_IOS_INTENT, prompt)
        label  = "native iOS design" if is_ios else "design"
        skills = _DESIGN_IOS if is_ios else _DESIGN_WEB
        matched.append((label, skills))

    for label, pat, skills in BUCKETS:
        if hit(pat, prompt):
            matched.append((label, skills))

    if matched:
        return matched

    if hit(_TASK_INTENT, prompt):
        return [("_fallback", FALLBACK_HINT)]

    return []
