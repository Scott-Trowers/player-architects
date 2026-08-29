"""Normalises raw counts to a per-90-minutes basis, replacing each count column in place."""

from scripts.constants import PER90_COUNT_COLUMNS


def normalize_per_90(df):
    df = df.copy()

    for raw_col_name in PER90_COUNT_COLUMNS:
        new_col_name = f'{raw_col_name}_p90'
        df[new_col_name] = df[raw_col_name] / df['90s']
        df = df.drop(columns=[raw_col_name])

    return df
