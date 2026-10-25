"""
Exploratory data analysis and diagnostic visualizations for transformations and scaling.

Ported from notebooks/season2122_transformation_and_scaling.ipynb. Provides functions
to summarize feature skewness, visualize skew distributions, compare pre/post power
transformations, and evaluate feature scaling distributions.
"""

from collections.abc import Sequence
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


def classify_skewness(X: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    """
    Computes Fisher-Pearson skewness and classifies features by skew severity.

    Parameters
    ----------
    X : pd.DataFrame
        Numeric feature matrix.

    Returns
    -------
    tuple[pd.DataFrame, dict[str, int]]
        A summary DataFrame sorted by absolute skewness, and a dictionary with
        counts for symmetric, moderate, high, and severe skew categories.
    """
    skewness_series = X.skew()
    abs_skewness = skewness_series.abs()

    summary_df = pd.DataFrame({
        'Metric': skewness_series.index,
        'Skewness': skewness_series.values,
        'Abs_Skewness': abs_skewness.values,
    }).sort_values('Abs_Skewness', ascending=False).reset_index(drop=True)

    # ASSUMPTION: common rule-of-thumb skew bands, |skew| > 1.0 being the transformation cut-off
    counts = {
        'symmetric': int((abs_skewness <= 0.5).sum()),
        'moderate': int(((abs_skewness > 0.5) & (abs_skewness <= 1.0)).sum()),
        'high': int(((abs_skewness > 1.0) & (abs_skewness <= 2.0)).sum()),
        'severe': int((abs_skewness > 2.0).sum()),
    }

    return summary_df, counts


def plot_skewness_distribution(
    X: pd.DataFrame,
    top_n: int = 15,
) -> tuple[plt.Figure, Any]:
    """
    Plots the overall distribution of absolute skewness and a barplot of top skewed metrics.

    Parameters
    ----------
    X : pd.DataFrame
        Numeric feature matrix.
    top_n : int
        Number of top skewed features to display in the barplot.

    Returns
    -------
    tuple[plt.Figure, Any]
        Figure and axes objects.
    """
    summary_df, _ = classify_skewness(X)
    abs_skewness = summary_df['Abs_Skewness']

    fig, axes = plt.subplots(1, 2, figsize=(16, 5))

    sns.histplot(abs_skewness, bins=25, kde=True, color='teal', ax=axes[0])
    axes[0].axvline(0.5, color='#4C72B0', linestyle='--', linewidth=1.5, label='Symmetric boundary (0.5)')
    axes[0].axvline(1.0, color='#DD8452', linestyle='--', linewidth=1.5, label='High skew threshold (1.0)')
    axes[0].axvline(2.0, color='#C44E52', linestyle='--', linewidth=1.5, label='Severe skew threshold (2.0)')
    axes[0].set_title(f'Distribution of Absolute Skewness Across {len(X.columns)} Metrics', fontsize=12, fontweight='bold')
    axes[0].set_xlabel('|Skewness|')
    axes[0].set_ylabel('Feature Count')
    axes[0].legend()

    top_skewed = summary_df.head(top_n)
    sns.barplot(
        data=top_skewed,
        x='Abs_Skewness',
        y='Metric',
        hue='Metric',
        palette='viridis',
        legend=False,
        ax=axes[1],
    )
    axes[1].set_title(f'Top {top_n} Most Skewed Features', fontsize=12, fontweight='bold')
    axes[1].set_xlabel('|Skewness|')
    axes[1].set_ylabel('')

    plt.tight_layout()
    return fig, axes


def plot_transformation_comparison(
    X_raw: pd.DataFrame,
    X_transformed: pd.DataFrame,
    columns: Sequence[str],
) -> tuple[plt.Figure, Any]:
    """
    Plots comparative density histograms before and after transformation for selected features.

    Parameters
    ----------
    X_raw : pd.DataFrame
        Raw numeric feature matrix.
    X_transformed : pd.DataFrame
        Transformed feature matrix.
    columns : Sequence[str]
        List of column names to compare.

    Returns
    -------
    tuple[plt.Figure, Any]
        Figure and axes array.
    """
    col_list = list(columns)
    n_cols = len(col_list)
    if n_cols == 0:
        raise ValueError("columns cannot be empty.")

    fig, axes = plt.subplots(n_cols, 2, figsize=(14, max(4, 3 * n_cols)))
    if n_cols == 1:
        axes = np.expand_dims(axes, axis=0)

    for i, col in enumerate(col_list):
        raw_s = X_raw[col].skew()
        trans_s = X_transformed[col].skew()

        sns.histplot(X_raw[col], kde=True, color='#4C72B0', ax=axes[i, 0], stat='density', bins=30)
        axes[i, 0].set_title(f"Raw: {col} (Skew: {raw_s:.2f})", fontweight='bold', fontsize=11)
        axes[i, 0].set_xlabel('')

        sns.histplot(X_transformed[col], kde=True, color='#55A868', ax=axes[i, 1], stat='density', bins=30)
        axes[i, 1].set_title(f"Yeo-Johnson: {col} (Skew: {trans_s:.2f})", fontweight='bold', fontsize=11)
        axes[i, 1].set_xlabel('')

    plt.tight_layout()
    return fig, axes


def plot_scaling_comparison(
    X_unscaled: pd.DataFrame,
    X_scaled: pd.DataFrame,
    sample_metrics: Sequence[str],
) -> tuple[plt.Figure, Any]:
    """
    Plots boxplots of sample metrics before and after scaling to illustrate distribution harmonisation.

    Parameters
    ----------
    X_unscaled : pd.DataFrame
        Feature matrix before scaling.
    X_scaled : pd.DataFrame
        Feature matrix after scaling.
    sample_metrics : Sequence[str]
        Metrics with diverse original scales to include in the plot.

    Returns
    -------
    tuple[plt.Figure, Any]
        Figure and axes array.
    """
    metrics = list(sample_metrics)
    fig, axes = plt.subplots(2, 1, figsize=(14, 8))

    sns.boxplot(data=X_unscaled[metrics], orient='h', palette='Blues', ax=axes[0])
    axes[0].set_title('Before Scaling (Heterogeneous Units)', fontsize=12, fontweight='bold')
    axes[0].set_xlabel('Raw / Transformed Value')

    sns.boxplot(data=X_scaled[metrics], orient='h', palette='Greens', ax=axes[1])
    axes[1].set_title('After Scaling (Standardised Z-scores)', fontsize=12, fontweight='bold')
    axes[1].set_xlabel('Standard Deviations (Z-score)')

    plt.tight_layout()
    return fig, axes
