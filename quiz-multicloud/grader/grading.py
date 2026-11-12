"""Pure grading logic, shared by the AWS Lambda handler and the local dev mode."""


def grade(questions, answers):
    """Grade a submission.

    questions: [{"id": 1, "points": 1, "correct": [0, 2]}, ...]
    answers:   {"1": [0, 2], ...}  (keys are question ids as strings)

    A question scores full points only when the chosen set equals the correct set.
    """
    details = []
    score = 0.0
    max_score = 0.0
    for q in questions:
        points = float(q.get("points", 1))
        max_score += points
        chosen = sorted({int(x) for x in answers.get(str(q["id"]), [])})
        correct = sorted({int(x) for x in q["correct"]})
        is_correct = chosen == correct
        if is_correct:
            score += points
        details.append(
            {
                "question_id": q["id"],
                "chosen": chosen,
                "correct": correct,
                "is_correct": is_correct,
                "earned": points if is_correct else 0.0,
                "points": points,
            }
        )
    percent = round(score * 100 / max_score, 2) if max_score else 0.0
    return {"score": score, "max_score": max_score, "percent": percent, "details": details}
