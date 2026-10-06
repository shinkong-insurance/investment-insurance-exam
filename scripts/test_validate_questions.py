import json
import pytest
from validate_questions import validate


def test_validate_real_questions():
    """Test that validate() on the real questions.json returns no errors."""
    path = "/Users/fortune/investment-insurance-exam/app/assets/json/questions.json"
    errors = validate(path)
    assert errors == [], f"Expected no errors, but found: {errors}"


def test_validate_with_errors(tmp_path):
    """Test that validate() detects various errors in a temp JSON file."""
    # Create a test file with multiple errors
    test_data = [
        # Normal question
        {
            "id": 101001,
            "chapterId": 101,
            "questionNo": 1,
            "question": "Valid question?",
            "options": ["A", "B", "C"],
            "answer": 1
        },
        # Duplicate id
        {
            "id": 101001,
            "chapterId": 101,
            "questionNo": 2,
            "question": "Another question?",
            "options": ["A", "B"],
            "answer": 1
        },
        # Out-of-range answer
        {
            "id": 101002,
            "chapterId": 101,
            "questionNo": 3,
            "question": "Question with bad answer?",
            "options": ["A", "B"],
            "answer": 5
        },
        # Empty question
        {
            "id": 101003,
            "chapterId": 101,
            "questionNo": 4,
            "question": "   ",
            "options": ["A", "B"],
            "answer": 1
        },
        # Invalid chapterId
        {
            "id": 101004,
            "chapterId": 999,
            "questionNo": 5,
            "question": "Question with bad chapter?",
            "options": ["A", "B"],
            "answer": 1
        }
    ]

    test_file = tmp_path / "test_questions.json"
    test_file.write_text(json.dumps(test_data), encoding='utf-8')

    errors = validate(str(test_file))

    # Should have errors for: duplicate id, out-of-range answer, empty question, invalid chapterId
    assert len(errors) >= 4, f"Expected at least 4 errors, got {len(errors)}: {errors}"

    # Verify specific errors are present
    error_text = " ".join(errors)
    assert "重複 id" in error_text or "101001" in error_text, f"Missing duplicate id error in: {errors}"
    assert "正解" in error_text and "超出選項範圍" in error_text, f"Missing answer range error in: {errors}"
    assert "題幹為空" in error_text, f"Missing empty question error in: {errors}"
    assert "999" in error_text or "chapterId" in error_text, f"Missing chapterId error in: {errors}"
