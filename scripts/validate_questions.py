# scripts/validate_questions.py
import json
import sys
from collections import Counter

def validate(path: str) -> list[str]:
    with open(path, encoding='utf-8') as f:
        questions = json.load(f)

    errors = []
    ids = Counter(q['id'] for q in questions)
    for qid, count in ids.items():
        if count > 1:
            errors.append(f"重複 id: {qid} (出現 {count} 次)")

    per_chapter_qno = {}
    for q in questions:
        key = (q['chapterId'], q['questionNo'])
        per_chapter_qno.setdefault(key, []).append(q['id'])
    for key, qids in per_chapter_qno.items():
        if len(qids) > 1:
            errors.append(f"章節 {key[0]} 題號 {key[1]} 重複: ids={qids}")

    for q in questions:
        n_options = len(q['options'])
        if n_options < 2:
            errors.append(f"id {q['id']}: 選項數過少 ({n_options})")
        if not (1 <= q['answer'] <= n_options):
            errors.append(f"id {q['id']}: 正解 {q['answer']} 超出選項範圍 (共 {n_options} 個選項)")
        if not q['question'].strip():
            errors.append(f"id {q['id']}: 題幹為空")
        if q['chapterId'] not in range(101, 111) and q['chapterId'] not in (201, 202):
            errors.append(f"id {q['id']}: chapterId {q['chapterId']} 不在預期範圍 (101-110, 201, 202)")

    return errors


if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else \
        "/Users/fortune/investment-insurance-exam/app/assets/json/questions.json"
    errors = validate(path)
    if errors:
        print(f"發現 {len(errors)} 個問題：")
        for e in errors:
            print(" -", e)
        sys.exit(1)
    print("校驗通過，無問題。")
