import json

import pytest

import handler
from certificate import build_certificate
from grading import grade

QUESTIONS = [
    {"id": 1, "points": 1, "correct": [1]},
    {"id": 2, "points": 2, "correct": [0, 2]},
    {"id": 3, "points": 1, "correct": [3]},
]


def test_grade_mixed():
    r = grade(QUESTIONS, {"1": [1], "2": [2, 0], "3": [0]})
    assert r["score"] == 3 and r["max_score"] == 4 and r["percent"] == 75.0
    assert [d["is_correct"] for d in r["details"]] == [True, True, False]


def test_partial_multi_answer_scores_zero_and_missing_answers_ok():
    r = grade(QUESTIONS, {"2": [0]})
    assert r["score"] == 0 and r["percent"] == 0.0


def test_empty_exam():
    assert grade([], {})["percent"] == 0.0


def test_certificate_is_pdf_with_unicode():
    pdf = build_certificate(student_name="Nguyễn Văn Ánh", exam_title="Điện toán đám mây", score=3, max_score=4,
                            percent=75, passed=True, issued_at="11/11/2026", cert_id="ABC")
    assert pdf.startswith(b"%PDF") and len(pdf) > 1000


class FakeS3:
    def __init__(self):
        self.objects = {}

    def put_object(self, Bucket, Key, Body, ContentType):
        self.objects[Key] = Body

    def generate_presigned_url(self, op, Params, ExpiresIn):
        return f"https://{Params['Bucket']}.s3.amazonaws.com/{Params['Key']}?X-Amz-Expires={ExpiresIn}"


class FakeSES:
    def __init__(self):
        self.sent = []

    def send_email(self, **kw):
        self.sent.append(kw)


@pytest.fixture
def aws(monkeypatch):
    s3, ses = FakeS3(), FakeSES()
    monkeypatch.setattr(handler, "_clients", {"s3": s3, "ses": ses})
    monkeypatch.setenv("GRADER_SECRET", "s3cret")
    monkeypatch.setenv("CERT_BUCKET", "quiz-certs")
    monkeypatch.setenv("SES_SENDER", "noreply@example.com")
    return s3, ses


def _event(body, secret="s3cret"):
    return {"headers": {"X-Grader-Secret": secret}, "body": json.dumps(body)}


PAYLOAD = {
    "submission_id": 7,
    "student": {"name": "Lê Thị B", "email": "b@example.com"},
    "exam": {"id": 3, "title": "Thi thử", "pass_percent": 50},
    "questions": QUESTIONS,
    "answers": {"1": [1], "2": [0, 2]},
}


def test_handler_rejects_bad_secret(aws):
    assert handler.lambda_handler(_event(PAYLOAD, secret="nope"), None)["statusCode"] == 401


def test_handler_grades_stores_pdf_and_emails(aws):
    s3, ses = aws
    resp = handler.lambda_handler(_event(PAYLOAD), None)
    assert resp["statusCode"] == 200
    body = json.loads(resp["body"])
    assert body["score"] == 3 and body["passed"] is True
    assert body["certificate_key"] in s3.objects and s3.objects[body["certificate_key"]].startswith(b"%PDF")
    assert body["certificate_url"].startswith("https://quiz-certs.s3.amazonaws.com/certificates/exam-3/submission-7-")
    assert ses.sent[0]["Destination"]["ToAddresses"] == ["b@example.com"]


def test_handler_presign_validates_key(aws):
    ok = handler.lambda_handler(_event({"action": "presign", "certificate_key": "certificates/x.pdf"}), None)
    assert ok["statusCode"] == 200
    bad = handler.lambda_handler(_event({"action": "presign", "certificate_key": "../secret"}), None)
    assert bad["statusCode"] == 400


def test_handler_bad_payload(aws):
    assert handler.lambda_handler(_event({"action": "grade"}), None)["statusCode"] == 400
