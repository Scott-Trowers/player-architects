"""Orchestrates the full player-featureset build, from raw CSV to final feature matrix."""

from scripts.featureset.aggregate import aggregate_players, load_raw_player_data
from scripts.featureset.columns import build_final_featureset
from scripts.featureset.engineer import (
    engineer_defensive_plays,
    engineer_dribbling,
    engineer_involvement,
    engineer_matches_played,
    engineer_passing,
    engineer_pressures,
)
from scripts.featureset.normalize import normalize_per_90


def build_featureset(raw_csv_path):
    df = load_raw_player_data(raw_csv_path)
    df = aggregate_players(df)
    df = normalize_per_90(df)

    df = engineer_matches_played(df)
    df = engineer_passing(df)
    df = engineer_defensive_plays(df)
    df = engineer_pressures(df)
    df = engineer_involvement(df)
    df = engineer_dribbling(df)

    final_featureset = build_final_featureset()
    return df[final_featureset]
