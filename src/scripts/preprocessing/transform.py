"""
Feature transformation and domain feature engineering for model preprocessing.

Ported from notebooks/season2122_transformation_and_scaling.ipynb. Provides skewness
detection, Yeo-Johnson power transformations, UEFA Fair Play discipline aggregation,
set-piece taker binarization, and scikit-learn compatible transformers.
"""

from collections.abc import Sequence
from typing import Any

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import PowerTransformer

from scripts.preprocessing.columns import COLS_TO_METADATA


def detect_skewed_features(
    X: pd.DataFrame,
    threshold: float = 1.0,
) -> list[str]:
    """
    Identifies features whose absolute Fisher-Pearson skewness exceeds threshold.

    Parameters
    ----------
    X : pd.DataFrame
        Numeric feature matrix.
    threshold : float
        Absolute skewness threshold above which a feature is considered highly skewed.

    Returns
    -------
    list[str]
        Column names of features exceeding the skewness threshold.
    """
    skews = X.skew().abs()
    return skews[skews > threshold].index.tolist()


def power_transform_features(
    X: pd.DataFrame,
    columns: Sequence[str] | None = None,
    method: str = 'yeo-johnson',
    skew_threshold: float = 1.0,
) -> tuple[pd.DataFrame, PowerTransformer]:
    """
    Applies power transformation to reduce skewness and stabilise variance.

    Parameters
    ----------
    X : pd.DataFrame
        Numeric feature matrix.
    columns : Sequence[str] | None
        Columns to transform. If None, columns exceeding skew_threshold are detected.
    method : str
        Power transformation method ('yeo-johnson' or 'box-cox').
    skew_threshold : float
        Threshold used if columns is None.

    Returns
    -------
    tuple[pd.DataFrame, PowerTransformer]
        Transformed copy of X and the fitted PowerTransformer instance.
    """
    if columns is None:
        columns = detect_skewed_features(X, threshold=skew_threshold)

    X_trans = X.copy()
    if not columns:
        transformer = PowerTransformer(method=method, standardize=False)
        return X_trans, transformer

    transformer = PowerTransformer(method=method, standardize=False)
    transformed_vals = transformer.fit_transform(X[list(columns)])
    X_trans[list(columns)] = transformed_vals

    return X_trans, transformer


def engineer_card_points(
    X: pd.DataFrame,
    transformer: PowerTransformer | None = None,
) -> tuple[pd.Series, PowerTransformer]:
    """
    Calculates UEFA Fair Play discipline points and applies Yeo-Johnson transformation.

    Formula: 1 point for Yellow Card (CrdY_p90), 3 points for Red Card (CrdR_p90).

    Parameters
    ----------
    X : pd.DataFrame
        Numeric feature matrix containing 'CrdY_p90' and 'CrdR_p90'.
    transformer : PowerTransformer | None
        Fitted PowerTransformer. If None, a new transformer is fitted.

    Returns
    -------
    tuple[pd.Series, PowerTransformer]
        Transformed card_points_p90 Series and the fitted PowerTransformer.
    """
    card_points_raw = X['CrdY_p90'] + (3.0 * X['CrdR_p90'])
    raw_df = card_points_raw.to_frame()

    if transformer is None:
        transformer = PowerTransformer(method='yeo-johnson', standardize=False)
        transformed_vals = transformer.fit_transform(raw_df).flatten()
    else:
        transformed_vals = transformer.transform(raw_df).flatten()

    card_points_series = pd.Series(
        transformed_vals,
        index=X.index,
        name='card_points_p90',
    )
    return card_points_series, transformer


def engineer_set_piece_takers(
    X: pd.DataFrame,
    pk_pct: float = 50.0,
    fk_pct: float = 50.0,
    pk_threshold: float | None = None,
    fk_threshold: float | None = None,
) -> tuple[pd.DataFrame, float, float]:
    """
    Binarizes penalty and direct free kick shot volume into taker indicators.

    A player is marked as a taker (1) if their per-90 shot volume meets or exceeds
    the percentile threshold computed among non-zero shot takers, filtering out
    occasional/one-off takers.

    Parameters
    ----------
    X : pd.DataFrame
        Numeric feature matrix containing 'ShoPK_p90' and 'ShoFK_p90'.
    pk_pct : float
        Percentile among non-zero penalty takers to qualify as designated taker.
    fk_pct : float
        Percentile among non-zero free kick takers to qualify as designated taker.
    pk_threshold : float | None
        Pre-computed PK threshold. If None, calculated from X.
    fk_threshold : float | None
        Pre-computed FK threshold. If None, calculated from X.

    Returns
    -------
    tuple[pd.DataFrame, float, float]
        DataFrame with 'is_pk_taker' and 'is_fk_taker' columns, plus the two thresholds.
    """
    if pk_threshold is None:
        pk_takers = X.loc[X['ShoPK_p90'] > 0, 'ShoPK_p90']
        pk_threshold = float(np.percentile(pk_takers, pk_pct)) if len(pk_takers) > 0 else 0.0

    if fk_threshold is None:
        fk_takers = X.loc[X['ShoFK_p90'] > 0, 'ShoFK_p90']
        fk_threshold = float(np.percentile(fk_takers, fk_pct)) if len(fk_takers) > 0 else 0.0

    indicators = pd.DataFrame(index=X.index)
    indicators['is_pk_taker'] = (X['ShoPK_p90'] >= pk_threshold).astype(int)
    indicators['is_fk_taker'] = (X['ShoFK_p90'] >= fk_threshold).astype(int)

    return indicators, pk_threshold, fk_threshold


def retire_sparse_features(
    X: pd.DataFrame,
    metadata_df: pd.DataFrame,
    cols_to_retire: Sequence[str] = COLS_TO_METADATA,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Moves retired features from the active feature matrix to the metadata matrix.

    Parameters
    ----------
    X : pd.DataFrame
        Active feature matrix.
    metadata_df : pd.DataFrame
        Metadata matrix.
    cols_to_retire : Sequence[str]
        Column names to retire from X into metadata_df.

    Returns
    -------
    tuple[pd.DataFrame, pd.DataFrame]
        Tuple of (updated_X, updated_metadata_df).
    """
    updated_meta = metadata_df.copy()
    for col in cols_to_retire:
        if col in X.columns and col not in updated_meta.columns:
            updated_meta[col] = X[col]

    drop_cols = [col for col in cols_to_retire if col in X.columns]
    updated_X = X.drop(columns=drop_cols)

    return updated_X, updated_meta


class YeoJohnsonTransformer(BaseEstimator, TransformerMixin):
    """
    Scikit-learn compatible transformer that detects and transforms skewed features.
    """

    def __init__(
        self,
        skew_threshold: float = 1.0,
        columns: Sequence[str] | None = None,
    ):
        self.skew_threshold = skew_threshold
        self.columns = columns
        self.skewed_cols_: list[str] = []
        self.transformer_: PowerTransformer | None = None

    def fit(self, X: pd.DataFrame, y: Any = None) -> YeoJohnsonTransformer:
        if self.columns is not None:
            self.skewed_cols_ = list(self.columns)
        else:
            self.skewed_cols_ = detect_skewed_features(X, threshold=self.skew_threshold)

        if self.skewed_cols_:
            self.transformer_ = PowerTransformer(method='yeo-johnson', standardize=False)
            self.transformer_.fit(X[self.skewed_cols_])
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        X_out = X.copy()
        if self.transformer_ is not None and self.skewed_cols_:
            transformed_vals = self.transformer_.transform(X[self.skewed_cols_])
            X_out[self.skewed_cols_] = transformed_vals
        return X_out


class DomainSparsityTransformer(BaseEstimator, TransformerMixin):
    """
    Scikit-learn compatible transformer that performs domain-specific feature
    engineering (card points, set-piece indicators) and drops retired sparse columns.
    """

    def __init__(
        self,
        pk_pct: float = 50.0,
        fk_pct: float = 50.0,
        cols_to_retire: Sequence[str] = COLS_TO_METADATA,
    ):
        self.pk_pct = pk_pct
        self.fk_pct = fk_pct
        self.cols_to_retire = list(cols_to_retire)
        self.card_transformer_: PowerTransformer | None = None
        self.pk_threshold_: float | None = None
        self.fk_threshold_: float | None = None

    def fit(self, X: pd.DataFrame, y: Any = None) -> DomainSparsityTransformer:
        _, self.card_transformer_ = engineer_card_points(X)
        _, self.pk_threshold_, self.fk_threshold_ = engineer_set_piece_takers(
            X, pk_pct=self.pk_pct, fk_pct=self.fk_pct
        )
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        X_out = X.copy()
        card_series, _ = engineer_card_points(X, transformer=self.card_transformer_)
        X_out['card_points_p90'] = card_series

        indicators, _, _ = engineer_set_piece_takers(
            X,
            pk_threshold=self.pk_threshold_,
            fk_threshold=self.fk_threshold_,
        )
        X_out['is_pk_taker'] = indicators['is_pk_taker']
        X_out['is_fk_taker'] = indicators['is_fk_taker']

        drop_cols = [col for col in self.cols_to_retire if col in X_out.columns]
        return X_out.drop(columns=drop_cols)
