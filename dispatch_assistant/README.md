# Dispatch Operations Assistant (demo v0.1)

Upload a rate confirmation PDF → AI pulls out the load details → you review, fix and approve → loads are searchable, and a morning report shows what needs attention.

**What it does**
- Extracts broker, load #, rate, pickup and delivery (company, city, state, date, time window), equipment, weight, commodity, references and instructions
- Flags missing required fields and **blocks approval** until you fill them in
- Search and filter loads by status: needs_review → approved → booked → in_transit → delivered → invoiced (or rejected)
- Morning report: overdue deliveries, today's pickups and deliveries, loads waiting for review, missing info, loads ready to invoice
- Error log of failed uploads

**What it deliberately does not do:** send anything to brokers or drivers, accept loads, or negotiate. Every decision stays with you.

## Run it on your computer

You need Python 3.10 or newer (on Windows, tick "Add Python to PATH" when installing).

```bash
git clone <this repo> && cd Beggining-of-Rise
python -m venv .venv
# Windows:  .venv\Scripts\activate      Mac/Linux:  source .venv/bin/activate
pip install -r requirements.txt
python -m dispatch_assistant.samples.make_samples   # creates 2 fake rate cons
uvicorn dispatch_assistant.app:app --reload
```

Open http://localhost:8000 and upload `dispatch_assistant/samples/ratecon_complete.pdf`.

### Demo mode vs. real AI

- **Without an API key** the app runs in **demo mode** (header shows `extractor: demo`). It only reads the sample PDFs. Use it to test the screens.
- **With Claude:** create an API key at https://platform.claude.com and add a few dollars of credit, then start the app with the key set:

  ```bash
  # Windows (PowerShell):  $env:ANTHROPIC_API_KEY="sk-ant-..."
  # Mac/Linux:             export ANTHROPIC_API_KEY="sk-ant-..."
  uvicorn dispatch_assistant.app:app --reload
  ```

  The header now shows `extractor: claude`, and any real-looking rate con PDF will work. The default model is `claude-opus-5-5`; set `DISPATCH_MODEL` to change it. Expect a few cents per document.

**Data rule:** test only with the synthetic samples or documents you are authorized to use. Never upload your employer's rate cons, broker details or customer data.

## Tests

```bash
python -m pytest -q dispatch_assistant
```

## Files

| File | What it is |
|---|---|
| `app.py` | Web app (FastAPI): pages, upload, review, approval gate |
| `extractor.py` | Claude PDF extraction (structured JSON output) plus the demo fallback |
| `models.py` | Load fields, required-field rules, JSON schema |
| `db.py` | SQLite storage (`dispatch.db`) and error log |
| `report.py` | Morning report logic |
| `samples/make_samples.py` | Generates fake rate cons for testing |
