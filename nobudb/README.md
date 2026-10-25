# nobudb — 信長之野望 真戰 資料

資料來源：[nobudb.com](https://nobudb.com)（非官方社群整理，僅供參考）。

更新資料：`python3 nobudb/scrape.py`（需要 `beautifulsoup4`）

| 檔案 | 內容 |
|---|---|
| `data/tactics.json` | 戰法：品質、類型、發動機率（`rate`，小數；待核對者為 null）、來源武將、說明 |
| `data/status.json` | 戰法狀態：分類、疊加方式、說明、具備該狀態的戰法 |
| `data/traits.json` | 特性：專屬／通用，通用特性含各等級說明 |
| `data/officers.json` | 武將完整資料：基礎六圍（Lv1）、每級成長、特性與解鎖星數、自帶／傳承戰法、評定眾技能 |

## 尚缺（模擬對戰需要，網站沒有）
- 傷害公式（兵力、屬性差、兵種相剋）
- 行動順序與回合流程細節
- 實際發動率是否等於面板（需要戰報統計驗證）
