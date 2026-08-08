# Exercises

Hands-on sheets from the AI-Native Product Team workshops. Each one is self-contained: pick a rule,
build the thing, and verify it with your own eyes rather than trusting the sheet.

| | |
|---|---|
| [`w4/exercise-1-hooks.md`](w4/exercise-1-hooks.md) | Turn a decision your team ratified into a hook that **blocks** — the `advisory → enforced` step. Ships with a worked guard. |
| [`w4/decision-guard.sh`](w4/decision-guard.sh) | A working `UserPromptSubmit` guard enforcing **D-03** (*if the vendor documents a way, use the documented way*). Swap two regexes for your own rule. |

**You pass when you have both halves:** the guard fires on something it should catch, **and** stays
silent on something it shouldn't. One without the other is theatre or a nuisance — and a nuisance
gets disabled by Thursday.

> ⚠️ **Verify the payload field name against a real payload before you trust any guard.** As of
> 2026-08-08 the field is `prompt`, while the published docs said `user_input`. Read the wrong key
> and your hook sees an empty string, exits 0 forever, and looks exactly like a hook that works.
> The sheet shows you how to dump your own.
