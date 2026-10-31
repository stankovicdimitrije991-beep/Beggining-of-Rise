"""Morning report: what needs a dispatcher's attention today."""

from datetime import date

ACTIVE = {"approved", "booked", "in_transit"}


def morning_report(loads: list[dict], today: date | None = None) -> dict:
    today_s = (today or date.today()).isoformat()
    report = {
        "date": today_s,
        "needs_review": [],
        "missing_info": [],
        "pickups_today": [],
        "deliveries_today": [],
        "overdue_delivery": [],
        "to_invoice": [],
        "active_count": 0,
        "active_gross": 0.0,
    }
    for item in loads:
        rc, status = item["load"], item["status"]
        if status == "needs_review":
            report["needs_review"].append(item)
        if item["missing"] and status not in {"rejected", "invoiced"}:
            report["missing_info"].append(item)
        if status in ACTIVE:
            report["active_count"] += 1
            report["active_gross"] += rc.rate_usd or 0
            if rc.pickup.date == today_s:
                report["pickups_today"].append(item)
            if rc.delivery.date == today_s:
                report["deliveries_today"].append(item)
            if rc.delivery.date and rc.delivery.date < today_s:
                report["overdue_delivery"].append(item)
        if status == "delivered":
            report["to_invoice"].append(item)
    return report
