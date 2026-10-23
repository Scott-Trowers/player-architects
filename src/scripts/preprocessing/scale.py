"""
Feature scaling utilities and scikit-learn compatible scaler wrappers.

Ported from notebooks/season2122_transformation_and_scaling.ipynb. Provides
StandardScaler and RobustScaler wrappers that preserve pandas DataFrame index
and column structure.
"""

from typing import Any

import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import RobustScaler, StandardScaler


def scale_features(
    X: pd.DataFrame,
    scaler_type: str = 'standard',
) -> tuple[pd.DataFrame, StandardScaler | RobustScaler]:
    """
    Scales numeric features using StandardScaler or RobustScaler.

    Parameters
    ----------
    X : pd.DataFrame
        Transformed numeric feature matrix.
    scaler_type : str
        Scaling strategy ('standard' or 'robust').

    Returns
    -------
    tuple[pd.DataFrame, StandardScaler | RobustScaler]
        Scaled DataFrame matching original index and columns, and fitted scaler.

    Raises
    ------
    ValueError
        If an unsupported scaler_type is provided.
    """
    if scaler_type == 'standard':
        scaler: StandardScaler | RobustScaler = StandardScaler()
    elif scaler_type == 'robust':
        scaler = RobustScaler()
    else:
        raise ValueError(
            f"Unsupported scaler_type: {scaler_type}. Use 'standard' or 'robust'."
        )

    scaled_vals = scaler.fit_transform(X)
    X_scaled = pd.DataFrame(scaled_vals, index=X.index, columns=X.columns)
    return X_scaled, scaler


class DataFrameScaler(BaseEstimator, TransformerMixin):
    """
    Scikit-learn compatible scaler that preserves pandas DataFrame columns and index.
    """

    def __init__(self, scaler_type: str = 'standard'):
        self.scaler_type = scaler_type
        self.scaler_: StandardScaler | RobustScaler | None = None

    def fit(self, X: pd.DataFrame, y: Any = None) -> DataFrameScaler:
        if self.scaler_type == 'standard':
            self.scaler_ = StandardScaler()
        elif self.scaler_type == 'robust':
            self.scaler_ = RobustScaler()
        else:
            raise ValueError(
                f"Unsupported scaler_type: {self.scaler_type}. Use 'standard' or 'robust'."
            )
        self.scaler_.fit(X)
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        if self.scaler_ is None:
            raise RuntimeError("DataFrameScaler must be fitted before calling transform.")
        scaled_vals = self.scaler_.transform(X)
        return pd.DataFrame(scaled_vals, index=X.index, columns=X.columns)
