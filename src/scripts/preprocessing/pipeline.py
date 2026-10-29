"""
End-to-end preprocessing pipeline for player archetype modeling.

Orchestrates the complete transformation and scaling workflow, reproducing the
methodology established in notebooks/season2122_transformation_and_scaling.ipynb,
as a scikit-learn Pipeline so every learned setting lives in one fitted object.
"""

from collections.abc import Sequence
from dataclasses import dataclass

import pandas as pd
from sklearn.pipeline import Pipeline

from scripts.preprocessing.columns import (
    COLS_TO_METADATA,
    ID_COL,
    separate_features_and_metadata,
)
from scripts.preprocessing.scale import DEFAULT_SCALER_TYPE, DataFrameScaler
from scripts.preprocessing.transform import (
    DEFAULT_SKEW_THRESHOLD,
    DEFAULT_TAKER_PCT,
    ENGINEERED_COLS,
    DomainFeatureEngineer,
    YeoJohnsonTransformer,
    retire_sparse_features,
)


def build_preprocessing_pipeline(
    scaler_type: str = DEFAULT_SCALER_TYPE,
    skew_threshold: float = DEFAULT_SKEW_THRESHOLD,
    cols_to_retire: Sequence[str] = COLS_TO_METADATA,
    pk_pct: float = DEFAULT_TAKER_PCT,
    fk_pct: float = DEFAULT_TAKER_PCT,
) -> Pipeline:
    """
    Builds the (unfitted) chain of preprocessing steps, in the order they must run.

    1. engineer: adds card score and set-piece taker flags from raw values, drops rare columns.
    2. reshape: Yeo-Johnson transforms any remaining column with |skew| > skew_threshold.
    3. scale: puts every column on the same scale.

    Parameters
    ----------
    scaler_type : str
        Scaling strategy ('standard' or 'robust').
    skew_threshold : float
        Absolute skewness threshold for applying Yeo-Johnson transformation.
    cols_to_retire : Sequence[str]
        Low-frequency/sparse columns to remove from the model features.
    pk_pct : float
        Percentile among penalty shot takers needed to count as a designated taker.
    fk_pct : float
        Percentile among free kick shot takers needed to count as a designated taker.

    Returns
    -------
    Pipeline
        A scikit-learn Pipeline that hasn't learned anything yet.
    """
    return Pipeline([
        # runs first so the card score and taker cut-offs come from real per-90 values
        ('engineer', DomainFeatureEngineer(pk_pct=pk_pct, fk_pct=fk_pct, cols_to_retire=cols_to_retire)),
        # card_points_p90 is already reshaped by its own transformer, and the 0/1 taker flags
        # must stay binary, so neither is reshaped a second time
        ('reshape', YeoJohnsonTransformer(skew_threshold=skew_threshold, exclude=ENGINEERED_COLS)),
        # ASSUMPTION: the binary taker flags are scaled alongside everything else, as in the
        # notebook. this gives them a large spread relative to their meaning, so they may carry
        # outsized weight in distance-based clustering and are worth revisiting at modelling
        ('scale', DataFrameScaler(scaler_type=scaler_type)),
    ])


@dataclass
class PreprocessingArtifacts:
    """Container holding the pipeline's outputs and the fitted pipeline itself."""

    metadata_df: pd.DataFrame
    X_transformed: pd.DataFrame
    X_scaled: pd.DataFrame
    pipeline: Pipeline

    @property
    def full_preprocessed_df(self) -> pd.DataFrame:
        """Combines metadata and scaled modelling features into a single DataFrame."""
        return pd.concat([self.metadata_df, self.X_scaled], axis=1)

    @property
    def X_scaled_with_id(self) -> pd.DataFrame:
        """Scaled modelling features with the player identifier as the first column."""
        # keeps a join key in the saved file so model outputs never depend on row order
        return pd.concat([self.metadata_df[[ID_COL]], self.X_scaled], axis=1)


def preprocess_modelling_pipeline(
    df: pd.DataFrame,
    scaler_type: str = DEFAULT_SCALER_TYPE,
    skew_threshold: float = DEFAULT_SKEW_THRESHOLD,
    metadata_cols: Sequence[str] | None = None,
    cols_to_retire: Sequence[str] = COLS_TO_METADATA,
) -> PreprocessingArtifacts:
    """
    Separates metadata, then fits and applies the preprocessing pipeline to a player featureset.

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
        Dataclass containing metadata_df, X_transformed, X_scaled, and the fitted pipeline.
    """
    metadata_df, X_raw = separate_features_and_metadata(df, metadata_cols=metadata_cols)

    # retired columns are copied from the raw data so metadata keeps real, readable values
    _, metadata_df = retire_sparse_features(X_raw, metadata_df=metadata_df, cols_to_retire=cols_to_retire)

    # ASSUMPTION: v1 re-fits on every season passed in, so archetypes describe a player relative
    # to their own season. v2 should fit once on several seasons pooled together, giving stable
    # yardsticks for placing new players and comparing seasons (see docs/project-plan.md)
    pipeline = build_preprocessing_pipeline(
        scaler_type=scaler_type,
        skew_threshold=skew_threshold,
        cols_to_retire=cols_to_retire,
    )
    X_scaled = pipeline.fit_transform(X_raw)
    # every step except the final scaler, for inspecting values before scaling
    X_transformed = pipeline[:-1].transform(X_raw)

    return PreprocessingArtifacts(
        metadata_df=metadata_df,
        X_transformed=X_transformed,
        X_scaled=X_scaled,
        pipeline=pipeline,
    )
