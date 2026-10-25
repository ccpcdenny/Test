"""用回合一、二的普通攻擊擬合傷害公式（暫時假設，不含裝備、兵種相剋）。

模型：傷害 = c × 攻擊方兵力 × (α×武勇 + β − 防守方統率) × M
  M = 士氣 × (1 + 造成傷害增益) × 會心 × 防守方減傷（軍學、兵學、一領具足）× 傷害率
用法：python3 nobudb/fit_damage.py
"""
import itertools
import math

MORALE_ENEMY = 0.9874
# 名稱, 攻擊方武勇, 攻擊方兵力, 防守方統率, 傷害, 攻擊方倍率(不含防守方減傷), 防守方是否為我方, 防守方基本減傷
HITS = [
    ("甲斐R1#1→氏康", 226.5, 9841, 388.31, 219, (1 + .06 + .025) * MORALE_ENEMY, True, 0.975),
    ("甲斐R1#2→氏康", 226.5, 9841, 248.31, 387, (1 + .06 + .025) * MORALE_ENEMY, True, 0.975),
    ("福島R1→氏康", 299.5, 9066, 248.31, 667, (1 + .53 + .025) * MORALE_ENEMY, True, 0.975),
    ("道雪→福島", 408.91, 10252, 178.5, 885, 1.0, False, 1.0),
    ("千代→甲斐", 416.88, 10252, 175.5, 921, 1.0, False, 1.0),
    ("甲斐R2會心→氏康", 226.5, 9677, 248.31, 542, 1.525 * (1 + .06 + .025) * MORALE_ENEMY, True, 0.975),
    ("甲斐R2會心→道雪", 226.5, 9677, 266.28, 502, 1.525 * (1 + .06 + .025) * MORALE_ENEMY, True, 0.975 * 0.98),
]


def predict(h, c, a, b, r):
    _, A, T, D, _, M, ours, R = h
    return c * T * (a * A + b - D) * M * R * ((1 - r) if ours else 1.0)


def loss(c, a, b, r):
    total = 0.0
    for h in HITS:
        p = predict(h, c, a, b, r)
        if p <= 0:
            return float("inf")
        total += math.log(p / h[4]) ** 2
    return total


best = None
for r in [0.0, 0.06, 0.12, 0.18]:
    for a in [x / 20 for x in range(10, 61)]:
        for b in range(-100, 600, 10):
            for c in [x * 1e-5 for x in range(5, 40)]:
                l = loss(c, a, b, r)
                if best is None or l < best[0]:
                    best = (l, c, a, b, r)
l, c, a, b, r = best
print(f"最佳 c={c:.2e} α={a:.2f} β={b} r={r}  rms 誤差 {math.sqrt(l/len(HITS))*100:.1f}%")
for h in HITS:
    p = predict(h, c, a, b, r)
    print(f"{h[0]:14s} 實際 {h[4]:4d} 預測 {p:6.1f} ({(p/h[4]-1)*100:+.1f}%)")
