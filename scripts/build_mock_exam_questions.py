from __future__ import annotations  # python 3.9 相容

import re

from parse_chapter_questions import read_xlsx_rows, is_question_row, row_to_question

_PUNCT_MAP = str.maketrans({
    '？': '?', '，': ',', '；': ';', '：': ':', '！': '!', '（': '(', '）': ')',
    '「': '"', '」': '"', '『': '"', '』': '"', '、': ',', '　': '', '\xa0': '',
})


def normalize_question_text(s: str) -> str:
    s = (s or '').translate(_PUNCT_MAP)
    return re.sub(r'\s+', '', s)


def _load_real_rows(path: str) -> list[list[str]]:
    """兩種來源（UMU 與 11501 範本）版面相同：第0列標題／須知、第1列欄名、第2列起題目，
    後面接大量空白預留列。只留 A、B 欄皆非空的列。"""
    rows = read_xlsx_rows(path)
    return [r for r in rows[2:] if is_question_row(r)]


# 人工核對後的選項修正，key = 正規化題幹。
# TIPP 題：UMU 原始 xlsx 選項 C 儲存格為「…買低賣高」的投資組合調整策略以上皆非」，選項 D 儲存格空白，
# 即「以上皆非」被誤串接到 C 尾端、D 漏填；拆回 C 與 D（正解 A 不受影響）。
_OPTION_OVERRIDES = {
    normalize_question_text('關於時間不變性投資組合保險策略（TIPP）的敘述，下列何者正確：'): {
        'split_suffix_from_option': (3, '以上皆非'),
    },
}


def _apply_override(row: list[str], key: str) -> list[str]:
    ov = _OPTION_OVERRIDES.get(key)
    if not ov:
        return row
    idx, suffix = ov['split_suffix_from_option']
    row = list(row)
    col = 5 + idx  # 選項 idx（1 起算）在欄 6+idx-1
    cell = row[col].strip()
    if not cell.endswith(suffix) or row[col + 1].strip():
        raise ValueError(f"override 前提不成立（原始資料已變動？）: {cell!r}")
    row[col] = cell[:-len(suffix)].strip()
    row[col + 1] = suffix
    return row


def load_subject_questions(umu_path: str, template_path: str, chapter_id: int, start_id: int) -> list[dict]:
    """合併 UMU 平台版與 11501 範本版，依題幹正規化後去重；重複時一律保留
    UMU 版的內容與正解（5 題答案衝突已與使用者核對，以 UMU 版為準）。"""
    seen = {}
    for path in (umu_path, template_path):  # UMU 先，先到先贏
        for row in _load_real_rows(path):
            seen.setdefault(normalize_question_text(row[0]), row)  # dict 保留插入順序

    out = []
    for qno, (key, row) in enumerate(seen.items(), start=1):
        row = _apply_override(row, key)
        out.append(row_to_question(row, chapter_id, qno, start_id + qno - 1,
                                   source=f'科目模考 chapter {chapter_id}'))
    return out
