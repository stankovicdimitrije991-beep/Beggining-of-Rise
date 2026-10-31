"""Data shapes for a load extracted from a rate confirmation."""

from pydantic import BaseModel


class Stop(BaseModel):
    company: str | None
    address: str | None
    city: str | None
    state: str | None
    date: str | None  # YYYY-MM-DD
    time_window: str | None  # e.g. "08:00-14:00" or "FCFS"


class RateCon(BaseModel):
    broker_name: str | None
    broker_mc: str | None
    broker_contact_email: str | None
    load_number: str | None
    rate_usd: float | None
    pickup: Stop
    delivery: Stop
    equipment: str | None
    weight_lbs: float | None
    commodity: str | None
    reference_numbers: list[str]
    special_instructions: str | None


# Fields a dispatcher must have before a load can be approved.
REQUIRED_FIELDS = [
    "broker_name",
    "load_number",
    "rate_usd",
    "pickup.city",
    "pickup.state",
    "pickup.date",
    "delivery.city",
    "delivery.state",
    "delivery.date",
]


def missing_fields(rc: RateCon) -> list[str]:
    data = rc.model_dump()
    missing = []
    for path in REQUIRED_FIELDS:
        value = data
        for key in path.split("."):
            value = value.get(key) if isinstance(value, dict) else None
        if value in (None, ""):
            missing.append(path)
    return missing


def _nullable(type_name: str) -> dict:
    return {"anyOf": [{"type": type_name}, {"type": "null"}]}


_STOP_SCHEMA = {
    "type": "object",
    "properties": {
        "company": _nullable("string"),
        "address": _nullable("string"),
        "city": _nullable("string"),
        "state": _nullable("string"),
        "date": _nullable("string"),
        "time_window": _nullable("string"),
    },
    "required": ["company", "address", "city", "state", "date", "time_window"],
    "additionalProperties": False,
}

# JSON schema sent to Claude's structured outputs. Every field is required but
# nullable, so the model returns null instead of guessing a missing value.
RATECON_SCHEMA = {
    "type": "object",
    "properties": {
        "broker_name": _nullable("string"),
        "broker_mc": _nullable("string"),
        "broker_contact_email": _nullable("string"),
        "load_number": _nullable("string"),
        "rate_usd": _nullable("number"),
        "pickup": _STOP_SCHEMA,
        "delivery": _STOP_SCHEMA,
        "equipment": _nullable("string"),
        "weight_lbs": _nullable("number"),
        "commodity": _nullable("string"),
        "reference_numbers": {"type": "array", "items": {"type": "string"}},
        "special_instructions": _nullable("string"),
    },
    "required": [
        "broker_name",
        "broker_mc",
        "broker_contact_email",
        "load_number",
        "rate_usd",
        "pickup",
        "delivery",
        "equipment",
        "weight_lbs",
        "commodity",
        "reference_numbers",
        "special_instructions",
    ],
    "additionalProperties": False,
}
