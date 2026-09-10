#!/usr/bin/env python3
"""Discover proof-fuzzing strategies with a persistent mutation agent."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.proof_fuzzer.persistent_fuzzing import main

if __name__ == '__main__':
    main()
