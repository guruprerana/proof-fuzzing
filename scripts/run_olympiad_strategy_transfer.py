#!/usr/bin/env python3
"""Run problem-disjoint Olympiad strategy discovery and transfer evaluation."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.proof_fuzzer.olympiad_transfer import main

if __name__ == '__main__':
    main()
