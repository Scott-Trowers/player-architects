"""
Preprocesses the player featureset for unsupervised modelling standalone.

Reproduces the transformation, zero-inflation handling, column retirement, and scaling
pipeline developed in notebooks/season2122_transformation_and_scaling.ipynb.

Produces three artefacts in the destination directory:
    - player_features_scaled.csv: player_identifier plus the standardised numeric performance
      feature matrix for modelling.
    - player_metadata.csv: Descriptive identity, context, and retired feature matrix.
    - player_featureset_preprocessed.csv: Combined metadata and scaled features.

Usage:
    python -m scripts.preprocess_modelling_features
    python -m scripts.preprocess_modelling_features --input-csv path/to/player_featureset.csv --output-dir path/to/output_dir
"""

import argparse
from pathlib import Path

import pandas as pd

from scripts.preprocessing.pipeline import preprocess_modelling_pipeline

REPO_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DATA_DIR = REPO_ROOT / 'data' / 'processed'

DEFAULT_INPUT_CSV = PROCESSED_DATA_DIR / 'player_featureset.csv'


def main():
    """Reads the player featureset, prepares it for modelling, and saves the results as CSVs."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--input-csv',
        type=Path,
        default=DEFAULT_INPUT_CSV,
        help='Path to the input featureset CSV (default: data/processed/player_featureset.csv).',
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=PROCESSED_DATA_DIR,
        help='Directory to write preprocessed CSVs to (default: data/processed/).',
    )
    parser.add_argument(
        '--scaler',
        type=str,
        default='standard',
        choices=['standard', 'robust'],
        help='Scaler type to apply (default: standard).',
    )
    args = parser.parse_args()

    if not args.input_csv.exists():
        raise FileNotFoundError(f"Input featureset not found: {args.input_csv}")

    df = pd.read_csv(args.input_csv)
    print(f"Loaded featureset from {args.input_csv} ({df.shape[0]} players, {df.shape[1]} columns)")

    artifacts = preprocess_modelling_pipeline(df, scaler_type=args.scaler)

    args.output_dir.mkdir(parents=True, exist_ok=True)

    scaled_path = args.output_dir / 'player_features_scaled.csv'
    metadata_path = args.output_dir / 'player_metadata.csv'
    combined_path = args.output_dir / 'player_featureset_preprocessed.csv'

    scaled_with_id = artifacts.X_scaled_with_id
    scaled_with_id.to_csv(scaled_path, index=False)
    print(f"Wrote scaled features ({scaled_with_id.shape[0]} players, {scaled_with_id.shape[1]} columns) to {scaled_path}")

    artifacts.metadata_df.to_csv(metadata_path, index=False)
    print(f"Wrote metadata ({artifacts.metadata_df.shape[0]} players, {artifacts.metadata_df.shape[1]} columns) to {metadata_path}")

    artifacts.full_preprocessed_df.to_csv(combined_path, index=False)
    print(f"Wrote combined preprocessed featureset ({artifacts.full_preprocessed_df.shape[0]} players, {artifacts.full_preprocessed_df.shape[1]} columns) to {combined_path}")


if __name__ == '__main__':
    main()
