"""Generate synthetic rate confirmation PDFs for testing.

All brokers, companies, addresses and numbers here are made up. Never use
real employer or client documents for testing.

Run:  python -m dispatch_assistant.samples.make_samples
"""

from datetime import date, timedelta
from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

OUT = Path(__file__).parent

today = date.today()

SAMPLES = {
    "ratecon_complete.pdf": {
        "Broker": "Summit Peak Logistics (FICTIONAL)",
        "Broker MC": "MC-000001",
        "Broker Email": "loads@summitpeak.example",
        "Load Number": "SPL-48213",
        "Total Carrier Pay": "$2,450.00",
        "Pickup Company": "Valley Fresh Produce Co",
        "Pickup Address": "100 Example Rd",
        "Pickup City": "Fresno, CA",
        "Pickup Date": today.isoformat(),
        "Pickup Time": "06:00-12:00",
        "Delivery Company": "Desert Grocers DC",
        "Delivery Address": "200 Sample Ave",
        "Delivery City": "Phoenix, AZ",
        "Delivery Date": (today + timedelta(days=1)).isoformat(),
        "Delivery Time": "FCFS 08:00-16:00",
        "Equipment": "53' Reefer, 34F continuous",
        "Weight": "38,500 lbs",
        "Commodity": "Fresh produce",
        "References": "PO: 77120; PU#: VF-5521; DEL#: DG-9930",
        "Instructions": "Macropoint tracking required. Detention $50/hr after 2 hrs.",
    },
    "ratecon_missing_info.pdf": {
        "Broker": "Northbound Freight Partners (FICTIONAL)",
        "Load Number": "NFP-1170",
        "Pickup Company": "Cascade Lumber Yard",
        "Pickup City": "Eugene, OR",
        "Pickup Date": (today + timedelta(days=2)).isoformat(),
        "Delivery City": "Boise, ID",
        "Equipment": "48' Flatbed",
        "Commodity": "Lumber",
        "Instructions": "Tarps required. Rate to be confirmed by phone.",
    },
}


def make_pdf(path: Path, fields: dict) -> None:
    c = canvas.Canvas(str(path), pagesize=letter)
    y = 740
    c.setFont("Helvetica-Bold", 16)
    c.drawString(60, y, "RATE CONFIRMATION - SAMPLE / NOT A REAL LOAD")
    c.setFont("Helvetica", 11)
    y -= 36
    for label, value in fields.items():
        c.drawString(60, y, f"{label}: {value}")
        y -= 20
    c.save()


def main() -> None:
    for name, fields in SAMPLES.items():
        make_pdf(OUT / name, fields)
        print(f"wrote {OUT / name}")


if __name__ == "__main__":
    main()
