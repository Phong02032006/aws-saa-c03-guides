import io
import re

import pytest

from app import create_app
from models import Exam, Submission, db


@pytest.fixture
def app(tmp_path):
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path / 'test.db'}",
        "AUTH_MODE": "dev",
        "GRADER_URL": "",
        "LOCAL_CERT_DIR": str(tmp_path / "certs"),
    })
    with app.app_context():
        db.create_all()
    return app


def csrf(client, path="/login"):
    html = client.get(path).get_data(as_text=True)
    return re.search(r'name="csrf" value="([^"]+)"', html).group(1)


def login(client, name, email, role):
    r = client.post("/login", data={"csrf": csrf(client), "name": name, "email": email, "role": role})
    assert r.status_code == 302


def test_full_flow(app):
    teacher, student, other = app.test_client(), app.test_client(), app.test_client()
    login(teacher, "Cô Lan", "lan@school.edu", "teacher")
    login(student, "Nguyễn An", "an@school.edu", "student")
    login(other, "Trần Bình", "binh@school.edu", "student")

    # Students cannot reach teacher pages; requests without CSRF token are rejected.
    assert student.get("/teacher").status_code == 403
    assert teacher.post("/teacher/exams/new", data={"title": "x"}).status_code == 400

    t = csrf(teacher, "/teacher")
    r = teacher.post("/teacher/exams/new", data={"csrf": t, "title": "Kiểm tra Cloud", "duration_minutes": "10",
                                                 "pass_percent": "60"})
    exam_id = int(r.headers["Location"].rstrip("/").split("/")[-1])

    # Option C left blank: the correct index for "D" must be remapped to 2.
    teacher.post(f"/teacher/exams/{exam_id}/questions", data={
        "csrf": t, "text": "S3 là gì?", "options": ["Object storage", "VM", "", "DNS"], "correct": ["0"], "points": "1"})
    teacher.post(f"/teacher/exams/{exam_id}/questions", data={
        "csrf": t, "text": "Serverless?", "options": ["Lambda", "EC2", "", "Functions"], "correct": ["0", "3"],
        "points": "2"})
    csv_data = "question,A,B,C,D,correct,points\nEntra ID dùng để?,Danh tính,Lưu trữ,,,A,1\nlỗi,chỉ một,,,,A,1\n"
    teacher.post(f"/teacher/exams/{exam_id}/import", data={
        "csrf": t, "file": (io.BytesIO(csv_data.encode()), "q.csv")}, content_type="multipart/form-data")

    with app.app_context():
        exam = db.session.get(Exam, exam_id)
        assert [q.correct for q in exam.questions] == [[0], [0, 2], [0]]
        assert exam.questions[1].options == ["Lambda", "EC2", "Functions"]
        qids = [q.id for q in exam.questions]

    # Draft exams are hidden from students.
    assert student.get(f"/student/exams/{exam_id}").status_code == 404
    teacher.post(f"/teacher/exams/{exam_id}/publish", data={"csrf": t})
    assert "Kiểm tra Cloud" in student.get("/student").get_data(as_text=True)

    s = csrf(student, f"/student/exams/{exam_id}")
    r = student.post(f"/student/exams/{exam_id}", data={
        "csrf": s, f"q{qids[0]}": "0", f"q{qids[1]}": ["0", "2"], f"q{qids[2]}": "1"})
    sub_page = student.get(r.headers["Location"]).get_data(as_text=True)
    assert "3/4" in sub_page and "(75%)" in sub_page and "ĐẠT" in sub_page

    with app.app_context():
        sub = Submission.query.one()
        key = sub.certificate_key
    pdf = student.get(f"/local-certificates/{key}")
    assert pdf.status_code == 200 and pdf.data.startswith(b"%PDF")
    assert other.get(f"/local-certificates/{key}").status_code == 403
    assert other.get(f"/submissions/{sub.id}").status_code == 403

    # Only one attempt: revisiting redirects to the existing result.
    assert student.get(f"/student/exams/{exam_id}").headers["Location"].endswith(f"/submissions/{sub.id}")

    report_csv = teacher.get(f"/teacher/exams/{exam_id}/results.csv").get_data(as_text=True)
    assert "Nguyễn An" in report_csv and "Đạt" in report_csv
    report = teacher.get(f"/teacher/exams/{exam_id}/report").get_data(as_text=True)
    assert "BÁO CÁO KẾT QUẢ" in report
    assert "Kết quả bài thi" in teacher.get(f"/teacher/exams/{exam_id}/results").get_data(as_text=True)


def test_grader_failure_marks_error_and_regrade(app, monkeypatch):
    import grader_client

    teacher, student = app.test_client(), app.test_client()
    login(teacher, "T", "t@x.edu", "teacher")
    login(student, "S", "s@x.edu", "student")
    t = csrf(teacher, "/teacher")
    r = teacher.post("/teacher/exams/new", data={"csrf": t, "title": "E"})
    exam_id = int(r.headers["Location"].split("/")[-1])
    teacher.post(f"/teacher/exams/{exam_id}/questions", data={
        "csrf": t, "text": "Q", "options": ["a", "b"], "correct": ["1"]})
    teacher.post(f"/teacher/exams/{exam_id}/publish", data={"csrf": t})

    real = grader_client.grade_submission

    def boom(payload):
        raise ConnectionError("lambda down")

    monkeypatch.setattr(grader_client, "grade_submission", boom)
    s = csrf(student, f"/student/exams/{exam_id}")
    r = student.post(f"/student/exams/{exam_id}", data={"csrf": s, "q1": "1"})
    page = student.get(r.headers["Location"]).get_data(as_text=True)
    assert "Chấm lại" in page

    monkeypatch.setattr(grader_client, "grade_submission", real)
    sub_path = r.headers["Location"]
    student.post(f"{sub_path}/regrade", data={"csrf": csrf(student, sub_path)})
    assert "1/1" in student.get(sub_path).get_data(as_text=True)
