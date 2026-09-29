# ICT Liquidity Model — backtest results

6000 bars per market, real exchange data (Gate `XAU_USDT` for gold, OKX spot for
crypto). Entry is a limit order, never a fill at signal; when a bar spans both
stop and target the stop is assumed. No lookahead: every pivot used was already
confirmed at the signal bar.

## Verdict

| Market | Trades | Win | Expectancy | Total | PF | MaxDD | Half 1 | Half 2 | Best trade share |
|---|---|---|---|---|---|---|---|---|---|
| GOLD 1H | 154 | 49.4% | +0.367R | +56.6R | 1.73 | -14.0R | +0.722R (PF 2.97) | +0.417R (PF 1.70) | 8% |
| **BTC 1H** | 160 | 58.8% | +0.549R | +87.9R | 2.33 | -7.7R | +0.518R (PF 2.22) | +0.610R (PF 2.53) | 3% |
| **ETH 1H** | 159 | 60.4% | +0.615R | +97.8R | 2.55 | -7.0R | +0.612R (PF 2.56) | +0.736R (PF 2.96) | 4% |
| GOLD 15m | 142 | 45.1% | +0.628R | +89.2R | 2.14 | -14.7R | +0.145R (PF 1.23) | +1.228R (PF 3.62) | **59%** |

**One split is one sample — do not trust it.** The same gold 1H run gave
half-2 = **-0.06R (PF 0.91, fails)** at 4000 bars and +0.417R (PF 1.70, passes)
at 6000 bars. The verdict flipped on history depth alone, so a single
first-half/second-half split proves nothing. Rolling windows below are the real
test.

## Rolling windows (1500 bars, step 500) — the stability test

| Market | Positive windows | Worst window | Best-trade-share problem |
|---|---|---|---|
| **ETH 1H** | **12 / 12** | +0.227R (PF 1.43) | max 36%, mostly 7-25% — clean |
| **BTC 1H** | 12 / 12 | +0.066R (PF 1.11) | one window 99% — that window is fake |
| **GOLD 1H** | **8 / 10** | **-0.16R (PF 0.78)** | last window 72% — outlier-driven |

**ETH 1H is the cleanest.** Every window positive, no window carried by a single
trade.

**BTC 1H is 12/12 but not clean** — window 3000-4500 shows +0.066R with one trade
= 99% of that window's P&L. Treat that stretch as flat, not profitable.

**GOLD 1H is the weakest — and it is the market that matters most.** Two windows
are outright negative (3500-5000: -0.038R PF 0.94; 4000-5500: -0.16R PF 0.78) and
those are the *recent* windows. The final window (4500-6000) is positive only
because one trade is 72% of it. So gold 1H has a real losing stretch in recent
data and is outlier-dependent at the end.

**Do NOT trade gold with this model without further work.** It needs either a
regime filter (trade only when the higher-timeframe is trending) or a different
model entirely for gold.

**Does NOT work on GOLD 15m.** The full-sample number looks good (+89R, PF 2.14)
but it is a mirage: **one trade is 59% of the entire P&L**, and the first half is
barely positive (+0.145R, PF 1.23). Ten of twelve parameter variants fail the
out-of-sample test at 15m. Do not trade this model on gold 15m.

## Robustness — parameter neighbourhood

Each knob was nudged and the model re-run. An edge that exists at only one exact
setting is curve-fit and worthless.

**12 of 12 variants pass** on GOLD 1H, BTC 1H and ETH 1H — every value of
`disp_mult`, `min_pierce_atr`, `min_rr`, `confirm_window`, `entry_valid`,
`stop_buffer_atr`, the premium/discount filter and the pivot strength stays
positive in both halves.

On GOLD 15m only 2 of 12 pass, and those two are marginal.

The defaults shipped in the indicator are the values chosen **before** seeing any
data, not the best-performing row from the sweep. Picking the best row would be
curve-fitting.

## Frequency — this is not a scalper

Roughly **3 signals per 100 bars**, i.e. about 3 setups every 4 days on 1H.
It is an intraday/swing model. It will not produce 20-50 signals a day. Tuning it
to fire that often is exactly what destroys the edge.

## Files

- `engine/ict.py` — the model (pivots, sweep, displacement, MSS, FVG entry,
  stop, targets) plus the fill simulator and stats
- `backtest_ict.py` — paginated history fetch + market matrix
- `robustness.py` — parameter neighbourhood + out-of-sample split + distribution
- `gold_check.py` — 12 variants tested on gold, out-of-sample
- `final_numbers.py` — the table above
- `ict_model.pine` — the TradingView port (validated against TradingView's compiler)
