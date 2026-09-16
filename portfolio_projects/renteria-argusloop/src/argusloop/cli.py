from __future__ import annotations

import argparse
import json

from .agent import run


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Renteria ArgusLoop vision agent")
    parser.add_argument("task", help="Plain-English task to perform")
    args = parser.parse_args()
    records = run(args.task)
    print(json.dumps([r.model_dump(mode="json") for r in records], indent=2))


if __name__ == "__main__":
    main()

