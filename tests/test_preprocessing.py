"""
Unit tests for the preprocessing modules, scikit-learn transformers, and pipeline.
"""

import unittest
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.exceptions import NotFittedError
from sklearn.preprocessing import RobustScaler, StandardScaler

from scripts.preprocessing.columns import (
    COLS_TO_METADATA,
    DESCRIPTIVE_COLS,
    separate_features_and_metadata,
)
from scripts.preprocessing.pipeline import (
    build_preprocessing_pipeline,
    preprocess_modelling_pipeline,
)
from scripts.preprocessing.scale import DataFrameScaler, build_scaler
from scripts.preprocessing.transform import (
    DomainFeatureEngineer,
    YeoJohnsonTransformer,
    detect_skewed_features,
    engineer_card_points,
    engineer_set_piece_takers,
    retire_sparse_features,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
FEATURESET_CSV = REPO_ROOT / 'data' / 'processed' / 'player_featureset.csv'


def make_synthetic_featureset(n_players: int = 200, seed: int = 0) -> pd.DataFrame:
    """Builds a small fake player featureset shaped like the real one, for tests that can't rely on real data."""
    rng = np.random.default_rng(seed)
    df = pd.DataFrame({'player_identifier': [f'p{i}' for i in range(n_players)]})
    # every expected descriptive column, filled with placeholder values
    for col in DESCRIPTIVE_COLS[1:]:
        df[col] = rng.integers(18, 36, size=n_players)
    df = df.assign(
        # one lopsided column and one evenly spread column
        Goals_p90=rng.exponential(scale=0.2, size=n_players),
        Touches_p90=rng.normal(loc=50.0, scale=10.0, size=n_players),
    )
    # every retired column, mostly zeros like the real rare-event stats
    for col in COLS_TO_METADATA:
        df[col] = np.where(rng.random(n_players) > 0.8, rng.uniform(0.05, 0.5, size=n_players), 0.0)
    df['CrdY_p90'] = rng.uniform(0.0, 0.4, size=n_players)
    return df


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

    def test_missing_metadata_columns_warns(self):
        # the sample has no signed_preference_score or league minute columns, so a warning should name them
        with self.assertWarns(UserWarning) as caught:
            separate_features_and_metadata(self.sample_df)
        self.assertIn('signed_preference_score', str(caught.warning))

    def test_no_warning_when_all_metadata_present(self):
        # when every expected column is there, nothing should be flagged
        full_df = self.sample_df.copy()
        for col in DESCRIPTIVE_COLS:
            if col not in full_df.columns:
                full_df[col] = 0.0
        with warnings.catch_warnings():
            warnings.simplefilter('error')
            separate_features_and_metadata(full_df)

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

    @unittest.skipUnless(FEATURESET_CSV.exists(), 'player_featureset.csv does not exist')
    def test_retired_columns_exist_in_real_featureset(self):
        # catches a retired column being renamed upstream, which would silently leave it in the model
        real_cols = pd.read_csv(FEATURESET_CSV, nrows=1).columns
        for col in COLS_TO_METADATA:
            self.assertIn(col, real_cols)


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

    def test_no_shots_taken_means_no_takers(self):
        # if nobody took a penalty, nobody should be flagged as a penalty taker
        no_pk = pd.DataFrame({'ShoPK_p90': [0.0] * 5, 'ShoFK_p90': [0.0, 0.0, 0.0, 0.0, 0.3]})
        indicators, _, _ = engineer_set_piece_takers(no_pk)
        self.assertEqual(indicators['is_pk_taker'].sum(), 0)
        self.assertEqual(indicators['is_fk_taker'].sum(), 1)

    def test_zero_shot_player_never_a_taker_even_with_zero_threshold(self):
        # a threshold of 0 passed in from elsewhere still shouldn't flag players with no shots
        df = pd.DataFrame({'ShoPK_p90': [0.0, 0.2], 'ShoFK_p90': [0.0, 0.0]})
        indicators, _, _ = engineer_set_piece_takers(df, pk_threshold=0.0, fk_threshold=0.0)
        self.assertListEqual(indicators['is_pk_taker'].tolist(), [0, 1])
        self.assertListEqual(indicators['is_fk_taker'].tolist(), [0, 0])

    def test_card_points_weights_red_three_times_yellow(self):
        # one red card should score the same as three yellows before any reshaping
        df = pd.DataFrame({'CrdY_p90': [0.3, 0.0, 0.1, 0.2], 'CrdR_p90': [0.0, 0.1, 0.0, 0.05]})
        card_series, _ = engineer_card_points(df)
        self.assertAlmostEqual(card_series.iloc[0], card_series.iloc[1], places=10)

    def test_retire_sparse_features(self):
        meta_df = pd.DataFrame({'id': range(len(self.df))})
        updated_X, updated_meta = retire_sparse_features(
            self.df,
            meta_df,
            cols_to_retire=['OG_p90'],
        )
        self.assertNotIn('OG_p90', updated_X.columns)
        self.assertIn('OG_p90', updated_meta.columns)

    def test_yeo_johnson_transformer_respects_exclude(self):
        # an excluded column must be left exactly as it was, however lopsided it is
        transformer = YeoJohnsonTransformer(exclude=['skewed_feat'])
        X_out = transformer.fit_transform(self.df[['skewed_feat', 'normal_feat']])
        self.assertNotIn('skewed_feat', transformer.skewed_cols_)
        pd.testing.assert_series_equal(X_out['skewed_feat'], self.df['skewed_feat'])

    def test_domain_feature_engineer_sklearn_api(self):
        transformer = DomainFeatureEngineer(cols_to_retire=['CrdY_p90', 'CrdR_p90', 'ShoPK_p90', 'ShoFK_p90', 'OG_p90'])
        transformer.fit(self.df)
        transformed_df = transformer.transform(self.df)
        self.assertIn('card_points_p90', transformed_df.columns)
        self.assertIn('is_pk_taker', transformed_df.columns)
        self.assertIn('is_fk_taker', transformed_df.columns)
        self.assertNotIn('OG_p90', transformed_df.columns)
        self.assertNotIn('CrdY_p90', transformed_df.columns)

    def test_transformers_can_be_cloned(self):
        # scikit-learn tools (grid search, cross-validation) need to make fresh copies of each step
        for transformer in [
            DomainFeatureEngineer(cols_to_retire=['OG_p90']),
            YeoJohnsonTransformer(exclude=('a',)),
            DataFrameScaler(scaler_type='robust'),
        ]:
            copy = clone(transformer)
            self.assertEqual(copy.get_params(), transformer.get_params())

    def test_unfitted_transformers_raise(self):
        # using a step before it has learned anything must fail loudly, not pass data through unchanged
        for transformer in [DomainFeatureEngineer(), YeoJohnsonTransformer(), DataFrameScaler()]:
            with self.assertRaises(NotFittedError):
                transformer.transform(self.df)

    def test_fitted_settings_are_reused_on_new_data(self):
        # once learned, the taker cut-off stays fixed rather than being recalculated from new data
        engineer = DomainFeatureEngineer().fit(self.df)
        new_season = self.df.copy()
        new_season['ShoPK_p90'] = new_season['ShoPK_p90'] * 10
        engineer.transform(new_season)
        refit_threshold = DomainFeatureEngineer().fit(new_season).pk_threshold_
        self.assertNotAlmostEqual(engineer.pk_threshold_, refit_threshold)
        self.assertAlmostEqual(engineer.pk_threshold_, engineer_set_piece_takers(self.df)[1])


class TestScaling(unittest.TestCase):
    def setUp(self):
        np.random.seed(42)
        self.X = pd.DataFrame({
            'f1': np.random.normal(10, 5, 100),
            'f2': np.random.uniform(0, 100, 100),
        })

    def test_build_scaler_returns_requested_type(self):
        # the name passed in should pick the matching scikit-learn scaler
        self.assertIsInstance(build_scaler('standard'), StandardScaler)
        self.assertIsInstance(build_scaler('robust'), RobustScaler)

    def test_invalid_scaler_raises(self):
        # an unknown scaler name should fail clearly rather than quietly picking a default
        with self.assertRaises(ValueError):
            build_scaler('minmax')

    def test_standard_scaling(self):
        # every column should end up centred on 0 with a spread of 1
        X_scaled = DataFrameScaler(scaler_type='standard').fit_transform(self.X)
        self.assertEqual(X_scaled.shape, self.X.shape)
        for col in self.X.columns:
            self.assertAlmostEqual(X_scaled[col].mean(), 0.0, places=5)
            self.assertAlmostEqual(X_scaled[col].std(ddof=0), 1.0, places=5)

    def test_robust_scaling(self):
        # robust scaling centres each column on its median
        X_scaled = DataFrameScaler(scaler_type='robust').fit_transform(self.X)
        for col in self.X.columns:
            self.assertAlmostEqual(float(X_scaled[col].median()), 0.0, places=1)

    def test_data_frame_scaler_sklearn_api(self):
        scaler = DataFrameScaler(scaler_type='standard')
        scaler.fit(self.X)
        X_scaled = scaler.transform(self.X)
        self.assertIsInstance(X_scaled, pd.DataFrame)
        self.assertListEqual(list(X_scaled.columns), list(self.X.columns))


class TestSyntheticPipeline(unittest.TestCase):
    """End-to-end checks on fake data, so they always run (including in CI where the real CSV isn't available)."""

    def setUp(self):
        self.df = make_synthetic_featureset()
        self.artifacts = preprocess_modelling_pipeline(self.df)

    def test_retired_columns_keep_raw_values_in_metadata(self):
        # the main bug fix: metadata must show the original numbers, not the reshaped ones
        for col in COLS_TO_METADATA:
            pd.testing.assert_series_equal(self.artifacts.metadata_df[col], self.df[col])

    def test_retired_columns_removed_from_model_features(self):
        # rare columns must not leak into what the model sees
        for col in COLS_TO_METADATA:
            self.assertNotIn(col, self.artifacts.X_scaled.columns)

    def test_engineered_features_present(self):
        # the replacements for the retired columns should be in the model features
        for col in ['card_points_p90', 'is_pk_taker', 'is_fk_taker']:
            self.assertIn(col, self.artifacts.X_scaled.columns)

    def test_model_features_are_scaled(self):
        # every model feature should end up centred on 0 with a spread of 1
        self.assertLess(self.artifacts.X_scaled.mean().abs().max(), 1e-8)
        self.assertLess((self.artifacts.X_scaled.std(ddof=0) - 1.0).abs().max(), 1e-8)

    def test_scaled_with_id_has_identifier_first(self):
        # the saved model file needs the player id so results can be matched back to players
        with_id = self.artifacts.X_scaled_with_id
        self.assertEqual(with_id.columns[0], 'player_identifier')
        self.assertListEqual(with_id['player_identifier'].tolist(), self.df['player_identifier'].tolist())
        self.assertEqual(with_id.shape[1], self.artifacts.X_scaled.shape[1] + 1)

    def test_full_preprocessed_df_combines_metadata_and_features(self):
        # the combined output should be every metadata column plus every model feature
        combined = self.artifacts.full_preprocessed_df
        expected_cols = self.artifacts.metadata_df.shape[1] + self.artifacts.X_scaled.shape[1]
        self.assertEqual(combined.shape, (len(self.df), expected_cols))

    def test_pipeline_is_reproducible(self):
        # running twice on the same input must give identical output
        rerun = preprocess_modelling_pipeline(self.df)
        pd.testing.assert_frame_equal(rerun.X_scaled, self.artifacts.X_scaled)

    def test_taker_flags_stay_binary_before_scaling(self):
        # the 0/1 flags must not be reshaped by the skew step
        for col in ['is_pk_taker', 'is_fk_taker']:
            self.assertTrue(set(self.artifacts.X_transformed[col].unique()).issubset({0, 1}))

    def test_fitted_pipeline_applies_to_new_rows(self):
        # the saved pipeline should turn any new players into the same set of model columns
        _, X_raw = separate_features_and_metadata(self.df)
        new_rows = self.artifacts.pipeline.transform(X_raw.head(5))
        pd.testing.assert_frame_equal(new_rows, self.artifacts.X_scaled.head(5))

    def test_build_preprocessing_pipeline_step_order(self):
        # engineering must run on raw data before any reshaping or scaling
        pipeline = build_preprocessing_pipeline()
        self.assertListEqual([name for name, _ in pipeline.steps], ['engineer', 'reshape', 'scale'])


class TestEndToEndPipeline(unittest.TestCase):
    @unittest.skipUnless(FEATURESET_CSV.exists(), 'player_featureset.csv does not exist')
    def test_real_featureset_pipeline(self):
        df = pd.read_csv(FEATURESET_CSV)
        with warnings.catch_warnings():
            # every expected metadata column should now be in the featureset
            warnings.simplefilter('error', UserWarning)
            artifacts = preprocess_modelling_pipeline(df, scaler_type='standard', skew_threshold=1.0)

        # 1737 players in the 21/22 dataset
        self.assertEqual(artifacts.metadata_df.shape[0], 1737)
        self.assertEqual(artifacts.X_transformed.shape[0], 1737)
        self.assertEqual(artifacts.X_scaled.shape[0], 1737)

        # 30 metadata columns (16 descriptive + 14 retired)
        self.assertEqual(artifacts.metadata_df.shape[1], 30)

        # 99 modelling features
        self.assertEqual(artifacts.X_transformed.shape[1], 99)
        self.assertEqual(artifacts.X_scaled.shape[1], 99)

        # Combined preprocessed dataframe
        combined = artifacts.full_preprocessed_df
        self.assertEqual(combined.shape, (1737, 129))

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
            # and metadata keeps the real, untransformed values
            pd.testing.assert_series_equal(artifacts.metadata_df[col], df[col])

        # Verify mean ~ 0 and std ~ 1
        means = artifacts.X_scaled.mean().abs()
        stds = artifacts.X_scaled.std()
        self.assertLess(means.max(), 1e-4)
        self.assertLess((stds - 1.0).abs().max(), 0.05)


if __name__ == '__main__':
    unittest.main()
