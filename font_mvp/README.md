# Galaxy Leo King 字型 MVP

這是一個**原創、風格啟發**的 MVP 字型草案，靈感來自你提供的海報氛圍（銀河、史詩、金屬雕刻感），**不是對既有商標字樣的逐筆拷貝**。

## 目前交付

- `build_galaxy_leo_mvp_svg_font.py`：產生 SVG 字型檔的腳本。
- `GalaxyLeoKing-MVP.svg`：MVP 字型輸出。
- `style_rules.md`：從圖像抽取的字體設計規則（可作為後續擴字規格）。

## 支援字元（MVP v2）

- `A-Z`
- `a-z`
- `0-9`
- `銀河Leo星王`
- 空白

> 小寫採與大寫同骨架的展示字策略（偏標題用途）。

## 產生方式

```bash
python font_mvp/build_galaxy_leo_mvp_svg_font.py
```

## 設計規則（摘要）

1. **整體語氣**：史詩奇幻 + 星際科技。
2. **筆畫結構**：粗主幹、清楚重心、直向支撐感。
3. **收筆**：帶尖角或切面（像金屬切割）。
4. **對比**：主幹偏厚、內部留白足夠，確保縮小可讀性。
5. **版面節奏**：中宮略緊，字面偏滿，標題視覺更有壓迫力。


## 直接轉出 .otf（方式 1：FontForge）

```bash
bash font_mvp/export_otf.sh
# 或指定輸入/輸出
bash font_mvp/export_otf.sh font_mvp/GalaxyLeoKing-MVP.svg font_mvp/GalaxyLeoKing-MVP.otf
```

> 轉檔腳本：`export_otf_with_fontforge.pe`

## 後續建議

- 若要輸出 `.otf`，可用 FontForge 或 fonttools 將此 MVP 輪廓重建/轉換。
- 下一版可擴充：常用標點、中文常用 300 字、連字與 kerning。
