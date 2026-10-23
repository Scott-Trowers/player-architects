"""
End-to-end preprocessing pipeline for player archetype modeling.

Orchestrates the complete transformation and scaling workflow, reproducing the
methodology established in notebooks/season2122_transformation_and_scaling.ipynb.
"""

from collections.abc import Sequence
from dataclasses import dataclass

import pandas as pd
from sklearn.preprocessing import PowerTransformer, RobustScaler, StandardScaler

from scripts.preprocessing.columns import (
    COLS_TO_METADATA,
    separate_features_and_metadata,
)
from scripts.preprocessing.scale import scale_features
from scripts.preprocessing.transform import (
    detect_skewed_features,
    engineer_card_points,
    engineer_set_piece_takers,
    power_transform_features,
    retire_sparse_features,
)


@dataclass
class PreprocessingArtifacts:
    """Container holding outputs and stateful fitted estimators from the pipeline."""

    metadata_df: pd.DataFrame
    X_transformed: pd.DataFrame
    X_scaled: pd.DataFrame
    skewed_cols: list[str]
    pt_skewed: PowerTransformer
    pt_cards: PowerTransformer
    pk_threshold: float
    fk_threshold: float
    scaler: StandardScaler | RobustScaler

    @property
    def full_preprocessed_df(self) -> pd.DataFrame:
        """Combines metadata and scaled modelling features into a single DataFrame."""
        return pd.concat([self.metadata_df, self.X_scaled], axis=1)


def preprocess_modelling_pipeline(
    df: pd.DataFrame,
    scaler_type: str = 'standard',
    skew_threshold: float = 1.0,
    metadata_cols: Sequence[str] | None = None,
    cols_to_retire: Sequence[str] = COLS_TO_METADATA,
) -> PreprocessingArtifacts:
    """
    Executes the end-to-end transformation and scaling pipeline on a player featureset.

    1. Separates metadata columns from numeric performance features.
    2. Identifies features with |skew| > skew_threshold and applies Yeo-Johnson power transformation.
    3. Engineers UEFA Fair Play composite card score (CrdY_p90 + 3*CrdR_p90) and power-transforms it.
    4. Binarizes penalty and free kick shot volumes into taker flags (is_pk_taker, is_fk_taker).
    5. Retires rare-event / zero-inflated features from the active modeling matrix into metadata.
    6. Standardizes feature scales using StandardScaler (or RobustScaler).

    Parameters
    ----------
    df : pd.DataFrame
        Input featureset DataFrame (e.g. loaded from player_featureset.csv).
    scaler_type : str
        Scaling strategy ('standard' or 'robust'). Defaults to 'standard'.
    skew_threshold : float
        Absolute skewness threshold for applying Yeo-Johnson transformation.
    metadata_cols : Sequence[str] | None
        Custom metadata columns. If None, defaults to DESCRIPTIVE_COLS.
    cols_to_retire : Sequence[str]
        List of low-frequency/sparse columns to move from features to metadata.

    Returns
    -------
    PreprocessingArtifacts
        Dataclass containing metadata_df, X_transformed, X_scaled, and fitted estimators.
    """
    # 1. Separate metadata from performance metrics
    metadata_df, X_raw = separate_features_and_metadata(df, metadata_cols=metadata_cols)

    # 2. Power transform skewed performance features
    skewed_cols = detect_skewed_features(X_raw, threshold=skew_threshold)
    X_transformed, pt_skewed = power_transform_features(
        X_raw,
        columns=skewed_cols,
        method='yeo-johnson',
    )

    # 3. Domain feature engineering from raw values
    card_points_series, pt_cards = engineer_card_points(X_raw)
    X_transformed['card_points_p90'] = card_points_series

    indicators, pk_threshold, fk_threshold = engineer_set_piece_takers(X_raw)
    X_transformed['is_pk_taker'] = indicators['is_pk_taker']
    X_transformed['is_fk_taker'] = indicators['is_fk_taker']

    # 4. Retire low-frequency/zero-inflated columns to metadata
    X_transformed, metadata_df = retire_sparse_features(
        X_transformed,
        metadata_df=metadata_df,
        cols_to_retire=cols_to_retire,
    )

    # 5. Scale features
    X_scaled, scaler = scale_features(X_transformed, scaler_type=scaler_type)

    return PreprocessingArtifacts(
        metadata_df=metadata_df,
        X_transformed=X_transformed,
        X_scaled=X_scaled,
        skewed_cols=skewed_cols,
        pt_skewed=pt_skewed,
        pt_cards=pt_cards,
        pk_threshold=pk_threshold,
        fk_threshold=fk_threshold,
        scaler=scaler,
    )
