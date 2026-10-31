import json
from datetime import date, timedelta
from types import SimpleNamespace

from fastapi.testclient import TestClient

from dispatch_assistant.app import create_app
from dispatch_assistant.extractor import ClaudeExtractor, DemoExtractor, ExtractionError
from dispatch_assistant.models import missing_fields
from dispatch_assistant.samples.make_samples import SAMPLES, make_pdf


def sample_bytes(tmp_path, name):
    path = tmp_path / name
    make_pdf(path, SAMPLES[name])
    return path.read_bytes()


def make_client(tmp_path, extractor=None):
    app = create_app(str(tmp_path / "test.db"), extractor or DemoExtractor())
    return TestClient(app), app.state.store


def upload(client, data, name="rc.pdf"):
    return client.post("/upload", files={"file": (name, data, "application/pdf")}, follow_redirects=False)


def test_demo_extractor_reads_complete_sample(tmp_path):
    rc = DemoExtractor().extract(sample_bytes(tmp_path, "ratecon_complete.pdf"))
    assert rc.load_number == "SPL-48213"
    assert rc.rate_usd == 2450.0
    assert (rc.pickup.city, rc.pickup.state) == ("Fresno", "CA")
    assert rc.weight_lbs == 38500.0
    assert len(rc.reference_numbers) == 3
    assert missing_fields(rc) == []


def test_missing_fields_flagged(tmp_path):
    rc = DemoExtractor().extract(sample_bytes(tmp_path, "ratecon_missing_info.pdf"))
    assert set(missing_fields(rc)) == {"rate_usd", "delivery.date"}


def test_upload_review_approve_flow(tmp_path):
    client, store = make_client(tmp_path)
    resp = upload(client, sample_bytes(tmp_path, "ratecon_missing_info.pdf"))
    assert resp.status_code == 303
    load_id = int(resp.headers["location"].rsplit("/", 1)[1])

    # Approval is blocked while required info is missing.
    resp = client.post(f"/loads/{load_id}/status", data={"status": "approved"}, follow_redirects=False)
    assert "error=" in resp.headers["location"]
    assert store.get_load(load_id)["status"] == "needs_review"

    # Dispatcher fills in the gaps, then approval works.
    item = store.get_load(load_id)
    form = {f: getattr(item["load"], f) or "" for f in ["broker_name", "load_number", "equipment", "commodity"]}
    form.update({
        "rate_usd": "$1,980",
        "pickup.city": "Eugene", "pickup.state": "OR", "pickup.date": item["load"].pickup.date,
        "delivery.city": "Boise", "delivery.state": "ID", "delivery.date": "2030-01-02",
        "reference_numbers": "PO: 1\nBOL: 2",
    })
    client.post(f"/loads/{load_id}", data=form)
    item = store.get_load(load_id)
    assert item["missing"] == []
    assert item["load"].rate_usd == 1980.0
    assert item["load"].reference_numbers == ["PO: 1", "BOL: 2"]

    client.post(f"/loads/{load_id}/status", data={"status": "approved"})
    assert store.get_load(load_id)["status"] == "approved"

    assert "Eugene" in client.get("/").text
    assert "Eugene" in client.get("/?q=NFP-1170").text
    assert "Eugene" not in client.get("/?q=nothing-matches").text


def test_non_pdf_is_rejected_and_logged(tmp_path):
    client, store = make_client(tmp_path)
    resp = upload(client, b"hello", "notes.txt")
    assert "error=" in resp.headers["location"]
    assert store.list_loads() == []
    assert store.list_errors()[0]["source_file"] == "notes.txt"
    assert "notes.txt" in client.get("/errors").text


def test_morning_report(tmp_path):
    client, store = make_client(tmp_path)
    resp = upload(client, sample_bytes(tmp_path, "ratecon_complete.pdf"))
    load_id = int(resp.headers["location"].rsplit("/", 1)[1])
    client.post(f"/loads/{load_id}/status", data={"status": "booked"})
    page = client.get("/report").text
    assert "Pickups today (1)" in page
    assert "$2,450.00 gross in progress" in page


class FakeMessages:
    def __init__(self, response):
        self.response, self.calls = response, []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return self.response


def fake_client(text, stop_reason="end_turn"):
    response = SimpleNamespace(stop_reason=stop_reason, content=[SimpleNamespace(type="text", text=text)])
    return SimpleNamespace(beta=SimpleNamespace(messages=FakeMessages(response)))


def test_claude_extractor_request_and_parse(tmp_path):
    rc = DemoExtractor().extract(sample_bytes(tmp_path, "ratecon_complete.pdf"))
    client = fake_client(rc.model_dump_json())
    result = ClaudeExtractor(client).extract(b"%PDF-1.4 fake")
    assert result == rc

    call = client.beta.messages.calls[0]
    assert call["output_config"]["format"]["type"] == "json_schema"
    assert call["fallbacks"] == "default"
    doc = call["messages"][0]["content"][0]
    assert doc["type"] == "document" and doc["source"]["media_type"] == "application/pdf"


def test_claude_extractor_refusal_and_bad_json():
    for client in (fake_client("", stop_reason="refusal"), fake_client("not json")):
        try:
            ClaudeExtractor(client).extract(b"%PDF")
        except ExtractionError:
            pass
        else:
            raise AssertionError("expected ExtractionError")


def test_schema_matches_model():
    from dispatch_assistant.models import RATECON_SCHEMA, RateCon
    assert set(RATECON_SCHEMA["required"]) == set(RateCon.model_fields)
    assert json.dumps(RATECON_SCHEMA)
