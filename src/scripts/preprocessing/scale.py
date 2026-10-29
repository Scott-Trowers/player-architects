"""
Feature scaling utilities and scikit-learn compatible scaler wrappers.

Ported from notebooks/season2122_transformation_and_scaling.ipynb. Provides a
StandardScaler/RobustScaler wrapper that preserves pandas DataFrame index and
column structure.
"""

from typing import Any

import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import RobustScaler, StandardScaler
from sklearn.utils.validation import check_is_fitted

# ASSUMPTION: StandardScaler over RobustScaler. many features are still zero-inflated after
# transforming, so their IQR is 0 and RobustScaler would leave them unscaled
DEFAULT_SCALER_TYPE = 'standard'


def build_scaler(scaler_type: str = DEFAULT_SCALER_TYPE) -> StandardScaler | RobustScaler:
    """
    Creates an unfitted scikit-learn scaler from its name.

    Parameters
    ----------
    scaler_type : str
        Scaling strategy ('standard' or 'robust').

    Returns
    -------
    StandardScaler | RobustScaler
        A new scaler that hasn't learned anything yet.

    Raises
    ------
    ValueError
        If an unsupported scaler_type is provided.
    """
    if scaler_type == 'standard':
        return StandardScaler()
    if scaler_type == 'robust':
        return RobustScaler()
    raise ValueError(f"Unsupported scaler_type: {scaler_type}. Use 'standard' or 'robust'.")


class DataFrameScaler(BaseEstimator, TransformerMixin):
    """
    Scikit-learn compatible scaler that preserves pandas DataFrame columns and index.
    """

    def __init__(self, scaler_type: str = DEFAULT_SCALER_TYPE):
        """
        Sets up the scaler's settings. Nothing is learned from data yet.

        Parameters
        ----------
        scaler_type : str
            Which scaling method to use ('standard' or 'robust').
        """
        self.scaler_type = scaler_type

    def fit(self, X: pd.DataFrame, y: Any = None) -> DataFrameScaler:
        """
        Learns the average and spread of each column so they can be put on the same scale.

        Parameters
        ----------
        X : pd.DataFrame
            Player performance data to learn from.
        y : Any
            Not used. Only here so this works inside scikit-learn tools.

        Returns
        -------
        DataFrameScaler
            This same scaler, now holding what it learned.

        Raises
        ------
        ValueError
            If scaler_type is not 'standard' or 'robust'.
        """
        self.scaler_ = build_scaler(self.scaler_type).fit(X)
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Puts every column on the same scale using what was learned in fit.

        Parameters
        ----------
        X : pd.DataFrame
            Player performance data to scale.

        Returns
        -------
        pd.DataFrame
            Scaled data, keeping the original row labels and column names.

        Raises
        ------
        NotFittedError
            If called before fit.
        """
        check_is_fitted(self)
        scaled_vals = self.scaler_.transform(X)
        return pd.DataFrame(scaled_vals, index=X.index, columns=X.columns)
