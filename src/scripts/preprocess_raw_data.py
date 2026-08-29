"""
Reverts the source data's already-per-90 columns back to raw counts.

FBref's raw export divides most count columns by 90s before you ever see them,
which breaks aggregation (you can't sum two per-90 rates) and would double-normalise
if divided by 90s again downstream. This restores raw counts so notebooks can
aggregate correctly and normalise per-90 themselves, exactly once.

Usage:
    python -m scripts.preprocess_raw_data
    python -m scripts.preprocess_raw_data path/to/input.csv path/to/output.csv
"""

import argparse
from pathlib import Path

import pandas as pd

from scripts.constants import PER90_COUNT_COLUMNS

REPO_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = REPO_ROOT / 'data' / 'raw'
PROCESSED_DATA_DIR = REPO_ROOT / 'data' / 'processed'

CSV_READ_KWARGS = {'sep': ';', 'encoding': 'latin1'}


def convert_per90_to_counts(df, columns=PER90_COUNT_COLUMNS, matches_col='90s'):
    df = df.copy()
    present_columns = [col for col in columns if col in df.columns]
    missing_columns = sorted(set(columns) - set(present_columns))
    if missing_columns:
        print(f"WARNING: expected per-90 columns not found in source, skipping: {missing_columns}")

    df[present_columns] = df[present_columns].mul(df[matches_col], axis=0).round().astype('Int64')
    return df


def preprocess_file(input_path, output_path):
    df = pd.read_csv(input_path, **CSV_READ_KWARGS)
    df = convert_per90_to_counts(df)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, **CSV_READ_KWARGS)
    print(f"Wrote raw counts to {output_path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input_csv', nargs='?', type=Path, help='Source CSV. If omitted, every CSV in data/raw is processed.')
    parser.add_argument('output_csv', nargs='?', type=Path, help='Destination CSV. Required if input_csv is given.')
    args = parser.parse_args()

    if args.input_csv:
        if not args.output_csv:
            parser.error('output_csv is required when input_csv is given')
        preprocess_file(args.input_csv, args.output_csv)
        return

    for input_path in sorted(RAW_DATA_DIR.glob('*.csv')):
        preprocess_file(input_path, PROCESSED_DATA_DIR / input_path.name)


if __name__ == '__main__':
    main()
