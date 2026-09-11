#!/usr/bin/env python3
"""Evaluate a frozen strategy library against generic mutation instructions."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from src.archive.proof_fuzzer.matched_strategy_pilot import main

if __name__ == '__main__':
    main()
