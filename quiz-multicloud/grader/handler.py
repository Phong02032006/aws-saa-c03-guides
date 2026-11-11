"""AWS Lambda entry point (handler: handler.lambda_handler). Works behind API Gateway (proxy) or a Function URL."""
import base64
import hmac
import json
import logging
import os

from service import process_submission

log = logging.getLogger()
log.setLevel(logging.INFO)

_clients = {}


def _client(name):
    if name not in _clients:
        import boto3
        from botocore.config import Config

        _clients[name] = boto3.client(name, config=Config(signature_version="s3v4"))
    return _clients[name]


def _response(status, body):
    return {"statusCode": status, "headers": {"Content-Type": "application/json"}, "body": json.dumps(body)}


def _presign(key):
    return _client("s3").generate_presigned_url(
        "get_object",
        Params={"Bucket": os.environ["CERT_BUCKET"], "Key": key, "ResponseContentType": "application/pdf"},
        ExpiresIn=int(os.environ.get("PRESIGN_TTL_SECONDS", "3600")),
    )


def _send_email(to, student_name, exam_title, result, url):
    sender = os.environ.get("SES_SENDER")
    if not sender or not to:
        return
    status = "ĐẠT" if result["passed"] else "CHƯA ĐẠT"
    text = (
        f"Chào {student_name},\n\nKết quả bài thi \"{exam_title}\": "
        f"{result['score']:g}/{result['max_score']:g} ({result['percent']:g}%) - {status}.\n"
        f"Tải file PDF (link hết hạn sau 1 giờ): {url}\n"
    )
    try:
        _client("ses").send_email(
            Source=sender,
            Destination={"ToAddresses": [to]},
            Message={"Subject": {"Data": f"Kết quả bài thi: {exam_title}", "Charset": "UTF-8"},
                     "Body": {"Text": {"Data": text, "Charset": "UTF-8"}}},
        )
    except Exception:  # email is best-effort; grading result must still be returned
        log.exception("SES send_email failed")


def lambda_handler(event, context):
    headers = {k.lower(): v for k, v in (event.get("headers") or {}).items()}
    secret = os.environ.get("GRADER_SECRET", "")
    if not secret or not hmac.compare_digest(headers.get("x-grader-secret", ""), secret):
        return _response(401, {"error": "unauthorized"})

    body = event.get("body") or "{}"
    if event.get("isBase64Encoded"):
        body = base64.b64decode(body).decode("utf-8")
    try:
        payload = json.loads(body)
    except ValueError:
        return _response(400, {"error": "invalid JSON"})

    action = payload.get("action", "grade")
    if action == "presign":
        key = payload.get("certificate_key", "")
        if not key.startswith("certificates/"):
            return _response(400, {"error": "invalid key"})
        return _response(200, {"certificate_url": _presign(key)})

    if action != "grade":
        return _response(400, {"error": f"unknown action {action}"})

    def store(key, pdf):
        _client("s3").put_object(Bucket=os.environ["CERT_BUCKET"], Key=key, Body=pdf, ContentType="application/pdf")

    try:
        result = process_submission(payload, store)
    except (KeyError, TypeError, ValueError) as exc:
        return _response(400, {"error": f"bad payload: {exc}"})

    result["certificate_url"] = _presign(result["certificate_key"])
    student = payload["student"]
    _send_email(student.get("email"), student["name"], payload["exam"]["title"], result, result["certificate_url"])
    log.info("graded submission %s: %s/%s", payload.get("submission_id"), result["score"], result["max_score"])
    return _response(200, result)
