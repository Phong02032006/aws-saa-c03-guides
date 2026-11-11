"""Sample data for demos/video: a teacher, several exams and graded submissions from a few students."""
import random

from models import Exam, Question, Submission, User, db

EXAMS = [
    {
        "title": "Điện toán đám mây - Kiểm tra giữa kỳ",
        "description": "Kiến thức nền tảng về AWS, Azure và mô hình dịch vụ đám mây.",
        "duration": 15, "pass": 50, "published": True,
        "questions": [
            ("Dịch vụ nào của AWS dùng để lưu trữ object?", ["Amazon EC2", "Amazon S3", "Amazon RDS", "AWS Lambda"], [1]),
            ("Microsoft Entra ID dùng cho mục đích gì?", ["Lưu file", "Quản lý danh tính & phân quyền", "Chạy container", "Gửi email"], [1]),
            ("Những dịch vụ nào là serverless?", ["AWS Lambda", "Amazon EC2", "Azure Functions", "Azure Virtual Machines"], [0, 2]),
            ("Presigned URL của S3 dùng để?", ["Cấp quyền truy cập object tạm thời", "Xoá bucket", "Tạo IAM user", "Mã hoá ổ đĩa"], [0]),
            ("Azure SQL Database thuộc mô hình dịch vụ nào?", ["IaaS", "PaaS", "SaaS", "On-premise"], [1]),
            ("Mô hình nào cho phép kết hợp nhiều nhà cung cấp đám mây?", ["Single-cloud", "Multi-cloud", "Private cloud", "Edge"], [1]),
        ],
    },
    {
        "title": "Bảo mật trên đám mây",
        "description": "IAM, mã hoá và nguyên tắc đặc quyền tối thiểu.",
        "duration": 10, "pass": 60, "published": True,
        "questions": [
            ("Nguyên tắc 'least privilege' nghĩa là?", ["Cấp toàn quyền cho admin", "Chỉ cấp quyền tối thiểu cần thiết", "Không dùng mật khẩu", "Tắt log"], [1]),
            ("Dịch vụ nào lưu bí mật (secret) an toàn?", ["AWS Secrets Manager", "Amazon S3 public", "Azure Key Vault", "Excel"], [0, 2]),
            ("MFA là viết tắt của?", ["Multi-Factor Authentication", "Main File Access", "Multi-Function App", "Managed Firewall"], [0]),
            ("Khi nào nên bật 'Block Public Access' cho S3?", ["Không bao giờ", "Khi bucket chứa dữ liệu riêng tư", "Chỉ khi host web", "Khi dùng Lambda"], [1]),
        ],
    },
    {
        "title": "Khảo sát mức độ hài lòng môn học",
        "description": "Bản nháp - chưa mở cho học sinh.",
        "duration": 5, "pass": 0, "published": False,
        "questions": [
            ("Bạn thấy môn học có hữu ích không?", ["Rất hữu ích", "Hữu ích", "Bình thường", "Không hữu ích"], [0, 1, 2, 3]),
        ],
    },
]

STUDENTS = ["Nguyễn Minh Anh", "Trần Quốc Bảo", "Lê Thu Hà", "Phạm Đức Huy", "Võ Ngọc Lan", "Đặng Gia Khánh"]


def seed_demo(app, grade_fn):
    """grade_fn(submission) grades and saves one submission (the app's normal grading path)."""
    if Exam.query.first():
        return False
    rng = random.Random(42)
    teacher = User(external_id="dev:teacher@demo.local", name="Cô Nguyễn Thị Mai", email="teacher@demo.local",
                   role="teacher")
    db.session.add(teacher)
    exams = []
    for spec in EXAMS:
        exam = Exam(title=spec["title"], description=spec["description"], duration_minutes=spec["duration"],
                    pass_percent=spec["pass"], published=spec["published"], teacher=teacher)
        for i, (text, opts, correct) in enumerate(spec["questions"]):
            exam.questions.append(Question(text=text, options=opts, correct=correct, points=1, position=i))
        db.session.add(exam)
        exams.append(exam)
    db.session.commit()

    for idx, name in enumerate(STUDENTS):
        email = f"sv{idx + 1}@demo.local"
        student = User(external_id=f"dev:{email}", name=name, email=email, role="student")
        db.session.add(student)
        db.session.commit()
        for exam in exams[:2]:
            if exam is exams[1] and idx % 2:
                continue
            skill = 0.35 + 0.6 * rng.random()
            answers = {}
            for q in exam.questions:
                if rng.random() < skill:
                    answers[str(q.id)] = list(q.correct)
                else:
                    answers[str(q.id)] = [rng.randrange(len(q.options))]
            sub = Submission(exam_id=exam.id, student_id=student.id, answers=answers)
            db.session.add(sub)
            db.session.commit()
            grade_fn(sub)
    return True
