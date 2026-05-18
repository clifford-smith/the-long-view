"""
The Long View — AI Radio Station
Entry point.

Usage:
  python main.py --generate <slot>    Generate a single segment immediately
  python main.py --schedule           Run the full automated scheduler
"""
from __future__ import annotations
import argparse
import logging
import logging.handlers
import sys


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.handlers.RotatingFileHandler(
            "the_long_view.log", maxBytes=5_000_000, backupCount=3
        ),
    ],
)

_VALID_SLOTS = {
    "morning_drift", "the_stack", "midday",
    "deep_cuts", "drive", "night_school", "archive",
}


def main() -> None:
    parser = argparse.ArgumentParser(description="The Long View — AI Radio Station")
    parser.add_argument(
        "--generate",
        metavar="SLOT",
        choices=_VALID_SLOTS,
        help=f"Generate a single segment immediately. Valid slots: {', '.join(sorted(_VALID_SLOTS))}",
    )
    parser.add_argument(
        "--schedule",
        action="store_true",
        help="Run the full automated scheduler (blocks forever)",
    )
    args = parser.parse_args()

    if args.generate:
        from stream.scheduler import generate_slot
        generate_slot(args.generate)
    elif args.schedule:
        from stream.scheduler import run_scheduler
        run_scheduler()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
