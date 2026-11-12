from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    # Entra object id (oid claim), or "dev:<email>" in dev auth mode.
    external_id = db.Column(db.String(128), unique=True, nullable=False)
    name = db.Column(db.Unicode(200), nullable=False)
    email = db.Column(db.String(255))
    role = db.Column(db.String(20), nullable=False)  # "teacher" | "student"
    created_at = db.Column(db.DateTime, default=utcnow)


class Exam(db.Model):
    __tablename__ = "exams"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Unicode(300), nullable=False)
    description = db.Column(db.UnicodeText, default="")
    duration_minutes = db.Column(db.Integer, default=15)
    pass_percent = db.Column(db.Float, default=50)
    published = db.Column(db.Boolean, default=False, nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow)

    teacher = db.relationship("User")
    questions = db.relationship(
        "Question", backref="exam", cascade="all, delete-orphan", order_by="Question.position"
    )
    submissions = db.relationship("Submission", backref="exam", cascade="all, delete-orphan")

    @property
    def max_score(self):
        return sum(q.points for q in self.questions)


class Question(db.Model):
    __tablename__ = "questions"
    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey("exams.id"), nullable=False)
    position = db.Column(db.Integer, default=0)
    text = db.Column(db.UnicodeText, nullable=False)
    options = db.Column(db.JSON, nullable=False)  # ["option A", "option B", ...]
    correct = db.Column(db.JSON, nullable=False)  # indices into options, e.g. [0] or [0, 2]
    points = db.Column(db.Float, default=1)

    @property
    def is_multi(self):
        return len(self.correct) > 1


class Submission(db.Model):
    __tablename__ = "submissions"
    __table_args__ = (db.UniqueConstraint("exam_id", "student_id", name="uq_one_attempt"),)
    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey("exams.id"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    answers = db.Column(db.JSON, nullable=False)
    details = db.Column(db.JSON)
    score = db.Column(db.Float)
    max_score = db.Column(db.Float)
    percent = db.Column(db.Float)
    passed = db.Column(db.Boolean)
    certificate_key = db.Column(db.String(500))
    certificate_id = db.Column(db.String(20))
    status = db.Column(db.String(20), default="pending")  # pending | graded | error
    submitted_at = db.Column(db.DateTime, default=utcnow)

    student = db.relationship("User")
