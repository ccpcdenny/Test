"""重播驗證器：把真實戰報的隨機結果固定下來，用目前的公式重算每一筆傷害並對答案。

用法：
  python3 nobudb/replay.py          重播並輸出對照表、寫出 battles/001_replay.json／.txt
  python3 nobudb/replay.py --fit    用標記 fit 的資料重新擬合傷害參數

屬性：我方取自已驗算的戰鬥屬性（verify_attrs.py）；敵方只有 tooltip 的取整值，這裡取 +0.5 當估計。
未實作的規則會在紀錄裡標示，不會假裝算出來。
傷害顯示為無條件捨去；亂舞傷害 = 亂舞率 × 主目標傷害（與副目標統率無關），以 splash 事件驗證。
"""
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).parent

# 傷害模型（工作模型，見 MECHANICS.md「傷害公式」）
PARAMS = {"c": 1.24e-4, "alpha": 1.6, "beta": 230.0, "r_ichiryo": 0.1409}  # 一領具足實際 −14.09%（戰報）
MORALE_ENEMY = 0.9874  # 敵方士氣 98.2 → 造成傷害 98.74%

UNITS = {
    "立花道雪": {"side": "我", "武勇": 408.91, "智略": 191.62, "統率": 266.28, "red": [0.975, 0.98]},
    "立花闇千代": {"side": "我", "武勇": 416.88, "智略": 181.42, "統率": 222.40, "red": [0.975, 0.98]},
    "北條氏康": {"side": "我", "武勇": 173.96, "智略": 241.27, "統率": 388.31, "red": [0.975, 0.98]},
    "成田甲斐": {"side": "敵", "武勇": 226.45, "智略": 137.5, "統率": 175.5, "red": [], "dealt": 0.06 + 0.025},
    "福島正則": {"side": "敵", "武勇": 299.5, "智略": 145.5, "統率": 178.5, "red": [], "dealt": 0.53 + 0.025},
    "豐臣秀吉": {"side": "敵", "武勇": 135.47, "智略": 328.91, "統率": 218.10, "red": [], "dealt": 0.025 - 0.08},
}

# 事件：("hit", 回合, 攻擊者, 防守者, 參數) 或 ("mod", 回合, 目標, 屬性, 變化, 說明)
# 參數：T 攻擊方兵力、rate 傷害率、crit 會心傷害增幅、actual 戰報傷害、fit 是否用於擬合
EVENTS = [
    ("hit", 1, "成田甲斐", "北條氏康", dict(T=9841, actual=219, fit=True, note="普攻（氏康統率 388.31）")),
    ("mod", 1, "北條氏康", "統率", -140, "一觸即發"),
    ("hit", 1, "成田甲斐", "北條氏康", dict(T=9841, actual=387, fit=True, note="連擊第二下")),
    ("hit", 1, "成田甲斐", "北條氏康", dict(T=9841, rate=1.92, actual=743, note="理非曲直")),
    ("hit", 1, "立花道雪", "福島正則", dict(T=10252, actual=885, fit=True, note="普攻")),
    ("hit", 1, "立花闇千代", "豐臣秀吉", dict(T=10252, rate=0.76, actual=623, note="疾風迅雷")),
    ("hit", 1, "立花闇千代", "成田甲斐", dict(T=10252, rate=0.76, actual=709, note="疾風迅雷")),
    ("hit", 1, "立花闇千代", "成田甲斐", dict(T=10252, actual=921, fit=True, note="普攻")),
    ("hit", 1, "福島正則", "北條氏康", dict(T=9066, actual=667, fit=True, note="普攻")),
    ("hit", 1, "福島正則", "北條氏康", dict(T=9066, actual=681, note="連擊第二下（戰報原值）")),
    ("splash", 1, "福島正則", "立花闇千代", dict(main=667, rate=0.92, actual=613, note="七本槍筆頭 亂舞 92%")),
    ("splash", 1, "福島正則", "立花道雪", dict(main=667, rate=0.92, actual=613, note="七本槍筆頭 亂舞 92%")),
    ("splash", 1, "福島正則", "立花闇千代", dict(main=667, rate=0.70, actual=466, note="一力當先 亂舞 70%")),
    ("splash", 1, "福島正則", "立花道雪", dict(main=667, rate=0.70, actual=466, note="一力當先 亂舞 70%")),
    ("splash", 1, "福島正則", "立花闇千代", dict(main=681, rate=0.92, actual=626, note="七本槍筆頭 亂舞 92%（連擊）")),
    ("splash", 1, "福島正則", "立花道雪", dict(main=681, rate=0.92, actual=626, note="七本槍筆頭 亂舞 92%（連擊）")),
    ("splash", 1, "福島正則", "立花闇千代", dict(main=681, rate=0.70, actual=476, note="一力當先 亂舞 70%（連擊）")),
    ("splash", 1, "福島正則", "立花道雪", dict(main=681, rate=0.70, actual=476, note="一力當先 亂舞 70%（連擊）")),
    ("hit", 1, "北條氏康", "立花闇千代", dict(T=8453, actual=248, extra_red=0.5196,
                                           alt="智略", note="混亂誤擊；御旗盾無本身 −48.04%；攻擊屬性不明")),
    ("hit", 1, "豐臣秀吉", "立花道雪", dict(T=9778, actual=244, alt="智略",
                                          note="秀吉普攻（千成瓢簞治療後兵力 9778）；攻擊屬性不明")),
    ("hit", 2, "成田甲斐", "北條氏康", dict(T=9677, crit=0.525, actual=542, fit=True, note="會心")),
    ("hit", 2, "成田甲斐", "立花道雪", dict(T=9677, crit=0.525, actual=502, fit=True, note="連擊第二下，會心")),
]


def predict(att, dfn, ev, params=PARAMS, stat="武勇", stat_value=None):
    A = att[stat] if stat_value is None else stat_value
    base = params["c"] * ev["T"] * (params["alpha"] * A + params["beta"] - dfn["統率"])
    mult = (MORALE_ENEMY if att["side"] == "敵" else 1.0) * (1 + att.get("dealt", 0.0))
    mult *= (1 + ev.get("crit", 0.0)) * ev.get("rate", 1.0)
    mult *= ev.get("extra_red", 1.0)
    for f in dfn["red"]:
        mult *= f
    if dfn["side"] == "我" and ev.get("ichiryo", True):
        mult *= 1 - params["r_ichiryo"]  # 氏康「一領具足」：戰鬥前 2 回合全隊傷亡 −12%
    return base * mult


def replay():
    units = json.loads(json.dumps(UNITS))
    log, rows = [], []
    for e in EVENTS:
        if e[0] == "mod":
            _, rnd, who, stat, delta, why = e
            units[who][stat] += delta
            log.append({"round": rnd, "type": "狀態", "target": who, "stat": stat, "delta": delta, "reason": why,
                        "now": round(units[who][stat], 2)})
            continue
        _, rnd, atk, dfn, ev = e
        ev = {"rate": 1.0, "crit": 0.0, "fit": False, **ev}
        if e[0] == "splash":
            pred = math.floor(ev["main"] * ev["rate"])  # 顯示為無條件捨去
        else:
            pred = predict(units[atk], units[dfn], ev)
        row = {"round": rnd, "attacker": atk, "defender": dfn, "note": ev.get("note", ""),
               "predicted": round(pred, 1), "actual": ev["actual"],
               "error_pct": round((pred / ev["actual"] - 1) * 100, 1), "fit": ev["fit"],
               "defender_統率": round(units[dfn]["統率"], 2)}
        if "alt" in ev:
            row["alt"] = ev["alt"]
            alt = predict(units[atk], units[dfn], ev, stat=ev["alt"])
            row["predicted_if_" + ev["alt"]] = round(alt, 1)
        rows.append(row)
        log.append({"type": "攻擊", **row})
    return log, rows


def render(rows):
    out = ["回合 攻擊者        → 防守者        實際  預測   誤差   用於擬合  備註"]
    for r in rows:
        extra = f"（若用{r['alt']}：{r['predicted_if_' + r['alt']]}）" if "alt" in r else ""
        out.append(f"R{r['round']}  {r['attacker']:<6s} → {r['defender']:<6s}  {r['actual']:>4d} {r['predicted']:>6.1f} "
                   f"{r['error_pct']:>+5.1f}%  {'是' if r['fit'] else '否（驗證）'}  {r['note']}{extra}")
    return "\n".join(out)


def rms(rows):
    errs = [math.log(r["predicted"] / r["actual"]) for r in rows if r["predicted"] > 0]
    return math.sqrt(sum(e * e for e in errs) / len(errs)) * 100 if errs else float("nan")


def fit():
    units = json.loads(json.dumps(UNITS))
    hits = []
    for e in EVENTS:
        if e[0] == "mod":
            units[e[2]][e[3]] += e[4]
        elif e[0] == "hit" and e[4].get("fit"):
            hits.append((dict(units[e[2]]), dict(units[e[3]]), {"rate": 1.0, "crit": 0.0, **e[4]}))
    best = None
    r = PARAMS["r_ichiryo"]  # 一領具足 −14.09% 已由戰報直接得知，不再擬合
    for ci in range(90, 171, 2):
        c = ci * 1e-6
        for ai in range(120, 241, 4):
            a = ai / 100
            for b in range(0, 400, 5):
                p = {"c": c, "alpha": a, "beta": b, "r_ichiryo": r}
                total = 0.0
                for att, dfn, ev in hits:
                    v = predict(att, dfn, ev, p)
                    if v <= 0:
                        total = float("inf")
                        break
                    total += math.log(v / ev["actual"]) ** 2
                if best is None or total < best[0]:
                    best = (total, p)
    print(f"最佳參數 {best[1]}  rms {math.sqrt(best[0] / len(hits)) * 100:.1f}%（{len(hits)} 筆）")


if __name__ == "__main__":
    if "--fit" in sys.argv:
        fit()
        sys.exit()
    log, rows = replay()
    table = render(rows)
    print(table)
    fitted = [r for r in rows if r["fit"]]
    held = [r for r in rows if not r["fit"]]
    print(f"\n擬合用 {len(fitted)} 筆 rms {rms(fitted):.1f}%；驗證用 {len(held)} 筆 rms {rms(held):.1f}%")
    (HERE / "battles" / "001_replay.json").write_text(
        json.dumps({"params": PARAMS, "log": log}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    (HERE / "battles" / "001_replay.txt").write_text(table + "\n", encoding="utf-8")
