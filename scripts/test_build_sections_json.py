from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_sections_json import build, DRAFT_DIR  # noqa: E402


def test_build_from_real_drafts(tmp_path):
    out = tmp_path / "sections.json"
    sections = build(DRAFT_DIR, out)
    assert out.exists()
    assert len(sections) == 46
    ids = [s["id"] for s in sections]
    assert len(set(ids)) == len(ids)
    assert min(ids) >= 10101
    assert {s["chapterId"] for s in sections} == set(range(101, 111))
    for s in sections:
        assert s["title"].strip()
        assert s["content"].strip()
        assert "僅供內部教育訓練使用" not in s["content"]
        assert "機密等級" not in s["content"]
