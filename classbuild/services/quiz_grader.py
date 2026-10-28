from classbuild.models.quiz import Quiz
def grade_quiz(
    quiz: Quiz,
    answers: list[str | None],
) -> tuple[int, list[dict]]:
    if len(answers) != len(quiz.questions):
        raise ValueError("The number of answers does not match the quiz.")
    score = 0
    results = []
    for question, answer in zip(quiz.questions, answers):
        is_correct = answer == question.correct_answer
        if is_correct:
            score += 1

        results.append(
            {
                "question": question.question,
                "selected_answer": answer,
                "correct_answer": question.correct_answer,
                "is_correct": is_correct,
                "explanation": question.explanation,
            }
        )

    return score, results