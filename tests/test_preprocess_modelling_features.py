"""
Unit tests for the preprocess_modelling_features command-line script.
"""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import pandas as pd

from scripts import preprocess_modelling_features
from tests.test_preprocessing import make_synthetic_featureset


class TestPreprocessModellingFeaturesCli(unittest.TestCase):
    def test_writes_three_outputs_with_player_id(self):
        # running the script on a fake featureset should save all three files, each keyed by player id
        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            input_csv = tmp_dir / 'featureset.csv'
            make_synthetic_featureset().to_csv(input_csv, index=False)

            argv = ['prog', '--input-csv', str(input_csv), '--output-dir', str(tmp_dir)]
            with mock.patch.object(sys, 'argv', argv):
                preprocess_modelling_features.main()

            for name in ['player_features_scaled.csv', 'player_metadata.csv', 'player_featureset_preprocessed.csv']:
                saved = pd.read_csv(tmp_dir / name)
                self.assertIn('player_identifier', saved.columns)

            scaled = pd.read_csv(tmp_dir / 'player_features_scaled.csv')
            self.assertEqual(scaled.columns[0], 'player_identifier')

    def test_missing_input_raises(self):
        # a wrong input path should fail straight away with a clear error
        argv = ['prog', '--input-csv', '/does/not/exist.csv']
        with mock.patch.object(sys, 'argv', argv), self.assertRaises(FileNotFoundError):
            preprocess_modelling_features.main()


if __name__ == '__main__':
    unittest.main()
