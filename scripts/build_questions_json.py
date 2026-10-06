# 獨立執行腳本（非測試）：解析 10 章 UMU xlsx → scripts/out/questions_chapters.json（中繼產物），
# 再合併兩科模考題 → app/assets/json/questions.json（最終題庫）
import json
import os

from build_mock_exam_questions import load_subject_questions
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
FINAL_PATH = os.path.join(REPO, "app", "assets", "json", "questions.json")


def main():
    all_questions = []
    for chapter_id, fname in CHAPTERS:
        qs = parse_chapter_file(os.path.join(SRC_DIR, fname), chapter_id=chapter_id,
                                start_question_no=1, start_id=chapter_id * 1000)
        all_questions.extend(qs)
        print(f"chapter {chapter_id}: {len(qs)} 題")
    ids = [q["id"] for q in all_questions]
    assert len(ids) == len(set(ids)), "duplicate question ids in output"
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(all_questions, f, ensure_ascii=False, indent=2)
    print("total:", len(all_questions))

    mock1 = load_subject_questions(
        umu_path=os.path.join(SRC_DIR, "UMU_題庫(投資型考古題第一科測驗).xlsx"),
        template_path=os.path.join(SRC_DIR, "第一科(考古題11501).xlsx"),
        chapter_id=201, start_id=201000)
    mock2 = load_subject_questions(
        umu_path=os.path.join(SRC_DIR, "UMU_題庫(投資型考古題第二科測驗).xlsx"),
        template_path=os.path.join(SRC_DIR, "第二科(考古題11501).xlsx"),
        chapter_id=202, start_id=202000)
    print("第一科模考:", len(mock1), "　第二科模考:", len(mock2))

    final_questions = all_questions + mock1 + mock2
    final_ids = [q["id"] for q in final_questions]
    assert len(final_ids) == len(set(final_ids)), "duplicate question ids in final merged list"
    with open(FINAL_PATH, "w", encoding="utf-8") as f:
        json.dump(final_questions, f, ensure_ascii=False, indent=2)
    print("final total:", len(final_questions))


if __name__ == "__main__":
    main()
