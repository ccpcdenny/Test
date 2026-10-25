"""從 nobudb.com 抓取《信長之野望 真戰》資料，輸出成 JSON 到 data/。

用法：python3 nobudb/scrape.py
"""
import json
import re
import urllib.request
from pathlib import Path

from bs4 import BeautifulSoup

BASE = "https://nobudb.com"
OUT = Path(__file__).parent / "data"


def fetch(path):
    req = urllib.request.Request(BASE + path, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return BeautifulSoup(r.read().decode("utf-8"), "html.parser")


def text(el):
    return el.get_text("", strip=True) if el else None


def parse_rate(s):
    m = re.search(r"(\d+(?:\.\d+)?)%", s or "")
    return float(m.group(1)) / 100 if m else None


def tactics():
    soup = fetch("/tactics")
    out = []
    for art in soup.select("article.tactic"):
        name_el = art.select_one(".tacticname")
        grade = text(name_el.select_one(".tactic-grade"))
        name = text(name_el)[len(grade or ""):]
        meta = [text(s) for s in art.select(".skill-meta > span")]
        rate_raw = meta[1].replace("發動機率", "").strip() if len(meta) > 1 else None
        src = art.select_one(".innate-sources")
        out.append({
            "name": name,
            "grade": grade,
            "type": meta[0] if meta else None,
            "rate": parse_rate(rate_raw),
            "rate_raw": rate_raw,
            "source": text(src.select_one(".innate-tag")) if src else None,
            "officers": [b.contents[0].strip() for b in src.select(".tactic-officer-link")] if src else [],
            "desc": text(art.select_one(".tacticdesc")),
        })
    return out


def cards(path):
    """狀態、特性頁共用的卡片格式。"""
    soup = fetch(path)
    out = []
    for group in soup.select("section.status-group"):
        h2 = group.select_one("h2")
        category = h2.contents[0].strip() if h2 else None
        for art in group.select("article.status-card"):
            stack = art.select_one(".status-card-head small")
            out.append({
                "name": text(art.select_one(".tacticname")),
                "category": category,
                "stacking": text(stack).replace("疊加方式", "").strip() if stack else None,
                "desc": text(art.select_one(".tacticdesc")),
                # 通用特性分 I/II/III 等級，每級各有說明
                "levels": [text(d) for d in art.select(".trait-level .tacticdesc")],
                "tactics": [b.contents[-1].strip() for b in art.select(".status-tactic")],
            })
    return out


def officers():
    """名將錄頁面內嵌的完整武將資料（含成長值、特性、戰法）。"""
    soup = fetch("/catalog")
    payload = "".join(
        json.loads(m.group(1))
        for sc in soup.find_all("script")
        if (m := re.match(r'self\.__next_f\.push\(\[1,(".*")\]\)$', sc.string or "", re.S))
    )
    data, _ = json.JSONDecoder().raw_decode(payload, payload.index('[{"id":"'))
    return data


def main():
    OUT.mkdir(exist_ok=True)
    for name, fn in [
        ("tactics", tactics),
        ("status", lambda: cards("/status")),
        ("traits", lambda: cards("/traits")),
        ("officers", officers),
    ]:
        data = fn()
        (OUT / f"{name}.json").write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"{name}: {len(data)}")


if __name__ == "__main__":
    main()
