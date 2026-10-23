"""
Unit tests for the preprocessing modules, scikit-learn transformers, and pipeline.
"""

import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from scripts.preprocessing.columns import (
    COLS_TO_METADATA,
    separate_features_and_metadata,
)
from scripts.preprocessing.pipeline import preprocess_modelling_pipeline
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

REPO_ROOT = Path(__file__).resolve().parents[1]
FEATURESET_CSV = REPO_ROOT / 'data' / 'processed' / 'player_featureset.csv'


class TestPreprocessingColumns(unittest.TestCase):
    def setUp(self):
        self.sample_df = pd.DataFrame({
            'player_identifier': ['p1', 'p2', 'p3'],
            'Player': ['Alice', 'Bob', 'Charlie'],
            'Nation': ['ENG', 'FRA', 'GER'],
            'Age': [25, 28, 22],
            'Pos': ['FW', 'MF', 'DF'],
            'Primary_Pos': ['FW', 'MF', 'DF'],
            'Num_Pos': [1, 1, 1],
            'Squad': ['TeamA', 'TeamB', 'TeamC'],
            'Comp': ['LeagueA', 'LeagueB', 'LeagueC'],
            'passing_foot_pref': ['right', 'left', 'indifferent'],
            'Goals_p90': [0.5, 0.1, 0.0],
            'Shots_p90': [3.0, 1.2, 0.4],
        })

    def test_metadata_separation(self):
        metadata_df, X = separate_features_and_metadata(self.sample_df)
        self.assertEqual(metadata_df.shape, (3, 10))
        self.assertEqual(X.shape, (3, 2))
        self.assertListEqual(sorted(X.columns.tolist()), ['Goals_p90', 'Shots_p90'])
        self.assertIn('Player', metadata_df.columns)
        self.assertIn('player_identifier', metadata_df.columns)

    def test_non_numeric_in_features_raises(self):
        bad_df = self.sample_df.copy()
        bad_df['invalid_text_metric'] = ['low', 'medium', 'high']
        with self.assertRaises(ValueError):
            separate_features_and_metadata(bad_df)

    def test_cols_to_metadata_contains_expected_retired_metrics(self):
        expected_retired = [
            'CrdY_p90', 'CrdR_p90', '2CrdY_p90', 'ShoPK_p90', 'ShoFK_p90',
            'OG_p90', 'Err_p90', 'PKcon_p90', 'GcaDef_p90', 'GcaPassDead_p90',
            'GcaDrib_p90', 'GcaFld_p90', 'BlkShSv_p90', 'PKwon_p90',
        ]
        self.assertEqual(len(COLS_TO_METADATA), 14)
        for col in expected_retired:
            self.assertIn(col, COLS_TO_METADATA)


class TestTransformations(unittest.TestCase):
    def setUp(self):
        np.random.seed(42)
        # Highly skewed exponential distribution
        skewed_vals = np.random.exponential(scale=2.0, size=200)
        # Approximately symmetric normal distribution
        normal_vals = np.random.normal(loc=10.0, scale=1.0, size=200)
        self.df = pd.DataFrame({
            'skewed_feat': skewed_vals,
            'normal_feat': normal_vals,
            'CrdY_p90': np.random.uniform(0.0, 0.4, size=200),
            'CrdR_p90': np.where(np.random.rand(200) > 0.9, 0.05, 0.0),
            'ShoPK_p90': np.where(np.random.rand(200) > 0.85, np.random.uniform(0.1, 0.5, size=200), 0.0),
            'ShoFK_p90': np.where(np.random.rand(200) > 0.75, np.random.uniform(0.1, 0.8, size=200), 0.0),
            'OG_p90': np.zeros(200),
        })

    def test_detect_skewed_features(self):
        skewed_cols = detect_skewed_features(self.df[['skewed_feat', 'normal_feat']], threshold=1.0)
        self.assertIn('skewed_feat', skewed_cols)
        self.assertNotIn('normal_feat', skewed_cols)

    def test_power_transform_features(self):
        raw_skew = self.df['skewed_feat'].skew()
        X_trans, pt = power_transform_features(self.df[['skewed_feat', 'normal_feat']], columns=['skewed_feat'])
        trans_skew = X_trans['skewed_feat'].skew()
        self.assertLess(abs(trans_skew), abs(raw_skew))
        self.assertTrue(hasattr(pt, 'lambdas_'))

    def test_yeo_johnson_transformer_sklearn_api(self):
        transformer = YeoJohnsonTransformer(skew_threshold=1.0)
        transformer.fit(self.df[['skewed_feat', 'normal_feat']])
        self.assertIn('skewed_feat', transformer.skewed_cols_)
        X_out = transformer.transform(self.df[['skewed_feat', 'normal_feat']])
        self.assertEqual(X_out.shape, (200, 2))
        self.assertLess(abs(X_out['skewed_feat'].skew()), abs(self.df['skewed_feat'].skew()))

    def test_engineer_card_points(self):
        card_series, pt = engineer_card_points(self.df)
        self.assertEqual(len(card_series), len(self.df))
        self.assertEqual(card_series.name, 'card_points_p90')
        self.assertTrue(hasattr(pt, 'lambdas_'))

    def test_engineer_set_piece_takers(self):
        indicators, pk_thresh, fk_thresh = engineer_set_piece_takers(self.df, pk_pct=50, fk_pct=50)
        self.assertIn('is_pk_taker', indicators.columns)
        self.assertIn('is_fk_taker', indicators.columns)
        self.assertGreater(pk_thresh, 0.0)
        self.assertGreater(fk_thresh, 0.0)
        # Takers should be binary
        self.assertTrue(set(indicators['is_pk_taker'].unique()).issubset({0, 1}))
        self.assertTrue(set(indicators['is_fk_taker'].unique()).issubset({0, 1}))

    def test_retire_sparse_features(self):
        meta_df = pd.DataFrame({'id': range(len(self.df))})
        updated_X, updated_meta = retire_sparse_features(
            self.df,
            meta_df,
            cols_to_retire=['OG_p90'],
        )
        self.assertNotIn('OG_p90', updated_X.columns)
        self.assertIn('OG_p90', updated_meta.columns)

    def test_domain_sparsity_transformer_sklearn_api(self):
        transformer = DomainSparsityTransformer(cols_to_retire=['CrdY_p90', 'CrdR_p90', 'ShoPK_p90', 'ShoFK_p90', 'OG_p90'])
        transformer.fit(self.df)
        transformed_df = transformer.transform(self.df)
        self.assertIn('card_points_p90', transformed_df.columns)
        self.assertIn('is_pk_taker', transformed_df.columns)
        self.assertIn('is_fk_taker', transformed_df.columns)
        self.assertNotIn('OG_p90', transformed_df.columns)
        self.assertNotIn('CrdY_p90', transformed_df.columns)


class TestScaling(unittest.TestCase):
    def setUp(self):
        np.random.seed(42)
        self.X = pd.DataFrame({
            'f1': np.random.normal(10, 5, 100),
            'f2': np.random.uniform(0, 100, 100),
        })

    def test_standard_scaling(self):
        X_scaled, scaler = scale_features(self.X, scaler_type='standard')
        self.assertIsNotNone(scaler)
        self.assertEqual(X_scaled.shape, self.X.shape)
        for col in self.X.columns:
            self.assertAlmostEqual(X_scaled[col].mean(), 0.0, places=5)
            self.assertAlmostEqual(X_scaled[col].std(ddof=0), 1.0, places=5)

    def test_robust_scaling(self):
        X_scaled, scaler = scale_features(self.X, scaler_type='robust')
        self.assertIsNotNone(scaler)
        self.assertEqual(X_scaled.shape, self.X.shape)
        for col in self.X.columns:
            self.assertAlmostEqual(float(X_scaled[col].median()), 0.0, places=1)

    def test_invalid_scaler_raises(self):
        with self.assertRaises(ValueError):
            scale_features(self.X, scaler_type='minmax')

    def test_data_frame_scaler_sklearn_api(self):
        scaler = DataFrameScaler(scaler_type='standard')
        scaler.fit(self.X)
        X_scaled = scaler.transform(self.X)
        self.assertIsInstance(X_scaled, pd.DataFrame)
        self.assertListEqual(list(X_scaled.columns), list(self.X.columns))


class TestEndToEndPipeline(unittest.TestCase):
    @unittest.skipUnless(FEATURESET_CSV.exists(), 'player_featureset.csv does not exist')
    def test_real_featureset_pipeline(self):
        df = pd.read_csv(FEATURESET_CSV)
        artifacts = preprocess_modelling_pipeline(df, scaler_type='standard', skew_threshold=1.0)

        # 1737 players in the 21/22 dataset
        self.assertEqual(artifacts.metadata_df.shape[0], 1737)
        self.assertEqual(artifacts.X_transformed.shape[0], 1737)
        self.assertEqual(artifacts.X_scaled.shape[0], 1737)

        # 24 metadata columns (10 original descriptive + 14 retired)
        self.assertEqual(artifacts.metadata_df.shape[1], 24)

        # 99 modelling features
        self.assertEqual(artifacts.X_transformed.shape[1], 99)
        self.assertEqual(artifacts.X_scaled.shape[1], 99)

        # Combined preprocessed dataframe
        combined = artifacts.full_preprocessed_df
        self.assertEqual(combined.shape, (1737, 123))

        # Check no missing values in scaled feature matrix
        self.assertEqual(artifacts.X_scaled.isna().sum().sum(), 0)

        # Verify key engineered features are present in active modelling set
        self.assertIn('card_points_p90', artifacts.X_scaled.columns)
        self.assertIn('is_pk_taker', artifacts.X_scaled.columns)
        self.assertIn('is_fk_taker', artifacts.X_scaled.columns)

        # Verify retired features are present in metadata but removed from modelling set
        for col in COLS_TO_METADATA:
            self.assertIn(col, artifacts.metadata_df.columns)
            self.assertNotIn(col, artifacts.X_scaled.columns)

        # Verify mean ~ 0 and std ~ 1
        means = artifacts.X_scaled.mean().abs()
        stds = artifacts.X_scaled.std()
        self.assertLess(means.max(), 1e-4)
        self.assertLess((stds - 1.0).abs().max(), 0.05)


if __name__ == '__main__':
    unittest.main()
