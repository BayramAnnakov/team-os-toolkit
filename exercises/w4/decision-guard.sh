#!/usr/bin/env bash
# owner: <your name> · tier: 2 · last_reviewed: 2026-08-09
#
# decision-guard — enforces ONE ratified decision from your decisions.md.
#
# Shipped enforcing D-03 of the AI-Native Product Team cohort brain:
#   "If the vendor documents a way, use the documented way.
#    Corollary: go and read the vendor's docs before inventing a mechanism."
#
# Swap RULE_ID, the TRIGGER pattern and the EXEMPT pattern for your own rule.
#
# MODE=advise  -> prints a nudge, prompt still runs (exit 0)      <- START HERE
# MODE=enforce -> blocks the prompt outright (exit 2)             <- earn this
#
# Wire it up in .claude/settings.json:
#   { "hooks": { "UserPromptSubmit": [ { "matcher": "*",
#       "hooks": [ { "type": "command", "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/decision-guard.sh" } ] } ] } }

set -uo pipefail

MODE="${DECISION_GUARD_MODE:-advise}"
RULE_ID="D-03"
RULE_TEXT="If the vendor documents a way, use the documented way."

payload=$(cat)

# The field is "prompt". Verified 2026-08-08 by dumping a real UserPromptSubmit
# payload from a live Claude Code run — the published docs said `user_input`, and
# they were wrong. Read the wrong key and this hook sees an empty string, exits 0,
# and looks EXACTLY like a hook that works. Verify the key before you trust a guard.
# Try each parser and check that it actually SUCCEEDED — testing `command -v` alone
# is not enough, because a present-but-broken jq fails exactly like a missing one.
parsed=no
if command -v jq >/dev/null 2>&1; then
  if prompt=$(printf '%s' "$payload" | jq -er '.prompt // ""' 2>/dev/null); then parsed=yes; fi
fi
if [ "$parsed" = no ] && command -v python3 >/dev/null 2>&1; then
  # A sed regex cannot parse JSON — it breaks on escaped quotes. python3 ships on
  # macOS and every mainstream Linux.
  if prompt=$(printf '%s' "$payload" | python3 -c \
      'import json,sys; print(json.load(sys.stdin).get("prompt",""))' 2>/dev/null); then parsed=yes; fi
fi

if [ "$parsed" = no ]; then
  # No working JSON parser — common on a bare Windows Git Bash box. Without this
  # branch the guard reads an empty prompt, exits 0, and looks EXACTLY like a
  # working hook: the precise failure this guard exists to teach you about.
  # Fail LOUDLY, and never block — a missing dependency must not gate your work.
  printf '%s\n' "⚠️  decision-guard: no working JSON parser (jq / python3) — THE GUARD IS NOT RUNNING." \
                "   It is not staying silent because your prompts are clean. Install jq or python3," \
                "   then re-run your must-fire test before you trust this hook again." >&2
  exit 0
fi

# An empty prompt is an ordinary case (a non-prompt event) — stay silent.
[ -z "${prompt:-}" ] && exit 0

lower=$(printf '%s' "$prompt" | tr '[:upper:]' '[:lower:]')

# TRIGGER — the shape of "I am about to invent a mechanism".
TRIGGER='symlink|workaround|work around|hack around|monkey.?patch|patch around|roll our own|write a wrapper|just wrap|костыл|обойт|свой велосипед|напиши обёртк|обертк'

# EXEMPT — evidence the person already did the thing D-03 asks for.
EXEMPT='docs|documentation|documented|vendor|changelog|release notes|reference|официальн|документац|по докам|в доке'

printf '%s' "$lower" | grep -Eq "$TRIGGER" || exit 0
printf '%s' "$lower" | grep -Eq "$EXEMPT"  && exit 0

msg="⚖️  ${RULE_ID} — ${RULE_TEXT}
   You're proposing a mechanism of our own. Before we build it:
   check whether the vendor already documents one, and say what you found.
   (Our own repo is currently carrying an open bug from skipping this — the
    symlink that reads as 9 bytes on Windows.)"

if [ "$MODE" = "enforce" ]; then
  printf '%s\n' "$msg" >&2
  exit 2          # blocks the prompt; stderr is fed back to Claude
fi

printf '%s\n' "$msg"
exit 0            # advisory: injected as context, prompt still runs
