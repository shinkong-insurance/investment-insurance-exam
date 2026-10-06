from parse_chapter_questions import read_xlsx_rows, parse_chapter_file, _clean_explanation

SRC = "/Users/fortune/investment-insurance-exam/source-materials/UMU_題庫(投資型第五章測驗).xlsx"


def test_read_xlsx_rows_header():
    rows = read_xlsx_rows(SRC)
    assert rows[1][:6] == ['問題描述', '題型', '正確答案', '分值', '難度', '答案說明']


def test_parse_chapter_file_count_and_shape():
    questions = parse_chapter_file(SRC, chapter_id=105, start_question_no=1, start_id=105000)
    assert len(questions) == 21
    q = questions[0]
    assert q['chapterId'] == 105
    assert q['questionNo'] == 1
    assert q['id'] == 105000
    assert len(q['options']) == 4
    assert q['answer'] in (1, 2, 3, 4)
    assert q['question']  # 非空


def test_clean_explanation_drops_letter_only():
    for s in ['A', 'b', ' C ', 'D', 'E']:
        assert _clean_explanation(s) == ''
    assert _clean_explanation(' 因為利率上升 ') == '因為利率上升'
    assert _clean_explanation('AB') == 'AB'
    assert _clean_explanation('') == ''
