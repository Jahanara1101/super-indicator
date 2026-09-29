# Super Indicator — Pine port notes

`super_indicator.pine` is the ready-to-paste file: one line of `//@version=5`,
no other comments, 344 lines. Paste it into the TradingView Pine Editor and hit
**Add to chart**. Nothing needs editing.

`super_indicator_annotated.pine` is the same script with the full commentary —
keep it as the reference, don't paste it.

## What is exact vs approximate

Exact (Pine built-in == our Python):
RSI(14), EMA 20/50, MACD(12,26,9), Bollinger(20, 2σ, population stdev),
Stochastic(14,3), ATR(14), pivots (strict), trendline slope, rolling VWAP.

Approximate — same rules as Python but our own definitions, not Pine built-ins:
Structure (BOS/CHoCH), Fair Value Gap, Order Block, Volume Profile.

Cannot be mirrored at all: **Liquidation Magnet.** The clusters come from
ByKaranteli's API. The two `Liq cluster` inputs default to 0, which makes that
voter abstain (11 voters active instead of 12). Leave them at 0 unless you paste
real levels in; `minVoters = 4` still passes comfortably.

## Comparing against Python

Compare on the **same feed**. Python reads:
- gold intraday 1m–4H → Gate.io futures `XAU_USDT`
- gold 1D and above → Yahoo `GC=F` (COMEX), shifted onto OANDA spot
- crypto, all TFs → OKX

On an `OANDA:XAUUSD` chart the OHLC differs from those feeds by a few dollars, so
values will not match even when both implementations are correct.

## Differences to expect in the levels

- TP1–TP4 here are a pure R ladder (2R/3R/4R/5R). Python first prefers pivot S/R
  zones and liquidation magnets that give ≥ 1R, then fills from the ladder.
- The stop here uses the most recent confirmed pivot below/above price. Python
  merges all pivots into zones and takes the nearest.

## Guards (identical to Python)

`confidence ≥ 30%` **and** `|net score| ≥ 0.45` **and** `≥ 4 voters active`.
All three must pass or the output is NO TRADE.
