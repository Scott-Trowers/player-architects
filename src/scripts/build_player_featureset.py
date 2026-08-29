"""
Builds the player featureset standalone, without running the EDA notebook.

Reproduces the cleaning, aggregation, per-90 normalisation, feature engineering, and
column pruning performed in notebooks/season2122_eda.ipynb, so the featureset can be
regenerated on demand. See docs/eda-findings.md for the reasoning behind each
column-group decision.

Usage:
    python -m scripts.build_player_featureset
    python -m scripts.build_player_featureset path/to/input.csv path/to/output.csv
"""

import argparse
from pathlib import Path

from scripts.featureset.pipeline import build_featureset

REPO_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DATA_DIR = REPO_ROOT / 'data' / 'processed'

DEFAULT_INPUT_CSV = PROCESSED_DATA_DIR / '2021-2022 Football Player Stats.csv'
DEFAULT_OUTPUT_CSV = PROCESSED_DATA_DIR / 'player_featureset.csv'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input_csv', nargs='?', type=Path, default=DEFAULT_INPUT_CSV)
    parser.add_argument('output_csv', nargs='?', type=Path, default=DEFAULT_OUTPUT_CSV)
    args = parser.parse_args()

    featureset = build_featureset(args.input_csv)

    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    featureset.to_csv(args.output_csv, index=False)
    print(f"Wrote player featureset ({featureset.shape[0]} players, {featureset.shape[1]} columns) to {args.output_csv}")


if __name__ == '__main__':
    main()
