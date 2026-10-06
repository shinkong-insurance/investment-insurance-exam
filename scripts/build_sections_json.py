"""Assemble scripts/sections_draft/chapter_*.json into app/assets/json/sections.json.

Section id = chapterId * 100 + order (e.g. 10101).
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DRAFT_DIR = ROOT / "scripts" / "sections_draft"
OUT_PATH = ROOT / "app" / "assets" / "json" / "sections.json"


def build(draft_dir: Path = DRAFT_DIR, out_path: Path = OUT_PATH) -> list:
    sections = []
    for path in sorted(Path(draft_dir).glob("chapter_*.json")):
        draft = json.loads(path.read_text(encoding="utf-8"))
        chapter_id = draft["chapterId"]
        assert 101 <= chapter_id <= 110, f"{path.name}: bad chapterId {chapter_id}"
        items = draft["sections"]
        assert len(items) < 100, f"{path.name}: too many sections"
        orders = [s["order"] for s in items]
        assert orders == list(range(1, len(items) + 1)), f"{path.name}: orders not 1..n: {orders}"
        for s in items:
            sections.append({
                "id": chapter_id * 100 + s["order"],
                "chapterId": chapter_id,
                "order": s["order"],
                "title": s["title"],
                "content": s["content"],
            })
    ids = [s["id"] for s in sections]
    assert len(ids) == len(set(ids)), "duplicate section ids"
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(sections, ensure_ascii=False, indent=2), encoding="utf-8")
    return sections


if __name__ == "__main__":
    result = build()
    print("total sections:", len(result))
    for cid in range(101, 111):
        print(cid, sum(1 for s in result if s["chapterId"] == cid))
