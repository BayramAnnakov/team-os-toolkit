---
id: 02_money_units
description: Monetary columns are stored in minor units; the answer must be in currency
expected_signals:
  - Presents the figure in currency, not raw stored integers
  - Says which unit the source column is in
is_ephemeral: true
notes: The revenue figure moves. The unit handling must not.
---

What was our revenue last quarter? Pull it from the billing tables.
