"""A long-only cbBTC trend rider for the btc-race bars replay.

The bot holds cbBTC only while a fast EMA sits clearly above a slow one, and sits in cash
otherwise: on a falling window that keeps it out of the drawdowns the dev window was full of,
and it still takes the multi-hour rallies whole. The band around the cross is wide enough
(0.2%) that the bot does not thrash, because every round trip pays roughly 40 bps between the
entry fee, the pool fee, the slippage and constant-product impact.

Decisions are a function of the bars alone: no clock, no environment, no randomness, so two
runs of the same window make the same fills.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))

import makefun_bars  # noqa: E402

SYMBOL = "CBBTC"
BAND = 0.002
FAST, SLOW = 30, 120
MAX_SLIP_BPS = 100


class Rider:
    """The bot's whole state: two EMAs over the closes it has been sent."""

    def __init__(self):
        self.fast = None
        self.slow = None
        self.last_close = None
        self.seen = 0

    def observe(self, close):
        if self.last_close == close:
            return
        self.last_close = close
        self.seen += 1
        if self.fast is None:
            self.fast = self.slow = float(close)
            return
        for name, span in (("fast", FAST), ("slow", SLOW)):
            k = 2.0 / (span + 1)
            setattr(self, name, close * k + getattr(self, name) * (1 - k))

    @property
    def wants_long(self):
        if self.fast is None or self.seen < SLOW:
            return False
        return self.fast > self.slow * (1 + BAND)


RIDER = Rider()


def on_hello(state):
    RIDER.__init__()


def on_batch(state, batch):
    close = state.close(SYMBOL)
    if close is None:
        return []
    RIDER.observe(close)
    if state.warming_up:
        return []

    held = state.positions.get(SYMBOL)
    qty = held.qty if held else 0
    if RIDER.wants_long and qty == 0:
        room = state.cash
        if "max_weight_bps" in (state.hello.get("caps") or {}):
            room = min(room, state.weight_room(SYMBOL))
        spend = room
        if spend < 1_000_000:
            return []
        return [
            {
                "side": "buy",
                "symbol": SYMBOL,
                "notional_quote_units": spend,
                "max_slippage_bps": MAX_SLIP_BPS,
            }
        ]
    if not RIDER.wants_long and qty > 0:
        return [
            {"side": "sell", "symbol": SYMBOL, "qty": qty, "max_slippage_bps": MAX_SLIP_BPS}
        ]
    return []


if __name__ == "__main__":
    makefun_bars.run(on_batch, on_hello=on_hello)
