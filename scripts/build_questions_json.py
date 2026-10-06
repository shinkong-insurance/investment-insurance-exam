# 獨立執行腳本（非測試）：解析 10 章 UMU xlsx → scripts/out/questions_chapters.json（中繼產物）
import json
import os

from parse_chapter_questions import parse_chapter_file

CHAPTERS = [
    (101, "UMU_題庫(投資型第一章測驗).xlsx"),
    (102, "UMU_題庫(投資型第二章測驗).xlsx"),
    (103, "UMU_題庫(投資型第三章測驗).xlsx"),
    (104, "UMU_題庫(投資型第四章測驗).xlsx"),
    (105, "UMU_題庫(投資型第五章測驗).xlsx"),
    (106, "UMU_題庫(投資型第六章測驗).xlsx"),
    (107, "UMU_題庫(投資型第七章測驗).xlsx"),
    (108, "UMU_題庫(投資型第八章測驗).xlsx"),
    (109, "UMU_題庫(投資型第九章測驗).xlsx"),
    (110, "UMU_題庫(投資型第十章測驗).xlsx"),
]
REPO = "/Users/fortune/investment-insurance-exam"
SRC_DIR = os.path.join(REPO, "source-materials")
OUT_PATH = os.path.join(REPO, "scripts", "out", "questions_chapters.json")


def main():
    all_questions = []
    for chapter_id, fname in CHAPTERS:
        qs = parse_chapter_file(os.path.join(SRC_DIR, fname), chapter_id=chapter_id,
                                start_question_no=1, start_id=chapter_id * 100)
        all_questions.extend(qs)
        print(f"chapter {chapter_id}: {len(qs)} 題")
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(all_questions, f, ensure_ascii=False, indent=2)
    print("total:", len(all_questions))


if __name__ == "__main__":
    main()
