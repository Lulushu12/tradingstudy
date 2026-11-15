"""Rebuild all data from scratch, reproducibly: download, clean, repair, clean again, resample, QA.

Usage: uv run python -m tradingstudy.data.pipeline
Raw downloads are cached and checksum-verified, so re-running only fetches what is missing.
Repair runs twice: the first pass can expose new gap days (from dropped frozen minutes) whose daily archives
contain real data, and those daily files can themselves contain frozen minutes.
"""
from tradingstudy.config import SYMBOLS
from tradingstudy.data import clean, download, qa, repair, resample


def main() -> None:
    download.main(SYMBOLS)
    clean.main(SYMBOLS)
    for _ in range(2):
        repair.main(SYMBOLS)
        clean.main(SYMBOLS)
    resample.main(SYMBOLS)
    qa.main()


if __name__ == "__main__":
    main()
