# nobudb — 信長之野望 真戰 資料

資料來源：[nobudb.com](https://nobudb.com)（非官方社群整理，僅供參考）。

更新資料：`python3 nobudb/scrape.py`（需要 `beautifulsoup4`）

| 檔案 | 內容 |
|---|---|
| `data/tactics.json` | 戰法：品質、類型、發動機率（`rate`，小數；待核對者為 null）、來源武將、說明 |
| `data/status.json` | 戰法狀態：分類、疊加方式、說明、具備該狀態的戰法 |
| `data/traits.json` | 特性：專屬／通用，通用特性含各等級說明 |
| `data/facilities.json` | 本城／支城設施（協力、兵種營、陣太鼓、守備櫓、督戰台、兵舍…）各等級效果 |
| `data/extra/tactics_missing.json` | 網站尚未收錄的戰法（手動補） |
| `battles/001.json` | 第一場戰報樣本（雙方屬性、逐筆傷害） |
| `MECHANICS.md` | 已確認／假設的戰鬥機制整理 |
| `verify_attrs.py` | 戰鬥屬性流程驗算 |
| `replay.py` | 重播驗證器：用真實戰報的隨機結果重算傷害並對答案（`--fit` 重新擬合參數），輸出 `battles/001_replay.json／.txt` |
| `data/officers.json` | 武將完整資料：基礎六圍（Lv1）、每級成長、特性與解鎖星數、自帶／傳承戰法、評定眾技能 |

## 尚缺（模擬對戰需要，網站沒有）
- 傷害公式（兵力、屬性差、兵種相剋）
- 行動順序與回合流程細節
- 實際發動率是否等於面板（需要戰報統計驗證）

`battles/001_transcript.md`：影片轉錄的完整戰報文字（準備階段、回合一、回合二開頭）。
