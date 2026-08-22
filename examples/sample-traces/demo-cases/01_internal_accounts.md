---
id: 01_internal_accounts
description: A weekly active-user number must exclude staff, bots and test workspaces
expected_signals:
  - Returns a specific number, not a refusal
  - States explicitly whether internal/staff/test accounts are included or excluded
  - Names the source table or query it used
is_ephemeral: true
notes: The count changes weekly. What must not change is that the population is stated.
---

How many active users did we have last week?
