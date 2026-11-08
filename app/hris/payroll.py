"""Payroll rules used to build demo payslips (Vietnamese social insurance + progressive PIT).
Demo assumptions: in production C&B configures these from current regulations."""
from __future__ import annotations

from datetime import date, timedelta

# Giả định cho dữ liệu mẫu. Khi triển khai thật, C&B cấu hình theo quy định hiện hành.
INSURANCE_CAP = 46_800_000
SI_RATE, HI_RATE, UI_RATE = 0.08, 0.015, 0.01
PERSONAL_DEDUCTION, DEPENDANT_DEDUCTION = 15_500_000, 6_200_000
PIT_BRACKETS = [(5e6, .05), (10e6, .10), (18e6, .15), (32e6, .20), (52e6, .25), (80e6, .30), (float("inf"), .35)]


def compute_pit(taxable: float) -> int:
    tax, lower = 0.0, 0.0
    for upper, rate in PIT_BRACKETS:
        if taxable <= lower:
            break
        tax += (min(taxable, upper) - lower) * rate
        lower = upper
    return int(round(tax, -3))


def build_payslip(base: int, allowance: int, overtime: int, bonus: int, dependants: int) -> dict:
    gross = base + allowance + overtime + bonus
    ins_base = min(base, INSURANCE_CAP)
    si, hi, ui = int(ins_base * SI_RATE), int(ins_base * HI_RATE), int(ins_base * UI_RATE)
    taxable = max(0, gross - si - hi - ui - PERSONAL_DEDUCTION - dependants * DEPENDANT_DEDUCTION)
    pit = compute_pit(taxable)
    return {"base": base, "allowance": allowance, "overtime": overtime, "bonus": bonus, "gross": gross,
            "social_insurance": si, "health_insurance": hi, "unemployment_insurance": ui, "pit": pit,
            "net": gross - si - hi - ui - pit}


def workdays(start: date, end: date) -> int:
    n, d = 0, start
    while d <= end:
        n += d.weekday() < 5
        d += timedelta(days=1)
    return n
