"""Turn a rate confirmation PDF into a structured RateCon.

ClaudeExtractor reads the PDF with Claude. DemoExtractor is a simple
pattern-matching fallback so the app can be tried without an API key; it only
understands the synthetic sample PDFs in samples/.
"""

import base64
import io
import json
import os
import re

import anthropic
from pypdf import PdfReader

from .models import RATECON_SCHEMA, RateCon, Stop

MODEL = os.environ.get("DISPATCH_MODEL", "claude-opus-5-5")

PROMPT = """You are extracting data from a US trucking rate confirmation for a dispatcher.

Fill every field from the document. Rules:
- Use null when a value is not in the document. Never guess or invent values.
- rate_usd is the total carrier pay (linehaul plus accessorials listed as carrier pay), as a number.
- Dates as YYYY-MM-DD. States as 2-letter codes.
- reference_numbers: PO, BOL, pickup and delivery numbers, each as "TYPE: value".
- special_instructions: a short summary of requirements (tracking, PPE, detention, lumper, etc.)."""


class ExtractionError(Exception):
    pass


class ClaudeExtractor:
    name = "claude"

    def __init__(self, client: anthropic.Anthropic | None = None):
        self.client = client or anthropic.Anthropic()

    def extract(self, pdf_bytes: bytes) -> RateCon:
        pdf_b64 = base64.standard_b64encode(pdf_bytes).decode()
        try:
            response = self.client.beta.messages.create(
                model=MODEL,
                max_tokens=16000,
                betas=["server-side-fallback-2026-07-01"],
                fallbacks="default",
                output_config={
                    "effort": "low",
                    "format": {"type": "json_schema", "schema": RATECON_SCHEMA},
                },
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "document",
                                "source": {
                                    "type": "base64",
                                    "media_type": "application/pdf",
                                    "data": pdf_b64,
                                },
                            },
                            {"type": "text", "text": PROMPT},
                        ],
                    }
                ],
            )
        except anthropic.AuthenticationError as e:
            raise ExtractionError("Invalid ANTHROPIC_API_KEY.") from e
        except anthropic.BadRequestError as e:
            raise ExtractionError(f"Claude rejected the request: {e.message}") from e
        except anthropic.RateLimitError as e:
            raise ExtractionError("Rate limited by the API, try again shortly.") from e
        except anthropic.APIStatusError as e:
            raise ExtractionError(f"API error {e.status_code}: {e.message}") from e
        except anthropic.APIConnectionError as e:
            raise ExtractionError("Could not reach the Claude API.") from e

        if response.stop_reason == "refusal":
            raise ExtractionError("Claude declined to process this document.")
        if response.stop_reason == "max_tokens":
            raise ExtractionError("Response was cut off; try again.")

        text = "".join(b.text for b in response.content if b.type == "text")
        try:
            return RateCon.model_validate(json.loads(text))
        except (json.JSONDecodeError, ValueError) as e:
            raise ExtractionError(f"Could not parse extraction: {e}") from e


class DemoExtractor:
    """Regex extraction for the synthetic sample PDFs only."""

    name = "demo"

    def extract(self, pdf_bytes: bytes) -> RateCon:
        try:
            reader = PdfReader(io.BytesIO(pdf_bytes))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception as e:
            raise ExtractionError(f"Could not read PDF: {e}") from e

        def field(label: str) -> str | None:
            m = re.search(rf"^{re.escape(label)}:\s*(.+)$", text, re.MULTILINE)
            return m.group(1).strip() if m else None

        def number(label: str) -> float | None:
            raw = field(label)
            if raw is None:
                return None
            digits = re.sub(r"[^0-9.]", "", raw)
            return float(digits) if digits else None

        def stop(prefix: str) -> Stop:
            city_state = field(f"{prefix} City") or ""
            city, _, state = city_state.partition(",")
            return Stop(
                company=field(f"{prefix} Company"),
                address=field(f"{prefix} Address"),
                city=city.strip() or None,
                state=state.strip() or None,
                date=field(f"{prefix} Date"),
                time_window=field(f"{prefix} Time"),
            )

        refs = field("References")
        return RateCon(
            broker_name=field("Broker"),
            broker_mc=field("Broker MC"),
            broker_contact_email=field("Broker Email"),
            load_number=field("Load Number"),
            rate_usd=number("Total Carrier Pay"),
            pickup=stop("Pickup"),
            delivery=stop("Delivery"),
            equipment=field("Equipment"),
            weight_lbs=number("Weight"),
            commodity=field("Commodity"),
            reference_numbers=[r.strip() for r in refs.split(";")] if refs else [],
            special_instructions=field("Instructions"),
        )


def default_extractor():
    if os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN"):
        return ClaudeExtractor()
    return DemoExtractor()
