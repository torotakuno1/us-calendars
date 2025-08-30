# US Macro Calendars (Apple/Google iCal ready)

このプロジェクトは、以下の **一次ソース**＋**Traders（月間ページ）** を統合し、
Apple/Google で購読できる `.ics` を自動生成します。

- FOMC（FRB公式）→ `docs/fomc.ics`
- Treasury 入札（FiscalData API）→ `docs/treasury_auctions.ics`
- OPEX（第3金曜・例外CSV）→ `docs/opex_us.ics`
- VIX 先物最終決済（CSV）→ `docs/vix_settlement.ics`
- 週次失業保険（木曜 08:30 ET・例外CSV）→ `docs/weekly_initial_claims.ics`
- 鉱工業生産 G.17（CSV）→ `docs/g17_industrial_production.ics`
- Traders（米イベント抽出）→ `docs/traders_us.ics`
- Earnings（Finnhub API・任意）→ `docs/earnings.ics`（デフォルト無効）

## 使い方（GitHub Pages公開）
1. このリポジトリを GitHub に作成し、`Settings → Pages → Source: GitHub Actions`（または `main` ブランチの `/docs`）で公開。
2. `Actions` を有効化。手動で **Run workflow** して `docs/*.ics` が生成されることを確認。
3. Apple カレンダー（iOS/macOS）：「設定 → カレンダー → アカウント → 照会するカレンダーを追加」で、`https://<user>.github.io/<repo>/<ics>` を登録。
   - 例：`https://<user>.github.io/<repo>/fomc.ics`
4. Google カレンダー：「その他のカレンダー → URL で追加」に同様の URL を登録。

## 例外CSVの編集
- `data/opex_exceptions_20XX.csv`：祝日繰上げ等で第3金曜がズレる場合に記載
- `data/vix_settlement_20XX.csv`：CFEの最終決済日を列挙（年次PDF/表に合わせて更新）
- `data/ui_exceptions_20XX.csv`：木曜8:30 ETからの例外（祝日前倒し等）
- `data/g17_schedule_20XX.csv`：FRBのリリース日程（G.17）

## 環境変数（任意）
- `FINNHUB_TOKEN`：Earnings（Finnhub API）を使う場合に設定

## 注意
- 一部サイトは HTML 構造変更があります。`scripts/make_traders_ics.py` は月1回程度の点検を推奨。
- 祝日例外は毎年、**Cboe/OCC/CFE の一次資料**で検証して CSV を更新してください。
