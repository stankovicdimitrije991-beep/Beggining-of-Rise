"""Dispatch Operations Assistant: upload rate cons, review, approve, report.

Run:  uvicorn dispatch_assistant.app:app --reload
"""

import os
from pathlib import Path
from urllib.parse import quote

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from .db import STATUSES, Store
from .extractor import ExtractionError, default_extractor
from .models import RateCon, missing_fields
from .report import morning_report

MAX_UPLOAD_BYTES = 20 * 1024 * 1024
TEXT_FIELDS = [
    "broker_name", "broker_mc", "broker_contact_email", "load_number",
    "equipment", "commodity", "special_instructions",
]
NUMBER_FIELDS = ["rate_usd", "weight_lbs"]
STOP_FIELDS = ["company", "address", "city", "state", "date", "time_window"]

templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


def create_app(db_path: str | None = None, extractor=None) -> FastAPI:
    app = FastAPI(title="Dispatch Operations Assistant")
    store = Store(db_path or os.environ.get("DISPATCH_DB", "dispatch.db"))
    app.state.store = store
    app.state.extractor = extractor or default_extractor()

    def page(request: Request, name: str, **ctx) -> HTMLResponse:
        ctx["extractor_name"] = app.state.extractor.name
        return templates.TemplateResponse(request, name, ctx)

    def load_or_404(load_id: int) -> dict:
        item = store.get_load(load_id)
        if item is None:
            raise HTTPException(404, "Load not found")
        return item

    @app.get("/", response_class=HTMLResponse)
    def index(request: Request, q: str = "", status: str = "", error: str = ""):
        return page(
            request, "index.html",
            loads=store.list_loads(q, status), q=q, status=status,
            statuses=STATUSES, error=error,
        )

    @app.post("/upload")
    async def upload(file: UploadFile = File(...)):
        name = file.filename or "upload.pdf"
        data = await file.read(MAX_UPLOAD_BYTES + 1)
        if len(data) > MAX_UPLOAD_BYTES:
            msg = "File is larger than 20 MB."
        elif not data.startswith(b"%PDF"):
            msg = "Only PDF files are supported."
        else:
            try:
                rc = app.state.extractor.extract(data)
            except ExtractionError as e:
                msg = str(e)
            else:
                load_id = store.add_load(rc, missing_fields(rc), name, app.state.extractor.name)
                return RedirectResponse(f"/loads/{load_id}", status_code=303)
        store.log_error(name, msg)
        return RedirectResponse(f"/?error={quote(msg)}", status_code=303)

    @app.get("/loads/{load_id}", response_class=HTMLResponse)
    def load_detail(request: Request, load_id: int, error: str = ""):
        return page(
            request, "load.html", item=load_or_404(load_id), statuses=STATUSES,
            text_fields=TEXT_FIELDS, number_fields=NUMBER_FIELDS,
            stop_fields=STOP_FIELDS, error=error,
        )

    @app.post("/loads/{load_id}")
    async def save_load(request: Request, load_id: int):
        load_or_404(load_id)
        form = await request.form()

        def text(key: str) -> str | None:
            value = str(form.get(key, "")).strip()
            return value or None

        def number(key: str) -> float | None:
            value = text(key)
            if value is None:
                return None
            try:
                return float(value.replace(",", "").replace("$", ""))
            except ValueError:
                return None

        rc = RateCon(
            **{f: text(f) for f in TEXT_FIELDS},
            **{f: number(f) for f in NUMBER_FIELDS},
            pickup={f: text(f"pickup.{f}") for f in STOP_FIELDS},
            delivery={f: text(f"delivery.{f}") for f in STOP_FIELDS},
            reference_numbers=[
                r.strip() for r in str(form.get("reference_numbers", "")).splitlines() if r.strip()
            ],
        )
        store.update_load(load_id, rc, missing_fields(rc), str(form.get("notes", "")))
        return RedirectResponse(f"/loads/{load_id}", status_code=303)

    @app.post("/loads/{load_id}/status")
    def change_status(load_id: int, status: str = Form(...)):
        item = load_or_404(load_id)
        if status not in STATUSES:
            raise HTTPException(400, "Unknown status")
        # Human approval gate: a load with missing required info can't move forward.
        if status not in {"needs_review", "rejected"} and item["missing"]:
            missing = ", ".join(item["missing"])
            return RedirectResponse(
                f"/loads/{load_id}?error=" + quote(f"Fill in the missing fields first: {missing}"), status_code=303
            )
        store.set_status(load_id, status)
        return RedirectResponse(f"/loads/{load_id}", status_code=303)

    @app.get("/report", response_class=HTMLResponse)
    def report(request: Request):
        return page(request, "report.html", r=morning_report(store.list_loads()))

    @app.get("/errors", response_class=HTMLResponse)
    def errors(request: Request):
        return page(request, "errors.html", errors=store.list_errors())

    return app


app = create_app()
