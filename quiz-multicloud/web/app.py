import csv
import io
import secrets
import statistics

import click
from flask import (Flask, Response, abort, flash, g, redirect, render_template, request, send_file, session,
                   url_for)
from werkzeug.middleware.proxy_fix import ProxyFix

import grader_client
from auth import bp as auth_bp
from auth import login_required
from config import Config
from models import Exam, Question, Submission, User, db

LETTERS = "ABCDEFGH"


def create_app(overrides=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if overrides:
        app.config.update(overrides)
    if app.config["AUTH_MODE"] not in ("dev", "entra"):
        raise RuntimeError("AUTH_MODE must be 'dev' or 'entra'")
    # App Service terminates TLS at its front end; trust X-Forwarded-* so redirect URIs use https.
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
    db.init_app(app)
    app.register_blueprint(auth_bp)
    register_security(app)
    register_routes(app)
    register_cli(app)
    return app


def register_security(app):
    def csrf_token():
        if "csrf" not in session:
            session["csrf"] = secrets.token_urlsafe(32)
        return session["csrf"]

    @app.before_request
    def check_csrf():
        if request.method == "POST":
            sent = request.form.get("csrf", "")
            if not sent or not secrets.compare_digest(sent, session.get("csrf", "")):
                abort(400, "CSRF token không hợp lệ")

    app.jinja_env.globals.update(csrf_token=csrf_token, letters=LETTERS)
    app.jinja_env.filters["num"] = lambda x: "" if x is None else f"{x:g}"


def _own_exam(exam_id):
    exam = db.get_or_404(Exam, exam_id)
    if exam.teacher_id != g.user.id:
        abort(403)
    return exam


def _parse_correct(raw, n_options):
    """'A' / 'a;c' / 'B,D' -> [0] / [0, 2] / [1, 3]."""
    idx = sorted({LETTERS.index(c) for c in raw.upper() if c in LETTERS})
    if not idx or max(idx) >= n_options:
        raise ValueError(f"đáp án đúng không hợp lệ: '{raw}'")
    return idx


def _exam_stats(exam):
    graded = [s for s in exam.submissions if s.status == "graded"]
    if not graded:
        return None
    percents = [s.percent for s in graded]
    return {
        "count": len(graded),
        "avg": round(statistics.mean(percents), 2),
        "max": max(percents),
        "min": min(percents),
        "pass_rate": round(100 * sum(1 for s in graded if s.passed) / len(graded), 1),
    }


def _question_stats(exam):
    """Percentage of graded submissions answering each question correctly (for the report)."""
    graded = [s for s in exam.submissions if s.status == "graded" and s.details]
    out = {}
    for q in exam.questions:
        hits = [d["is_correct"] for s in graded for d in s.details if d["question_id"] == q.id]
        out[q.id] = round(100 * sum(hits) / len(hits), 1) if hits else None
    return out


def _grade_and_save(app, sub):
    """Send a submission to the grader and persist the result. Returns False if grading failed."""
    exam = sub.exam
    payload = {
        "submission_id": sub.id,
        "student": {"name": sub.student.name, "email": sub.student.email},
        "exam": {"id": exam.id, "title": exam.title, "pass_percent": exam.pass_percent},
        "questions": [{"id": q.id, "points": q.points, "correct": q.correct} for q in exam.questions],
        "answers": sub.answers,
    }
    try:
        result = grader_client.grade_submission(payload)
    except Exception:
        app.logger.exception("grading failed for submission %s", sub.id)
        sub.status = "error"
        db.session.commit()
        return False
    sub.score, sub.max_score, sub.percent = result["score"], result["max_score"], result["percent"]
    sub.passed, sub.details = result["passed"], result["details"]
    sub.certificate_key, sub.certificate_id = result["certificate_key"], result["certificate_id"]
    sub.status = "graded"
    db.session.commit()
    return True


def register_routes(app):
    @app.route("/")
    def index():
        if g.user is None:
            return render_template("home.html")
        return redirect(url_for("teacher_dashboard" if g.user.role == "teacher" else "student_dashboard"))

    # ---------- Teacher ----------
    @app.route("/teacher")
    @login_required("teacher")
    def teacher_dashboard():
        exams = Exam.query.filter_by(teacher_id=g.user.id).order_by(Exam.created_at.desc()).all()
        return render_template("teacher_dashboard.html", exams=exams)

    @app.route("/teacher/exams/new", methods=["GET", "POST"])
    @login_required("teacher")
    def exam_new():
        if request.method == "POST":
            title = request.form.get("title", "").strip()
            if not title:
                flash("Tên bài thi không được để trống.", "danger")
                return render_template("exam_form.html")
            exam = Exam(
                title=title,
                description=request.form.get("description", "").strip(),
                duration_minutes=max(1, request.form.get("duration_minutes", 15, type=int)),
                pass_percent=min(100, max(0, request.form.get("pass_percent", 50, type=float))),
                teacher_id=g.user.id,
            )
            db.session.add(exam)
            db.session.commit()
            flash("Đã tạo bài thi. Hãy thêm câu hỏi.", "success")
            return redirect(url_for("exam_manage", exam_id=exam.id))
        return render_template("exam_form.html")

    @app.route("/teacher/exams/<int:exam_id>")
    @login_required("teacher")
    def exam_manage(exam_id):
        return render_template("exam_manage.html", exam=_own_exam(exam_id))

    @app.route("/teacher/exams/<int:exam_id>/questions", methods=["POST"])
    @login_required("teacher")
    def question_add(exam_id):
        exam = _own_exam(exam_id)
        raw = request.form.getlist("options")
        kept = [i for i, o in enumerate(raw) if o.strip()]
        options = [raw[i].strip() for i in kept]
        # Re-index correct answers because blank option boxes are dropped.
        chosen = {int(i) for i in request.form.getlist("correct") if i.isdigit()}
        correct = sorted(kept.index(i) for i in chosen if i in kept)
        text = request.form.get("text", "").strip()
        if not text or len(options) < 2 or not correct:
            flash("Câu hỏi cần nội dung, ít nhất 2 lựa chọn và ít nhất 1 đáp án đúng (ở ô có nội dung).", "danger")
        else:
            db.session.add(Question(exam=exam, text=text, options=options, correct=correct,
                                    points=max(0.0, request.form.get("points", 1, type=float)),
                                    position=len(exam.questions)))
            db.session.commit()
            flash("Đã thêm câu hỏi.", "success")
        return redirect(url_for("exam_manage", exam_id=exam.id))

    @app.route("/teacher/exams/<int:exam_id>/import", methods=["POST"])
    @login_required("teacher")
    def question_import(exam_id):
        """CSV columns: question, A, B, C, D, correct (e.g. 'A' or 'A;C'), points (optional)."""
        exam = _own_exam(exam_id)
        file = request.files.get("file")
        if not file:
            flash("Chưa chọn file CSV.", "danger")
            return redirect(url_for("exam_manage", exam_id=exam.id))
        reader = csv.DictReader(io.StringIO(file.read().decode("utf-8-sig")))
        added, errors = 0, []
        for line, row in enumerate(reader, start=2):
            try:
                options = [row.get(k, "").strip() for k in "ABCD" if row.get(k, "").strip()]
                if not row.get("question", "").strip() or len(options) < 2:
                    raise ValueError("thiếu câu hỏi hoặc ít hơn 2 lựa chọn")
                db.session.add(Question(exam=exam, text=row["question"].strip(), options=options,
                                        correct=_parse_correct(row.get("correct", ""), len(options)),
                                        points=float(row.get("points") or 1),
                                        position=len(exam.questions)))
                added += 1
            except (ValueError, KeyError) as exc:
                errors.append(f"dòng {line}: {exc}")
        db.session.commit()
        flash(f"Đã nhập {added} câu hỏi.", "success" if added else "warning")
        for e in errors[:10]:
            flash(e, "danger")
        return redirect(url_for("exam_manage", exam_id=exam.id))

    @app.route("/teacher/exams/<int:exam_id>/questions/<int:qid>/delete", methods=["POST"])
    @login_required("teacher")
    def question_delete(exam_id, qid):
        exam = _own_exam(exam_id)
        q = db.get_or_404(Question, qid)
        if q.exam_id != exam.id:
            abort(404)
        if exam.submissions:
            flash("Không thể xoá câu hỏi khi đã có bài nộp.", "danger")
        else:
            db.session.delete(q)
            db.session.commit()
        return redirect(url_for("exam_manage", exam_id=exam.id))

    @app.route("/teacher/exams/<int:exam_id>/publish", methods=["POST"])
    @login_required("teacher")
    def exam_publish(exam_id):
        exam = _own_exam(exam_id)
        if not exam.published and not exam.questions:
            flash("Cần ít nhất 1 câu hỏi trước khi mở bài thi.", "danger")
        else:
            exam.published = not exam.published
            db.session.commit()
            flash("Đã mở bài thi cho học sinh." if exam.published else "Đã đóng bài thi.", "success")
        return redirect(url_for("exam_manage", exam_id=exam.id))

    @app.route("/teacher/exams/<int:exam_id>/delete", methods=["POST"])
    @login_required("teacher")
    def exam_delete(exam_id):
        db.session.delete(_own_exam(exam_id))
        db.session.commit()
        flash("Đã xoá bài thi.", "success")
        return redirect(url_for("teacher_dashboard"))

    @app.route("/teacher/exams/<int:exam_id>/results")
    @login_required("teacher")
    def exam_results(exam_id):
        exam = _own_exam(exam_id)
        subs = sorted(exam.submissions, key=lambda s: s.submitted_at, reverse=True)
        return render_template("exam_results.html", exam=exam, submissions=subs, stats=_exam_stats(exam))

    @app.route("/teacher/exams/<int:exam_id>/results.csv")
    @login_required("teacher")
    def exam_results_csv(exam_id):
        exam = _own_exam(exam_id)
        buf = io.StringIO()
        w = csv.writer(buf)
        w.writerow(["Họ tên", "Email", "Điểm", "Điểm tối đa", "Phần trăm", "Kết quả", "Nộp lúc (UTC)", "Mã chứng nhận"])
        for s in sorted(exam.submissions, key=lambda s: s.submitted_at):
            w.writerow([s.student.name, s.student.email, s.score, s.max_score, s.percent,
                        "Đạt" if s.passed else "Chưa đạt", s.submitted_at.strftime("%Y-%m-%d %H:%M"),
                        s.certificate_id or ""])
        # BOM so Excel opens Vietnamese text correctly.
        return Response("\ufeff" + buf.getvalue(), mimetype="text/csv",
                        headers={"Content-Disposition": f"attachment; filename=ket-qua-exam-{exam.id}.csv"})

    @app.route("/teacher/exams/<int:exam_id>/report")
    @login_required("teacher")
    def exam_report(exam_id):
        exam = _own_exam(exam_id)
        return render_template("exam_report.html", exam=exam, stats=_exam_stats(exam),
                               qstats=_question_stats(exam),
                               submissions=sorted(exam.submissions, key=lambda s: -(s.percent or 0)))

    # ---------- Student ----------
    @app.route("/student")
    @login_required("student")
    def student_dashboard():
        exams = Exam.query.filter_by(published=True).order_by(Exam.created_at.desc()).all()
        mine = {s.exam_id: s for s in Submission.query.filter_by(student_id=g.user.id)}
        return render_template("student_dashboard.html", exams=exams, mine=mine)

    @app.route("/student/exams/<int:exam_id>", methods=["GET", "POST"])
    @login_required("student")
    def take_exam(exam_id):
        exam = db.get_or_404(Exam, exam_id)
        if not exam.published:
            abort(404)
        existing = Submission.query.filter_by(exam_id=exam.id, student_id=g.user.id).first()
        if existing:
            return redirect(url_for("submission_view", sub_id=existing.id))
        if request.method == "GET":
            return render_template("take_exam.html", exam=exam)

        answers = {str(q.id): [int(v) for v in request.form.getlist(f"q{q.id}") if v.isdigit()]
                   for q in exam.questions}
        sub = Submission(exam_id=exam.id, student_id=g.user.id, answers=answers)
        db.session.add(sub)
        db.session.commit()
        if not _grade_and_save(app, sub):
            flash("Đã lưu bài làm nhưng chấm điểm thất bại. Bấm 'Chấm lại' hoặc báo giáo viên.", "danger")
        return redirect(url_for("submission_view", sub_id=sub.id))

    @app.route("/submissions/<int:sub_id>")
    @login_required()
    def submission_view(sub_id):
        sub = db.get_or_404(Submission, sub_id)
        if g.user.id not in (sub.student_id, sub.exam.teacher_id):
            abort(403)
        cert_url = None
        if sub.certificate_key:
            try:
                cert_url = grader_client.certificate_url(sub.certificate_key)
            except Exception:
                app.logger.exception("presign failed")
        details = {d["question_id"]: d for d in (sub.details or [])}
        return render_template("submission.html", sub=sub, exam=sub.exam, details=details, cert_url=cert_url)

    @app.route("/submissions/<int:sub_id>/regrade", methods=["POST"])
    @login_required()
    def submission_regrade(sub_id):
        sub = db.get_or_404(Submission, sub_id)
        if g.user.id not in (sub.student_id, sub.exam.teacher_id) or sub.status != "error":
            abort(403)
        if not _grade_and_save(app, sub):
            flash("Vẫn chưa chấm được, thử lại sau.", "danger")
        return redirect(url_for("submission_view", sub_id=sub.id))

    @app.route("/local-certificates/<path:key>")
    @login_required()
    def local_certificate(key):
        if not grader_client.is_local():
            abort(404)
        sub = Submission.query.filter_by(certificate_key=key).first_or_404()
        if g.user.id not in (sub.student_id, sub.exam.teacher_id):
            abort(403)
        return send_file(grader_client.local_certificate_path(key), mimetype="application/pdf")

    @app.errorhandler(403)
    def forbidden(_):
        return render_template("error.html", code=403, message="Bạn không có quyền truy cập trang này."), 403

    @app.errorhandler(404)
    def not_found(_):
        return render_template("error.html", code=404, message="Không tìm thấy trang."), 404


def register_cli(app):
    @app.cli.command("init-db")
    @click.option("--demo", is_flag=True, help="Thêm 1 giáo viên và 1 bài thi mẫu")
    def init_db(demo):
        """Create tables (works on SQLite and Azure SQL)."""
        db.create_all()
        click.echo("Tables created.")
        if demo and not Exam.query.first():
            teacher = User.query.filter_by(external_id="dev:teacher@demo.local").first() or User(
                external_id="dev:teacher@demo.local", name="Giáo viên Demo", email="teacher@demo.local",
                role="teacher")
            exam = Exam(title="Điện toán đám mây - Kiểm tra 15 phút", teacher=teacher, duration_minutes=10,
                        description="Bài thi mẫu", pass_percent=50, published=True)
            samples = [
                ("Dịch vụ nào của AWS dùng để lưu trữ object?", ["Amazon EC2", "Amazon S3", "Amazon RDS", "AWS Lambda"], [1]),
                ("Microsoft Entra ID dùng cho mục đích gì?", ["Lưu file", "Quản lý danh tính & phân quyền", "Chạy container", "Gửi email"], [1]),
                ("Những dịch vụ nào là serverless?", ["AWS Lambda", "Amazon EC2", "Azure Functions", "Azure VM"], [0, 2]),
                ("Presigned URL của S3 dùng để?", ["Cấp quyền truy cập object tạm thời", "Xoá bucket", "Tạo IAM user", "Mã hoá ổ đĩa"], [0]),
            ]
            for i, (text, opts, correct) in enumerate(samples):
                exam.questions.append(Question(text=text, options=opts, correct=correct, points=1, position=i))
            db.session.add(exam)
            db.session.commit()
            click.echo("Demo data added.")


app = create_app()
