"""AWS Lambda entry point (handler: handler.lambda_handler).

One function, two triggers:
- API Gateway (HTTP): action "submit" queues a submission on SQS; "grade" grades synchronously; "presign" refreshes a link.
- SQS: grades queued submissions, stores the PDF on S3, reports the result to the web app and emails the student.
"""
import base64
import hmac
import json
import logging
import os
import urllib.request

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


def _store(key, pdf):
    _client("s3").put_object(Bucket=os.environ["CERT_BUCKET"], Key=key, Body=pdf, ContentType="application/pdf")


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
    except Exception:  # email is best-effort; grading result must still be delivered
        log.exception("SES send_email failed")


def _post_callback(body):
    """Report a grading result to the web app on Azure. Raises on failure so SQS retries the message."""
    req = urllib.request.Request(
        os.environ["WEB_CALLBACK_URL"],
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", "x-grader-secret": os.environ["GRADER_SECRET"]},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        if resp.status >= 300:
            raise RuntimeError(f"callback returned HTTP {resp.status}")


def _validate(payload):
    for key in ("submission_id", "student", "exam", "questions"):
        if key not in payload:
            raise KeyError(key)


def _handle_sqs(event):
    # Configure the SQS trigger with batch size 1: raising makes SQS redeliver the message,
    # and after maxReceiveCount attempts it moves to the dead-letter queue.
    for record in event["Records"]:
        payload = json.loads(record["body"])
        result = process_submission(payload, _store)
        _post_callback({"submission_id": payload["submission_id"], **result})
        student = payload["student"]
        _send_email(student.get("email"), student["name"], payload["exam"]["title"], result,
                    _presign(result["certificate_key"]))
        log.info("graded queued submission %s: %s/%s", payload["submission_id"], result["score"],
                 result["max_score"])
    return {"processed": len(event["Records"])}


def lambda_handler(event, context):
    if event.get("Records") and event["Records"][0].get("eventSource") == "aws:sqs":
        return _handle_sqs(event)

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

    if action == "submit":
        try:
            _validate(payload)
        except KeyError as exc:
            return _response(400, {"error": f"bad payload: missing {exc}"})
        msg = _client("sqs").send_message(QueueUrl=os.environ["GRADING_QUEUE_URL"], MessageBody=json.dumps(payload))
        log.info("queued submission %s as message %s", payload["submission_id"], msg["MessageId"])
        return _response(202, {"status": "queued", "message_id": msg["MessageId"]})

    if action != "grade":
        return _response(400, {"error": f"unknown action {action}"})

    try:
        result = process_submission(payload, _store)
    except (KeyError, TypeError, ValueError) as exc:
        return _response(400, {"error": f"bad payload: {exc}"})

    result["certificate_url"] = _presign(result["certificate_key"])
    student = payload["student"]
    _send_email(student.get("email"), student["name"], payload["exam"]["title"], result, result["certificate_url"])
    log.info("graded submission %s: %s/%s", payload.get("submission_id"), result["score"], result["max_score"])
    return _response(200, result)
