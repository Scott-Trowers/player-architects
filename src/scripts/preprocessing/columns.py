"""
Column definitions, metadata classifications, and feature separation utilities.

Ported from notebooks/season2122_transformation_and_scaling.ipynb. Defines the
descriptive metadata features, the zero-inflated and rare features retired from active
modelling into metadata, and provides helper functions to split the feature set.
"""

import warnings
from collections.abc import Sequence

import numpy as np
import pandas as pd

from scripts.featureset.columns import DESCRIPTIVE_COLS, LEAGUE_PCT_MINS_COLS

ID_COL = 'player_identifier'

__all__ = [
    'COLS_TO_METADATA',
    'DESCRIPTIVE_COLS',
    'ID_COL',
    'LEAGUE_PCT_MINS_COLS',
    'separate_features_and_metadata',
]

# ASSUMPTION: these are too rare or zero-inflated to be reliable over one season, even after
# Yeo-Johnson, so they'd dominate dimension reduction and clustering. each is either replaced
# by an engineered feature or already covered by a more common metric. raw values are kept in
# metadata so they can be re-explored in a future per-position (stratified) model
COLS_TO_METADATA: list[str] = [
    # card components subsumed into card_points_p90
    'CrdY_p90',
    'CrdR_p90',
    '2CrdY_p90',
    # set-piece raw volume converted to binary indicators
    'ShoPK_p90',
    'ShoFK_p90',
    # too rare to separate a real pattern from bad luck over 1 season
    'OG_p90',
    # negative outcomes covered by CarMis, CarDis, PasPress, TouDefPen, Fls and TklDri metrics
    'Err_p90',
    'PKcon_p90',
    # goal-creating components covered by the Sca (shot-creating) equivalents and broader GCA
    'GcaDef_p90',
    'GcaPassDead_p90',
    'GcaDrib_p90',
    'GcaFld_p90',
    # position-specific outliers covered by blocks/clearances and penalty box touches/carries
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

    Warns
    -----
    UserWarning
        If any expected metadata columns are missing from df.
    """
    if metadata_cols is None:
        metadata_cols = DESCRIPTIVE_COLS

    present_meta = [col for col in metadata_cols if col in df.columns]
    missing_meta = [col for col in metadata_cols if col not in df.columns]
    # a renamed or dropped descriptive column would otherwise vanish without anyone noticing
    if missing_meta:
        warnings.warn(
            f"Expected metadata columns missing from input: {missing_meta}",
            UserWarning,
            stacklevel=2,
        )

    feature_cols = [col for col in df.columns if col not in present_meta]

    metadata_df = df[present_meta].copy()
    X = df[feature_cols].copy()

    non_numeric = X.select_dtypes(exclude=[np.number]).columns.tolist()
    if non_numeric:
        raise ValueError(f"Non-numeric columns found in feature matrix: {non_numeric}")

    return metadata_df, X
