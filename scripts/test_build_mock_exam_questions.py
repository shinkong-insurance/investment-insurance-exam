from build_mock_exam_questions import normalize_question_text, load_subject_questions

SRC = "/Users/fortune/investment-insurance-exam/source-materials/"
U1 = SRC + "UMU_題庫(投資型考古題第一科測驗).xlsx"
T1 = SRC + "第一科(考古題11501).xlsx"
U2 = SRC + "UMU_題庫(投資型考古題第二科測驗).xlsx"
T2 = SRC + "第二科(考古題11501).xlsx"


def test_normalize_strips_fullwidth_punct_and_whitespace():
    a = normalize_question_text("下列何者為貨幣市場的證券？")
    b = normalize_question_text("下列何者為貨幣市場的證券?")
    assert a == b


def test_load_subject_one_dedup_count():
    # 第一科：UMU 50 + 11501 範本 50，重複 5 題，去重後 95 題
    qs = load_subject_questions(umu_path=U1, template_path=T1, chapter_id=201, start_id=201000)
    assert len(qs) == 95
    assert qs[0]['id'] == 201000 and qs[0]['chapterId'] == 201


def test_load_subject_two_dedup_count():
    qs = load_subject_questions(umu_path=U2, template_path=T2, chapter_id=202, start_id=202000)
    assert len(qs) == 181


def test_tipp_options_fixed_to_four():
    qs = load_subject_questions(umu_path=U2, template_path=T2, chapter_id=202, start_id=202000)
    assert all(len(q['options']) == 4 for q in qs)


def test_tipp_option_c_d_split():
    qs = load_subject_questions(umu_path=U2, template_path=T2, chapter_id=202, start_id=202000)
    tipp = [q for q in qs if '時間不變性' in q['question']]
    assert len(tipp) == 1
    assert tipp[0]['options'][2].endswith('投資組合調整策略')
    assert tipp[0]['options'][3] == '以上皆非'
    assert tipp[0]['answer'] == 1
