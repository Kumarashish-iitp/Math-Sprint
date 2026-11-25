
from django.shortcuts import render, redirect
import random


def home(request):
    return render(request, "home.html")


def build_ranges(difficulty):
    add_sub_ranges = {
        "easy": (1, 100),
        "medium": (1, 500),
        "hard": (1, 999),
    }

    mul_div_ranges = {
        "easy": (1, 20),
        "medium": (1, 40),
        "hard": (1, 60),
    }

    return add_sub_ranges[difficulty], mul_div_ranges[difficulty]


def generate_quiz(difficulty, operation, total_questions):

    (min_as, max_as), (min_md, max_md) = build_ranges(difficulty)

    questions = []
    answers = []

    operations = ["addition", "subtraction", "multiplication", "division"]

    for _ in range(total_questions):

        current_operation = (
            random.choice(operations) if operation == "mixed" else operation
        )

        if current_operation == "addition":
            num1 = random.randint(min_as, max_as)
            num2 = random.randint(min_as, max_as)
            answer = num1 + num2
            question_text = f"{num1} + {num2}"

        elif current_operation == "subtraction":
            num1 = random.randint(min_as, max_as)
            num2 = random.randint(min_as, max_as)

            num1, num2 = max(num1, num2), min(num1, num2)

            answer = num1 - num2
            question_text = f"{num1} - {num2}"

        elif current_operation == "multiplication":
            num1 = random.randint(min_md, max_md)
            num2 = random.randint(min_md, max_md)

            answer = num1 * num2
            question_text = f"{num1} × {num2}"

        else:
            divisor = random.randint(max(1, min_md), max_md)
            quotient = random.randint(min_md, max_md)

            dividend = divisor * quotient

            answer = quotient
            question_text = f"{dividend} ÷ {divisor}"

        questions.append(question_text)
        answers.append(answer)

    return questions, answers


def start_new_quiz(request, difficulty, operation, total_questions):

    questions, answers = generate_quiz(
        difficulty, operation, total_questions
    )

    request.session["quiz_data"] = {
        "questions": questions,
        "answers": answers,
        "current_index": 0,
        "total_questions": total_questions,
        "score": 0,
    }

    request.session["last_quiz_selection"] = {
        "difficulty": difficulty,
        "operation": operation,
        "total_questions": total_questions,
    }

    request.session.modified = True

    return redirect("play_quiz")


def quiz(request):

    if request.method == "POST":

        difficulty = request.POST.get("difficulty")
        operation = request.POST.get("operation")

        try:
            total_questions = int(request.POST.get("total_questions", 0))
        except (TypeError, ValueError):
            return redirect("home")

        valid_difficulties = ["easy", "medium", "hard"]

        valid_operations = [
            "addition",
            "subtraction",
            "multiplication",
            "division",
            "mixed",
        ]

        if difficulty not in valid_difficulties:
            return redirect("home")

        if operation not in valid_operations:
            return redirect("home")

        if total_questions not in [10, 15, 20]:
            return redirect("home")

        return start_new_quiz(
            request, difficulty, operation, total_questions
        )

    return redirect("home")


def play_quiz(request):

    quiz_data = request.session.get("quiz_data")

    if not quiz_data:
        return redirect("home")

    questions = quiz_data["questions"]
    answers = quiz_data["answers"]
    idx = quiz_data["current_index"]
    total = quiz_data["total_questions"]
    score = quiz_data["score"]

    feedback = None

    if request.method == "POST":

        raw_answer = request.POST.get("answer", "").strip()

        try:
            user_answer = int(raw_answer)
        except ValueError:
            user_answer = None

        correct_answer = answers[idx]

        if user_answer is not None and user_answer == correct_answer:
            score += 1
            feedback = "Sahi jawab!"
        else:
            feedback = f"Galat jawab! Sahi answer {correct_answer} tha."

        idx += 1

        if idx >= total:

            final_score = score

            del request.session["quiz_data"]
            request.session.modified = True

            return render(
                request,
                "result.html",
                {
                    "score": final_score,
                    "total_questions": total,
                },
            )

        quiz_data["current_index"] = idx
        quiz_data["score"] = score

        request.session["quiz_data"] = quiz_data
        request.session.modified = True

    return render(
        request,
        "question.html",
        {
            "question": questions[idx],
            "question_number": idx + 1,
            "total_questions": total,
            "score": score,
            "feedback": feedback,
        },
    )


def play_again(request):

    selection = request.session.get("last_quiz_selection")

    if not selection:
        return redirect("home")

    return start_new_quiz(
        request,
        selection["difficulty"],
        selection["operation"],
        selection["total_questions"],
    )
