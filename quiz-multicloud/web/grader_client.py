"""Talks to the AWS grader (API Gateway -> Lambda), or grades in-process when GRADER_URL is unset."""
import os
import sys

import requests
from flask import current_app, url_for

_GRADER_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "grader")


def _local_dir():
    return current_app.config["LOCAL_CERT_DIR"] or os.path.join(current_app.instance_path, "certificates")


def _call_remote(payload):
    resp = requests.post(
        current_app.config["GRADER_URL"],
        json=payload,
        headers={"x-grader-secret": current_app.config["GRADER_SECRET"]},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def is_local():
    return not current_app.config["GRADER_URL"]


def grade_submission(payload):
    if not is_local():
        return _call_remote({**payload, "action": "grade"})

    if _GRADER_DIR not in sys.path:
        sys.path.insert(0, _GRADER_DIR)
    from service import process_submission

    def store(key, pdf):
        path = os.path.join(_local_dir(), key)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(pdf)

    result = process_submission(payload, store)
    result["certificate_url"] = certificate_url(result["certificate_key"])
    return result


def certificate_url(key):
    """Presigned S3 URL (fresh each call, since they expire) or a local download route."""
    if is_local():
        return url_for("local_certificate", key=key)
    return _call_remote({"action": "presign", "certificate_key": key})["certificate_url"]


def local_certificate_path(key):
    base = os.path.realpath(_local_dir())
    path = os.path.realpath(os.path.join(base, key))
    if not path.startswith(base + os.sep):
        raise ValueError("invalid key")
    return path
