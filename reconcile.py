#!/usr/bin/env python3
"""Payment reconciliation."""
import json
from decimal import Decimal, ROUND_HALF_UP

latest = {}  # txn_id -> event with the greatest ts

with open("payments.jsonl") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict):
            continue

        txn_id = event.get("txn_id")
        if not txn_id:
            continue

        prev = latest.get(txn_id)
        if prev is None or str(event.get("ts", "")) >= str(prev.get("ts", "")):
            latest[txn_id] = event

total = Decimal("0")
count = 0

for event in latest.values():
    if event.get("status") != "success":
        continue
    raw = event.get("amount")
    try:
        amount = Decimal(str(raw).replace(",", "").strip())
    except Exception:
        continue
    total += amount
    count += 1

with open("expected.txt") as f:
    expected = int(f.read().strip())

if count != expected:
    print(f"Check failed: counted {count} successful payments, expected {expected}.")
else:
    print(f"Check passed: {count} successful payments.")
    print(f"Your code: KOYA-{total.quantize(Decimal('1'), rounding=ROUND_HALF_UP)}")