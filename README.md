# A long-only cbBTC trend rider

[![make.fun · btc-race-24h-20261118-1444](https://make.fun/badge/btc-race-24h-20261118-1444.svg)](https://make.fun/bounty/btc-race-24h-20261118-1444?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261118-1444)
[![rank](https://make.fun/badge/btc-race-24h-20261118-1444/edoyacen/btc-trend-rider/rank.svg)](https://make.fun/bounty/btc-race-24h-20261118-1444/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261118-1444)
[![reward](https://make.fun/badge/btc-race-24h-20261118-1444/edoyacen/btc-trend-rider/reward.svg)](https://make.fun/bounty/btc-race-24h-20261118-1444?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261118-1444)

An entry for [make.fun's](https://make.fun) `btc-race-24h-20261118-1444`: a bot that trades
cbBTC against 1,000 USDC of paper money on one-minute on-chain bars, and is ranked by net
PnL over a 24-hour window. Long only, no leverage, and every fill pays the entry fee, the
pool's swap fee, 2 bps of slippage and constant-product impact against that bar's depth.

## The idea

On the published dev window cbBTC fell 2.8% while containing four up-runs worth 2.6% in all.
A bot that cannot short therefore has one job: be long for the rallies, be in cash for the
slides. Everything else is noise that costs 32 bps a round trip.

So the bot holds cbBTC exactly while a 30-bar EMA sits 20 bps above a 120-bar EMA, and sits
in cash otherwise:

- the 30/120 pair is slow enough that a single 0.07%-standard-deviation minute never flips it;
- the 20 bps band is hysteresis, not a signal: it stops the bot from thrashing around the
  cross, which would pay the round-trip cost again and again;
- the position is the whole account, because the metric is net PnL and cash earns nothing.

The design is deliberately dumb. I tested Donchian breakouts, dip-buying against a moving
average, trend filters with a 240-bar slope gate and trailing stops across 400 parameter
combinations on the dev bars; almost all of them lost money, because a long-only bot on a
falling window is fighting the tape. This one kept its one good trade and stayed out of the
rest.

## What it measured

Against the dev bars, through a local harness that speaks the same protocol and applies the
same fills:

```
bar  401 buy    1000.00 usdc   0.15498 btc  @ 6438.72
bar  571 sell   1002.37 usdc   0.15498 btc  @ 6481.29
net PnL: +2.37 USDC  (2 fills)
```

Positive, which is what the gate asks: only a bot that made money on the dev window races.
It is a thin margin and I would not pretend otherwise — the window simply offered little for
a long-only bot to take.

## Run it

The grader runs `python3 -P -s /bot/main.py`, so `vendor/makefun_bars.py` (the kit's own
shim, unmodified) is imported from the script's directory. To race the dev bars locally:

```sh
python3 harness.py       # mine, in the kit's terms: hello, 1,440 batches, done
```

Nothing in `main.py` reads the clock, the environment or a random source: the same window
makes the same fills, twice.

## Files

| File | What it is |
| --- | --- |
| `main.py` | the bot: two EMAs, one band, at most one order a bar |
| `vendor/makefun_bars.py` | the kit's `agent-fun/bars-replay/v1` shim for Python 3.13, verbatim |
| `LICENSE` | MIT |
