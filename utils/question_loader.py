"""
Question Loader for Marathi Quiz Application
Handles loading, validation, and normalization of quiz questions from JSON files.
"""

import json
import os
from typing import List, Dict, Any, Tuple, Optional


def normalize_question(item: Dict[str, Any], index: int) -> Optional[Dict[str, Any]]:
    """
    Normalizes a single question dictionary into a standard format.
    Ensures required fields exist and values are cleaned.
    """
    if not isinstance(item, dict):
        return None

    # Question text is mandatory
    question_text = str(item.get("question") or item.get("q") or "").strip()
    if not question_text:
        return None

    # Options list
    raw_options = item.get("options") or item.get("choices") or []
    if not isinstance(raw_options, list):
        return None
    options = [str(opt).strip() for opt in raw_options if str(opt).strip()]
    if len(options) < 2:
        return None

    # Answer
    raw_answer = str(item.get("answer") or item.get("correct_answer") or "").strip()
    if not raw_answer:
        # Fallback: if answer is given as an index (0-based or 1-based)
        ans_idx = item.get("answer_index")
        if isinstance(ans_idx, int) and 0 <= ans_idx < len(options):
            raw_answer = options[ans_idx]
        elif isinstance(ans_idx, int) and 1 <= ans_idx <= len(options):
            raw_answer = options[ans_idx - 1]

    # Ensure answer is in options, or match case-insensitively / trimmed
    matched_answer = raw_answer
    if raw_answer not in options:
        for opt in options:
            if opt.strip().lower() == raw_answer.strip().lower():
                matched_answer = opt
                break
    
    if not matched_answer:
        # If still no valid answer, use first option or keep raw_answer
        matched_answer = options[0] if options else ""

    # ID
    raw_id = item.get("id")
    if raw_id is not None:
        try:
            q_id = int(raw_id)
        except (ValueError, TypeError):
            q_id = str(raw_id)
    else:
        q_id = index + 1

    # Standardized Question Object
    return {
        "id": q_id,
        "class": item.get("class", 4),
        "subject": item.get("subject", "Marathi"),
        "topic": str(item.get("topic", "")).strip(),
        "question": question_text,
        "options": options,
        "answer": matched_answer,
        "explanation": str(item.get("explanation", "")).strip(),
        "validation_note": str(item.get("validation_note", "")).strip(),
        "teacher": str(item.get("teacher", "")).strip() if item.get("teacher") else None
    }


def load_questions(file_path: Optional[str] = None) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Loads and normalizes questions from a JSON file.
    
    Returns:
        tuple: (list_of_questions, metadata_dict)
    """
    candidate_paths = []
    
    if file_path:
        candidate_paths.append(file_path)
        
    # Relative to current file
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    candidate_paths.append(os.path.join(base_dir, "data", "questions.json"))
    candidate_paths.append(os.path.join(os.getcwd(), "data", "questions.json"))
    candidate_paths.append(os.path.join(os.getcwd(), "marathi_quiz", "data", "questions.json"))
    candidate_paths.append(r"c:\Users\ASUS\Desktop\quiz\marathi.json")

    resolved_path = None
    for path in candidate_paths:
        if path and os.path.exists(path):
            resolved_path = path
            break

    if not resolved_path:
        return [], {
            "error": "प्रश्नांची फाईल (questions.json) सापडली नाही. कृपया data/questions.json फाईल तपासा.",
            "raw_error": "File not found in search paths."
        }

    try:
        with open(resolved_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
    except UnicodeDecodeError:
        try:
            with open(resolved_path, "r", encoding="utf-8-sig") as f:
                raw_data = json.load(f)
        except Exception as e:
            return [], {
                "error": f"फाईल वाचताना त्रुटी आली: {str(e)}",
                "raw_error": str(e)
            }
    except json.JSONDecodeError as e:
        return [], {
            "error": f"JSON फाईलचे स्वरूप चुकीचे आहे: {str(e)}",
            "raw_error": str(e)
        }
    except Exception as e:
        return [], {
            "error": f"फाईल उघडता आली नाही: {str(e)}",
            "raw_error": str(e)
        }

    # Extract questions list and any top-level metadata
    metadata: Dict[str, Any] = {
        "file_path": resolved_path,
        "teacher": None,
        "subject": "मराठी",
        "class": "४ थी",
    }

    raw_list = []
    if isinstance(raw_data, list):
        raw_list = raw_data
    elif isinstance(raw_data, dict):
        # Could be {"teacher": "...", "questions": [...]} or {"data": [...]}
        if "teacher" in raw_data:
            metadata["teacher"] = raw_data["teacher"]
        if "subject" in raw_data:
            metadata["subject"] = raw_data["subject"]
        if "class" in raw_data:
            metadata["class"] = raw_data["class"]
            
        for key in ["questions", "items", "data", "quiz"]:
            if key in raw_data and isinstance(raw_data[key], list):
                raw_list = raw_data[key]
                break

    if not raw_list:
        return [], {
            "error": "फाईलमध्ये एकही प्रश्न उपलब्ध नाही.",
            "raw_error": "Empty or unrecognized question list format."
        }

    # Normalize each question
    normalized_questions = []
    for idx, item in enumerate(raw_list):
        norm = normalize_question(item, idx)
        if norm:
            # If item has teacher info and metadata doesn't, capture it
            if norm.get("teacher") and not metadata.get("teacher"):
                metadata["teacher"] = norm["teacher"]
            normalized_questions.append(norm)

    if not normalized_questions:
        return [], {
            "error": "प्रश्नांचे वैध स्वरूप सापडले नाही.",
            "raw_error": "All items failed normalization."
        }

    metadata["total_loaded"] = len(normalized_questions)
    return normalized_questions, metadata
