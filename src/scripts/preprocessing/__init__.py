"""
Preprocessing package for player archetype modelling pipeline.

Provides feature/metadata separation, power transformations, domain sparsity
engineering, feature scaling, and pipeline orchestration.
"""

from scripts.preprocessing.columns import (
    COLS_TO_METADATA,
    DESCRIPTIVE_COLS,
    LEAGUE_PCT_MINS_COLS,
    separate_features_and_metadata,
)
from scripts.preprocessing.pipeline import (
    PreprocessingArtifacts,
    preprocess_modelling_pipeline,
)
from scripts.preprocessing.scale import DataFrameScaler, scale_features
from scripts.preprocessing.transform import (
    DomainSparsityTransformer,
    YeoJohnsonTransformer,
    detect_skewed_features,
    engineer_card_points,
    engineer_set_piece_takers,
    power_transform_features,
    retire_sparse_features,
)

__all__ = [
    'COLS_TO_METADATA',
    'DESCRIPTIVE_COLS',
    'LEAGUE_PCT_MINS_COLS',
    'DataFrameScaler',
    'DomainSparsityTransformer',
    'PreprocessingArtifacts',
    'YeoJohnsonTransformer',
    'detect_skewed_features',
    'engineer_card_points',
    'engineer_set_piece_takers',
    'power_transform_features',
    'preprocess_modelling_pipeline',
    'retire_sparse_features',
    'scale_features',
    'separate_features_and_metadata',
]
