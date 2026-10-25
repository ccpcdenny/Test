"""戰鬥屬性計算流程，與戰報準備階段的數字對照（不含裝備）。

用法：python3 nobudb/verify_attrs.py
"""


def battle_attr(panel, troop_lv=0, combat=True, military=0.0, council=0.0,
                coop=0.0, season=0.0, tactic_pct=0.0, tactic_flat=0.0):
    v = panel
    if combat:
        v += panel * troop_lv * 0.02   # 兵種：每級 +2%，只加武勇、智略、統率、速度
    v += military                      # 軍學固定值
    v += panel * council               # 評定眾 %，以面板為底
    v += panel * coop                  # 設施協力 %，以面板為底
    v += season                        # 賽季固定值
    v += v * tactic_pct                # 特性、戰法 %，以當下數值為底
    v += tactic_flat                   # 戰法固定值（如三河武士統率 +16）
    return v


# (名稱, 算出值, 戰報值)；戰報值為準備階段各頁顯示的數字
CASES = [
    ("道雪 武勇（武威II 後）", battle_attr(307.48, 10, council=.0224, coop=.07, tactic_pct=.025), 407.31),
    ("道雪 統率（含三河武士）", battle_attr(189.79, 10, military=5, council=.0224, coop=.07, tactic_flat=16), 266.28),
    ("道雪 智略", battle_attr(148.27, 10, council=.0224, coop=.07), 191.62),
    ("道雪 速度", battle_attr(125.49, 10, council=.0224, coop=.07), 162.18),
    ("道雪 魅力", battle_attr(136.02, combat=False, council=.0224, coop=.07), 148.59),
    ("道雪 政務", battle_attr(154.81, combat=False, council=.0224, coop=.07), 169.12),
    ("闇千代 武勇（賽季後）", battle_attr(314.70, 10, council=.0224, coop=.07, season=2), 408.71),
    ("闇千代 智略（賽季後）", battle_attr(138.83, 10, council=.0224, coop=.07, season=2), 181.42),
]

if __name__ == "__main__":
    for name, calc, seen in CASES:
        ok = "✓" if abs(calc - seen) <= 0.05 else "✗"
        print(f"{ok} {name}: 算 {calc:.2f} / 戰報 {seen}")
