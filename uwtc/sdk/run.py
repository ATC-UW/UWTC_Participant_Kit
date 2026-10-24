"""Run a strategy file against the exchange.

    python -m uwtc.sdk.run competitor_strategy.py --url ws://HOST:8000/ws --key API_KEY

``--url`` / ``--key`` default to the ``UWTC_URL`` / ``UWTC_API_KEY`` environment
variables. The file must define ``class Strategy(BaseStrategy)`` (or exactly
one ``BaseStrategy`` subclass); pass ``--class`` to pick another name.

``--offline --round N`` runs a local simulation instead; this needs the full
server package (organisers only) and is unavailable in the team SDK.
"""

from __future__ import annotations

import argparse
import importlib.util
import inspect
import logging
import os
import sys
from pathlib import Path

from .base import BaseStrategy


def load_strategy_class(path: str | os.PathLike, class_name: str | None = None) -> type[BaseStrategy]:
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"strategy file not found: {p}")
    spec = importlib.util.spec_from_file_location("competitor_strategy", p)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {p}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["competitor_strategy"] = module
    spec.loader.exec_module(module)
    if class_name:
        cls = getattr(module, class_name, None)
        if not (inspect.isclass(cls) and issubclass(cls, BaseStrategy)):
            raise TypeError(f"{class_name} is not a BaseStrategy subclass in {p}")
        return cls
    cls = getattr(module, "Strategy", None)
    if inspect.isclass(cls) and issubclass(cls, BaseStrategy):
        return cls
    found = [c for _, c in inspect.getmembers(module, inspect.isclass)
             if issubclass(c, BaseStrategy) and c is not BaseStrategy and c.__module__ == module.__name__]
    if len(found) != 1:
        raise TypeError(f"{p} must define class Strategy(BaseStrategy) (found {len(found)} candidates)")
    return found[0]


def _offline(cls: type[BaseStrategy], args: argparse.Namespace) -> int:
    try:
        from uwtc.config import load_round_config
        from uwtc.engine.simulator import simulate
        from uwtc.strategies import make_strategies
    except ImportError:
        print("--offline needs the full uwtc server package; connect to the practice server instead.",
              file=sys.stderr)
        return 2
    cfg = load_round_config(args.round)
    if args.seed is not None:
        cfg = cfg.model_copy(update={"seed": args.seed})
    strategies = {"you": cls()}
    if args.opponents:
        strategies.update(make_strategies([o for o in args.opponents.split(",") if o], cfg))
    results, _ = simulate(cfg, strategies)
    for r in sorted(results.values(), key=lambda r: r["rank"]):
        print(f"{r['rank']:>3} {r['team']:<16} pnl ${r['pnl'] / 100:>12,.2f}  fees ${r['fees'] / 100:>9,.2f}  "
              f"volume {r['volume']:>8}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m uwtc.sdk.run", description=__doc__.split("\n\n")[0])
    ap.add_argument("strategy", help="path to competitor_strategy.py")
    ap.add_argument("--url", default=os.environ.get("UWTC_URL", "ws://localhost:8000/ws"))
    ap.add_argument("--key", default=os.environ.get("UWTC_API_KEY"), help="team API key (or UWTC_API_KEY)")
    ap.add_argument("--class", dest="class_name", default=None)
    ap.add_argument("--log-level", default=os.environ.get("UWTC_LOG_LEVEL", "INFO"))
    ap.add_argument("--no-reconnect", action="store_true")
    ap.add_argument("--stay", action="store_true", help="keep running after the session finishes")
    ap.add_argument("--offline", action="store_true", help="local simulation (organisers only)")
    ap.add_argument("--round", type=int, default=1)
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--opponents", default="example,random")
    args = ap.parse_args(argv)
    logging.basicConfig(level=args.log_level.upper(), format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    cls = load_strategy_class(args.strategy, args.class_name)
    if args.offline:
        return _offline(cls, args)
    if not args.key:
        ap.error("an API key is required (--key or UWTC_API_KEY)")
    from .client import run_strategy

    client = run_strategy(cls(), args.url, args.key, reconnect=not args.no_reconnect,
                          exit_when_finished=not args.stay)
    if client.stop_reason:
        print(f"stopped: {client.stop_reason}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
