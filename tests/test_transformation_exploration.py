"""
Unit tests for the transformation and scaling EDA helpers.
"""

import unittest

import matplotlib

# draw charts in memory only, so tests don't try to open windows
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from scripts.eda.transformation_exploration import (
    classify_skewness,
    plot_scaling_comparison,
    plot_skewness_distribution,
    plot_transformation_comparison,
)


class TestTransformationExploration(unittest.TestCase):
    def setUp(self):
        rng = np.random.default_rng(0)
        self.X = pd.DataFrame({
            'even': rng.normal(size=500),
            'lopsided': rng.exponential(size=500),
            'very_lopsided': rng.exponential(size=500) ** 3,
        })

    def tearDown(self):
        # close charts so they don't pile up in memory across tests
        plt.close('all')

    def test_classify_skewness_counts_every_feature_once(self):
        # each column should land in exactly one skew band
        summary_df, counts = classify_skewness(self.X)
        self.assertEqual(sum(counts.values()), self.X.shape[1])
        self.assertEqual(len(summary_df), self.X.shape[1])

    def test_classify_skewness_sorts_most_skewed_first(self):
        # the most lopsided column should be at the top of the summary
        summary_df, counts = classify_skewness(self.X)
        self.assertEqual(summary_df.loc[0, 'Metric'], 'very_lopsided')
        self.assertEqual(counts['symmetric'], 1)
        self.assertEqual(counts['severe'], 2)

    def test_plot_skewness_distribution_returns_two_panels(self):
        # one histogram panel and one bar chart panel
        fig, axes = plot_skewness_distribution(self.X, top_n=2)
        self.assertIsInstance(fig, plt.Figure)
        self.assertEqual(len(axes), 2)

    def test_plot_transformation_comparison_one_row_per_column(self):
        # a before/after pair of charts for every column asked for, including just one
        _fig, axes = plot_transformation_comparison(self.X, np.log1p(self.X.abs()), ['lopsided'])
        self.assertEqual(axes.shape, (1, 2))
        _fig, axes = plot_transformation_comparison(self.X, np.log1p(self.X.abs()), ['lopsided', 'even'])
        self.assertEqual(axes.shape, (2, 2))

    def test_plot_transformation_comparison_empty_raises(self):
        # asking for no columns is a mistake and should fail clearly
        with self.assertRaises(ValueError):
            plot_transformation_comparison(self.X, self.X, [])

    def test_plot_scaling_comparison_returns_before_and_after(self):
        # one chart before scaling and one after
        scaled = (self.X - self.X.mean()) / self.X.std()
        _fig, axes = plot_scaling_comparison(self.X, scaled, ['even', 'lopsided'])
        self.assertEqual(len(axes), 2)


if __name__ == '__main__':
    unittest.main()
