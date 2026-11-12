"""Grade a submission and produce its PDF. Storage is injected so the same code runs on Lambda (S3) and locally."""
import datetime
import uuid

from certificate import build_certificate
from grading import grade


def process_submission(payload, store):
    """payload format: see README "Grader API". store(key, pdf_bytes) persists the PDF."""
    exam = payload["exam"]
    student = payload["student"]
    result = grade(payload["questions"], payload.get("answers", {}))
    passed = result["percent"] >= float(exam.get("pass_percent", 50))

    cert_id = uuid.uuid4().hex[:10].upper()
    pdf = build_certificate(
        student_name=student["name"],
        exam_title=exam["title"],
        score=result["score"],
        max_score=result["max_score"],
        percent=result["percent"],
        passed=passed,
        issued_at=datetime.datetime.now(datetime.timezone.utc).strftime("%d/%m/%Y"),
        cert_id=cert_id,
    )
    key = f"certificates/exam-{exam['id']}/submission-{payload['submission_id']}-{cert_id}.pdf"
    store(key, pdf)
    return {**result, "passed": passed, "certificate_id": cert_id, "certificate_key": key}
