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
from sklearn.utils.validation import check_is_fitted

from scripts.preprocessing.columns import COLS_TO_METADATA

# ASSUMPTION: |skew| > 1.0 is the conventional "highly skewed" cut-off. 46 of 109 features
# breached it in the 21/22 data, and those are the ones that would dominate variance in
# dimension reduction and the distances used for clustering
DEFAULT_SKEW_THRESHOLD = 1.0

# ASSUMPTION: yeo-johnson over box-cox (can't handle the many zeros) and log(x + 1) (unevenly
# compresses small fractional per-90 values). it also handles negative values, like
# forward_pressing_index, and fits its own strength (lambda) per feature
POWER_METHOD = 'yeo-johnson'

# ASSUMPTION: UEFA Fair Play weighting, a red has 3x the impact of a yellow. combining them cuts
# red card zero-inflation from ~99% to ~6% because yellows are far more common
YELLOW_CARD_POINTS = 1.0
RED_CARD_POINTS = 3.0

# ASSUMPTION: a designated taker is in the top half (by per-90 volume) of players who took at
# least one, which filters out one-off and occasional takers
DEFAULT_TAKER_PCT = 50.0

ENGINEERED_COLS: tuple[str, ...] = ('card_points_p90', 'is_pk_taker', 'is_fk_taker')


def detect_skewed_features(
    X: pd.DataFrame,
    threshold: float = DEFAULT_SKEW_THRESHOLD,
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


def engineer_card_points(
    X: pd.DataFrame,
    transformer: PowerTransformer | None = None,
) -> tuple[pd.Series, PowerTransformer]:
    """
    Calculates UEFA Fair Play discipline points and applies Yeo-Johnson transformation.

    Formula: 1 point for Yellow Card (CrdY_p90), 3 points for Red Card (CrdR_p90).
    2CrdY_p90 (second yellows) is not added on top, see the ASSUMPTION note in the code.

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
    # ASSUMPTION: 2CrdY_p90 is left out because second-yellow sending offs are already counted in
    # CrdR_p90 (true for all 143 such players in 21/22), so adding it would double count
    card_points_raw = YELLOW_CARD_POINTS * X['CrdY_p90'] + RED_CARD_POINTS * X['CrdR_p90']
    raw_df = card_points_raw.to_frame()

    if transformer is None:
        transformer = PowerTransformer(method=POWER_METHOD, standardize=False)
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
    pk_pct: float = DEFAULT_TAKER_PCT,
    fk_pct: float = DEFAULT_TAKER_PCT,
    pk_threshold: float | None = None,
    fk_threshold: float | None = None,
) -> tuple[pd.DataFrame, float, float]:
    """
    Binarizes penalty and direct free kick shot volume into taker indicators.

    A player is marked as a taker (1) only if they took at least one shot of that
    type AND their per-90 shot volume meets or exceeds the percentile threshold
    computed among non-zero shot takers, filtering out occasional/one-off takers.

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

    # the > 0 check stops everyone being flagged when no one took that kind of shot (threshold 0)
    indicators = pd.DataFrame(index=X.index)
    indicators['is_pk_taker'] = (
        (X['ShoPK_p90'] > 0) & (X['ShoPK_p90'] >= pk_threshold)
    ).astype(int)
    indicators['is_fk_taker'] = (
        (X['ShoFK_p90'] > 0) & (X['ShoFK_p90'] >= fk_threshold)
    ).astype(int)

    return indicators, pk_threshold, fk_threshold


def retire_sparse_features(
    X: pd.DataFrame,
    metadata_df: pd.DataFrame,
    cols_to_retire: Sequence[str] = COLS_TO_METADATA,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Moves retired features from the active feature matrix to the metadata matrix.

    Pass the raw (untransformed) matrix as X so metadata keeps real, readable values.

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


class DomainFeatureEngineer(BaseEstimator, TransformerMixin):
    """
    Scikit-learn transformer that adds the card score and set-piece taker flags,
    then drops the rare columns they replace (or that are too rare to model).

    Must run on raw, untransformed data so the card score and taker cut-offs are
    worked out from real per-90 values.
    """

    def __init__(
        self,
        pk_pct: float = DEFAULT_TAKER_PCT,
        fk_pct: float = DEFAULT_TAKER_PCT,
        cols_to_retire: Sequence[str] = COLS_TO_METADATA,
    ):
        """
        Stores the settings exactly as given. Nothing is learned from data yet.

        Parameters
        ----------
        pk_pct : float
            How high up the penalty-taking rankings a player must be to count as a taker.
        fk_pct : float
            How high up the free-kick-taking rankings a player must be to count as a taker.
        cols_to_retire : Sequence[str]
            Columns to remove from the model because they're too rare to be useful.
        """
        # stored untouched so scikit-learn can make fresh copies of this transformer
        self.pk_pct = pk_pct
        self.fk_pct = fk_pct
        self.cols_to_retire = cols_to_retire

    def fit(self, X: pd.DataFrame, y: Any = None) -> DomainFeatureEngineer:
        """
        Learns the cut-offs for set-piece takers and how to reshape the card score.

        Parameters
        ----------
        X : pd.DataFrame
            Raw player performance data to learn from.
        y : Any
            Not used. Only here so this works inside scikit-learn tools.

        Returns
        -------
        DomainFeatureEngineer
            This same transformer, now holding what it learned.
        """
        _, self.card_transformer_ = engineer_card_points(X)
        _, self.pk_threshold_, self.fk_threshold_ = engineer_set_piece_takers(
            X, pk_pct=self.pk_pct, fk_pct=self.fk_pct
        )
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Adds the card score and set-piece taker flags, then removes the rare columns.

        Parameters
        ----------
        X : pd.DataFrame
            Raw player performance data.

        Returns
        -------
        pd.DataFrame
            A copy of the data with the new columns added and the rare columns removed.

        Raises
        ------
        NotFittedError
            If called before fit.
        """
        check_is_fitted(self)
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


class YeoJohnsonTransformer(BaseEstimator, TransformerMixin):
    """
    Scikit-learn transformer that finds lopsided (skewed) columns and reshapes them
    with a Yeo-Johnson power transformation so they're closer to a bell curve.
    """

    def __init__(
        self,
        skew_threshold: float = DEFAULT_SKEW_THRESHOLD,
        columns: Sequence[str] | None = None,
        exclude: Sequence[str] = (),
    ):
        """
        Stores the settings exactly as given. Nothing is learned from data yet.

        Parameters
        ----------
        skew_threshold : float
            How lopsided a column has to be before it gets reshaped.
        columns : Sequence[str] | None
            A fixed list of columns to reshape. If None, lopsided columns are found
            automatically when fit is called.
        exclude : Sequence[str]
            Columns that must never be reshaped, even if they look lopsided.
        """
        # stored untouched so scikit-learn can make fresh copies of this transformer
        self.skew_threshold = skew_threshold
        self.columns = columns
        self.exclude = exclude

    def fit(self, X: pd.DataFrame, y: Any = None) -> YeoJohnsonTransformer:
        """
        Learns which columns are lopsided and how much each needs reshaping.

        Parameters
        ----------
        X : pd.DataFrame
            Player performance data to learn from.
        y : Any
            Not used. Only here so this works inside scikit-learn tools.

        Returns
        -------
        YeoJohnsonTransformer
            This same transformer, now holding what it learned.
        """
        candidates = X.drop(columns=[col for col in self.exclude if col in X.columns])
        if self.columns is not None:
            self.skewed_cols_ = [col for col in self.columns if col in candidates.columns]
        else:
            self.skewed_cols_ = detect_skewed_features(candidates, threshold=self.skew_threshold)

        self.transformer_ = None
        if self.skewed_cols_:
            self.transformer_ = PowerTransformer(method=POWER_METHOD, standardize=False)
            self.transformer_.fit(X[self.skewed_cols_])
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Reshapes the lopsided columns using what was learned in fit.

        Parameters
        ----------
        X : pd.DataFrame
            Player performance data to reshape.

        Returns
        -------
        pd.DataFrame
            A copy of the data with the lopsided columns reshaped. Other columns are unchanged.

        Raises
        ------
        NotFittedError
            If called before fit.
        """
        check_is_fitted(self)
        X_out = X.copy()
        if self.transformer_ is not None:
            X_out[self.skewed_cols_] = self.transformer_.transform(X[self.skewed_cols_])
        return X_out
