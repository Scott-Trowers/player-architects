"""
Column definitions, metadata classifications, and feature separation utilities.

Ported from notebooks/season2122_transformation_and_scaling.ipynb. Defines the
descriptive metadata features, the zero-inflated and rare features retired from active
modelling into metadata, and provides helper functions to split the feature set.
"""

from collections.abc import Sequence

import numpy as np
import pandas as pd

LEAGUE_PCT_MINS_COLS: list[str] = [
    'Premier League_pct_mins',
    'Ligue 1_pct_mins',
    'Bundesliga_pct_mins',
    'Serie A_pct_mins',
    'La Liga_pct_mins',
]

DESCRIPTIVE_COLS: list[str] = [
    'player_identifier',
    'Player',
    'Nation',
    'Age',
    'Pos',
    'Primary_Pos',
    'Num_Pos',
    'Squad',
    'Comp',
    'passing_foot_pref',
    'signed_preference_score',
    *LEAGUE_PCT_MINS_COLS,
]

COLS_TO_METADATA: list[str] = [
    # Card components subsumed into card_points_p90
    'CrdY_p90',
    'CrdR_p90',
    '2CrdY_p90',
    # Set-piece raw volume converted to binary indicators
    'ShoPK_p90',
    'ShoFK_p90',
    # Stochastic noise over 1 season
    'OG_p90',
    # Negative outcomes covered by continuous ball security & foul/duel rates
    'Err_p90',
    'PKcon_p90',
    # Goal-creating components covered by Sca equivalents & broader GCA
    'GcaDef_p90',
    'GcaPassDead_p90',
    'GcaDrib_p90',
    'GcaFld_p90',
    # Positional extreme outliers covered by clearances/blocks and box entries
    'BlkShSv_p90',
    'PKwon_p90',
]


def separate_features_and_metadata(
    df: pd.DataFrame,
    metadata_cols: Sequence[str] | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Separates metadata/descriptive columns from numeric performance features.

    Parameters
    ----------
    df : pd.DataFrame
        Full player featureset containing descriptive and performance columns.
    metadata_cols : Sequence[str] | None
        List of metadata column names. If None, defaults to DESCRIPTIVE_COLS.

    Returns
    -------
    tuple[pd.DataFrame, pd.DataFrame]
        A tuple of (metadata_df, X_raw) where metadata_df contains present
        metadata columns and X_raw contains purely numeric performance features.

    Raises
    ------
    ValueError
        If any non-numeric columns remain in X_raw.
    """
    if metadata_cols is None:
        metadata_cols = DESCRIPTIVE_COLS

    present_meta = [col for col in metadata_cols if col in df.columns]
    feature_cols = [col for col in df.columns if col not in present_meta]

    metadata_df = df[present_meta].copy()
    X = df[feature_cols].copy()

    non_numeric = X.select_dtypes(exclude=[np.number]).columns.tolist()
    if non_numeric:
        raise ValueError(f"Non-numeric columns found in feature matrix: {non_numeric}")

    return metadata_df, X
