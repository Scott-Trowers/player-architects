"""
Derived-feature calculations, one function per column group.

Ported from the feature-engineering cells in notebooks/season2122_eda.ipynb. Each
function adds its group's derived columns to the per-90-normalised dataframe.
"""

import numpy as np
import pandas as pd


def engineer_matches_played(df):
    df = df.copy()
    df['avg_minutes_per_match'] = df['Min'] / df['MP']
    df['starts_pct'] = df['Starts'] / df['MP']
    return df


def engineer_passing(df):
    df = df.copy()

    df['forward_distance_pct'] = (df['PasTotPrgDist_p90'] / df['PasTotDist_p90']).fillna(0)
    df['progressive_pass_pct'] = (df['PasProg_p90'] / df['PasCmp_p90']).fillna(0)
    df['intercepted_pass_rate'] = (df['PasInt_p90'] / df['PasAtt_p90']).fillna(0)
    df['oob_pass_rate'] = (df['PasOut_p90'] / df['PasAtt_p90']).fillna(0)
    df['offside_pass_rate'] = (df['PasOff_p90'] / df['PasAtt_p90']).fillna(0)
    df['pressure_pass_rate'] = (df['PasPress_p90'] / df['PasAtt_p90']).fillna(0)

    # footedness entropy: 1.0 = perfect 50/50 split between feet, 0.0 = 100/0 split
    total_foot_passes = df['PaswRight_p90'] + df['PaswLeft_p90']
    px = np.where(total_foot_passes > 0, df['PaswRight_p90'] / total_foot_passes, 0.0)
    py = np.where(total_foot_passes > 0, df['PaswLeft_p90'] / total_foot_passes, 0.0)
    hx = np.where(px > 0, -px * np.log2(px), 0.0)
    hy = np.where(py > 0, -py * np.log2(py), 0.0)
    df['passing_two_footedness_entropy'] = hx + hy

    df['signed_preference_score'] = (
        np.sign(df['PaswRight_p90'] - df['PaswLeft_p90']) * (1.0 - df['passing_two_footedness_entropy'])
    )

    bins = [-1.01, -0.50, -0.10, 0.10, 0.50, 1.01]
    labels = [
        'heavily prefers left foot',
        'prefers left foot',
        'indifferent',
        'prefers right foot',
        'heavily prefers right foot',
    ]
    df['passing_foot_pref'] = pd.cut(df['signed_preference_score'], bins=bins, labels=labels)

    return df


def engineer_defensive_plays(df):
    df = df.copy()
    df['Tkl_success%'] = (df['TklWon_p90'] / df['Tkl_p90']).fillna(0)
    return df


def engineer_pressures(df):
    df = df.copy()
    df['forward_pressing_index'] = (
        (df['PresAtt3rd_p90'] - df['PresDef3rd_p90']).div(df['Press_p90']).fillna(0.0)
    )
    return df


def engineer_involvement(df):
    df = df.copy()
    df['forward_touch_index'] = (
        (df['TouAtt3rd_p90'] - df['TouDef3rd_p90']).div(df['Touches_p90']).fillna(0.0)
    )
    return df


def engineer_dribbling(df):
    df = df.copy()
    df['CarProg%'] = df['CarProg_p90'].div(df['Carries_p90']).fillna(0.0)
    return df
