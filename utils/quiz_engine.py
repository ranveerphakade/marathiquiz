"""
Quiz Engine for Marathi Quiz Application
Handles quiz state initialization, question sampling, scoring, and review calculations.
"""

import random
from typing import List, Dict, Any, Tuple


MARATHI_DIGITS = {
    "0": "०", "1": "१", "2": "२", "3": "३", "4": "४",
    "5": "५", "6": "६", "7": "७", "8": "८", "9": "९"
}


def to_marathi_num(val: Any) -> str:
    """Converts standard integers/strings to Marathi numerals."""
    s = str(val)
    return "".join(MARATHI_DIGITS.get(ch, ch) for ch in s)


def select_questions(all_questions: List[Dict[str, Any]], mode: str = "full", count: int = 0) -> List[Dict[str, Any]]:
    """
    Selects questions based on quiz mode.
    - Full Quiz: all questions in existing order.
    - Practice Quiz: random sample of specified count.
    """
    if not all_questions:
        return []

    if mode == "full" or count <= 0 or count >= len(all_questions):
        return list(all_questions)

    # Practice mode: sample random questions without replacement
    sample_size = min(count, len(all_questions))
    return random.sample(all_questions, sample_size)


def calculate_score(questions: List[Dict[str, Any]], user_answers: Dict[Any, str]) -> Dict[str, Any]:
    """
    Computes final quiz score and detailed review breakdown.
    
    Returns:
        Dict containing total, correct, incorrect, unanswered, percentage, feedback, and wrong_questions list.
    """
    total = len(questions)
    if total == 0:
        return {
            "total": 0,
            "correct": 0,
            "incorrect": 0,
            "unanswered": 0,
            "percentage": 0.0,
            "feedback": "कोणतेही प्रश्न उपलब्ध नाहीत.",
            "wrong_questions": []
        }

    correct = 0
    incorrect = 0
    unanswered = 0
    wrong_questions = []

    for q in questions:
        q_id = q.get("id")
        correct_ans = str(q.get("answer", "")).strip()
        user_ans = user_answers.get(q_id)

        if user_ans is None or user_ans == "":
            unanswered += 1
            wrong_questions.append({
                "question_data": q,
                "user_answer": "उत्तर दिले नाही (Unanswered)",
                "correct_answer": correct_ans,
                "is_unanswered": True
            })
        elif str(user_ans).strip() == correct_ans:
            correct += 1
        else:
            incorrect += 1
            wrong_questions.append({
                "question_data": q,
                "user_answer": str(user_ans).strip(),
                "correct_answer": correct_ans,
                "is_unanswered": False
            })

    percentage = round((correct / total) * 100, 1)

    # Performance messages in Marathi as required
    if percentage >= 90:
        feedback = "🌟 अप्रतिम! खूप छान काम केले."
        badge = "success"
    elif percentage >= 75:
        feedback = "👏 खूप छान! अजून थोडा सराव करा."
        badge = "info"
    elif percentage >= 50:
        feedback = "👍 छान प्रयत्न! पुन्हा सराव करा."
        badge = "warning"
    else:
        feedback = "💪 पुन्हा सराव करा आणि प्रयत्न चालू ठेवा!"
        badge = "primary"

    return {
        "total": total,
        "correct": correct,
        "incorrect": incorrect,
        "unanswered": unanswered,
        "percentage": percentage,
        "feedback": feedback,
        "badge": badge,
        "wrong_questions": wrong_questions
    }
