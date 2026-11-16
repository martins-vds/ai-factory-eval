def calculate_late_fee(due_on, returned_on, today):
    days_late = max(0, ((returned_on or today) - due_on).days)
    amount_cents = min(days_late * 25 if days_late > 2 else 0, 1000)
    return days_late, amount_cents
