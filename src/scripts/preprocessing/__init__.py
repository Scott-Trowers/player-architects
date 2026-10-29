"""
Preprocessing package for player archetype modelling pipeline.

Provides feature/metadata separation, power transformations, domain sparsity
engineering, feature scaling, and pipeline orchestration.
"""

from scripts.preprocessing.columns import (
    COLS_TO_METADATA,
    DESCRIPTIVE_COLS,
    ID_COL,
    LEAGUE_PCT_MINS_COLS,
    separate_features_and_metadata,
)
from scripts.preprocessing.pipeline import (
    PreprocessingArtifacts,
    build_preprocessing_pipeline,
    preprocess_modelling_pipeline,
)
from scripts.preprocessing.scale import DataFrameScaler, build_scaler
from scripts.preprocessing.transform import (
    ENGINEERED_COLS,
    DomainFeatureEngineer,
    YeoJohnsonTransformer,
    detect_skewed_features,
    engineer_card_points,
    engineer_set_piece_takers,
    retire_sparse_features,
)

__all__ = [
    'COLS_TO_METADATA',
    'DESCRIPTIVE_COLS',
    'ENGINEERED_COLS',
    'ID_COL',
    'LEAGUE_PCT_MINS_COLS',
    'DataFrameScaler',
    'DomainFeatureEngineer',
    'PreprocessingArtifacts',
    'YeoJohnsonTransformer',
    'build_preprocessing_pipeline',
    'build_scaler',
    'detect_skewed_features',
    'engineer_card_points',
    'engineer_set_piece_takers',
    'preprocess_modelling_pipeline',
    'retire_sparse_features',
    'separate_features_and_metadata',
]
