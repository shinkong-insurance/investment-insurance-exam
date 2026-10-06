from __future__ import annotations  # python 3.9 相容 list[str] 型別標註

import zipfile
import xml.etree.ElementTree as ET
import re

NS = {'a': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}


def _col_to_idx(ref: str) -> int:
    letters = re.match(r'[A-Z]+', ref).group()
    idx = 0
    for ch in letters:
        idx = idx * 26 + (ord(ch) - ord('A') + 1)
    return idx - 1


def read_xlsx_rows(path: str) -> list[list[str]]:
    """讀 xlsx 的 sheet1，回傳每列的儲存格字串陣列（依欄位字母對齊，缺的補空字串）。"""
    with zipfile.ZipFile(path) as z:
        shared = []
        if 'xl/sharedStrings.xml' in z.namelist():
            root = ET.fromstring(z.read('xl/sharedStrings.xml'))
            for si in root.findall('a:si', NS):
                text = ''.join(t.text or '' for t in si.findall('.//a:t', NS))
                shared.append(text)
        sheet = ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
        rows = []
        for row in sheet.findall('.//a:row', NS):
            cells = {}
            maxidx = -1
            for c in row.findall('a:c', NS):
                idx = _col_to_idx(c.get('r'))
                v = c.find('a:v', NS)
                t = c.get('t')
                val = v.text if v is not None else ''
                if t == 's' and val != '':
                    val = shared[int(val)]
                cells[idx] = val
                maxidx = max(maxidx, idx)
            rows.append([cells.get(i, '') for i in range(max(maxidx + 1, 10))])
        return rows


ANSWER_LETTER_TO_INDEX = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5}


def _clean_explanation(s: str) -> str:
    """去頭尾空白；若內容只是單一答案字母 A-E（不含資訊）則清空。"""
    s = (s or '').strip()
    if len(s) == 1 and s.upper() in ANSWER_LETTER_TO_INDEX:
        return ''
    return s


def parse_chapter_file(path: str, chapter_id: int, start_question_no: int, start_id: int) -> list[dict]:
    rows = read_xlsx_rows(path)
    out = []
    qno = start_question_no
    qid = start_id
    for row in rows[2:]:  # 第0列標題、第1列欄名，從第2列起是題目
        if len(row) < 2 or not row[1]:
            continue  # 題型欄空白＝沒有題目（例如尾端空白列）
        question_text = row[0].strip()
        answer_letter = row[2].strip().upper()
        options = [row[6].strip(), row[7].strip(), row[8].strip(), row[9].strip()]
        options = [o for o in options if o]  # 去掉空白選項
        if answer_letter not in ANSWER_LETTER_TO_INDEX or ANSWER_LETTER_TO_INDEX[answer_letter] > len(options):
            raise ValueError(f"{path}: 第 {qno} 題正解 '{answer_letter}' 對應不到選項，需人工複核: {question_text[:30]}")
        out.append({
            'id': qid,
            'chapterId': chapter_id,
            'questionNo': qno,
            'question': question_text,
            'options': options,
            'answer': ANSWER_LETTER_TO_INDEX[answer_letter],
            'explanation': _clean_explanation(row[5]),
        })
        qno += 1
        qid += 1
    return out
