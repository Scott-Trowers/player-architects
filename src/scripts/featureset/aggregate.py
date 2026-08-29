"""
Loads raw per-club player rows and aggregates them to one row per player.

Ported from the cleaning/aggregation cells in notebooks/season2122_eda.ipynb: drops
the index column, excludes goalkeepers, applies the minimum-minutes filter, builds a
unique player identifier, then aggregates players who appear more than once (played
for multiple clubs in the season) by summing counts and recalculating percentages,
ratios, and averages from the summed counts rather than naively averaging them.
"""

import numpy as np
import pandas as pd
from unidecode import unidecode

CSV_READ_KWARGS = {'sep': ';', 'encoding': 'latin1'}
MIN_MINUTES_THRESHOLD = 600

# Percentage/ratio/average columns that must be recalculated from summed counts after
# aggregation, rather than summed themselves.
RECALC_COLS = [
    '90s', 'SoT%', 'G/Sh', 'G/SoT', 'PasTotCmp%', 'PasShoCmp%', 'PasMedCmp%',
    'PasLonCmp%', 'TklDri%', 'Press%', 'DriSucc%', 'Rec%', 'AerWon%', 'ShoDist',
]


def load_raw_player_data(csv_path):
    df = pd.read_csv(csv_path, **CSV_READ_KWARGS)
    df = df.drop('Rk', axis=1)
    df['Player'] = df['Player'].apply(unidecode)

    df = df[~df['Pos'].str.contains('GK')]
    df = df[df['Min'] >= MIN_MINUTES_THRESHOLD]

    df['player_identifier'] = df['Player'] + '_' + df['Nation'] + '_' + df['Born'].astype(str)
    return df


def clean_positions(pos_str):
    if not isinstance(pos_str, str) or pd.isna(pos_str):
        return ''

    clean_str = ''.join(c for c in pos_str if c.isalpha())
    chunks = [clean_str[i:i + 2] for i in range(0, len(clean_str), 2) if len(clean_str[i:i + 2]) == 2]
    return ', '.join(sorted(set(chunks)))


def aggregate_players(df):
    df = df.copy()

    # estimate a weighted shot distance column
    df['ShoDist_weighted'] = df['ShoDist'] * df['Shots']

    # split minutes played into one for each league
    comps = df['Comp'].dropna().unique()
    comp_min_cols = []
    for comp in comps:
        min_col = f'{comp}_pct_mins'
        df[min_col] = df['Min'].where(df['Comp'] == comp, 0)
        comp_min_cols.append(min_col)

    numeric_cols = df.select_dtypes(include='number').columns
    exclude_from_sum = RECALC_COLS + ['Age', 'Born']

    agg_dict = {
        'Player': 'first',
        'Nation': 'first',
        'Born': 'first',
        'Age': 'max',
        'Pos': lambda x: ''.join(sorted(x.unique())),
        'Squad': lambda x: ', '.join(sorted(x.unique())),
        'Comp': lambda x: ', '.join(sorted(x.unique())),
    }
    for col in numeric_cols:
        if col not in exclude_from_sum:
            agg_dict[col] = 'sum'

    aggregated = df.groupby('player_identifier').agg(agg_dict)

    # determine the primary position (position at the club where the player played the most minutes)
    idx_max_min = df.groupby('player_identifier')['Min'].idxmax()
    primary_pos_map = df.loc[idx_max_min].set_index('player_identifier')['Pos'].str[:2]
    aggregated['Primary_Pos'] = aggregated.index.map(primary_pos_map)

    for pct_col in comp_min_cols:
        aggregated[pct_col] = (aggregated[pct_col] / aggregated['Min']).fillna(0)

    # Recalculate ratios and percentages from the summed counts
    aggregated['90s'] = aggregated['Min'] / 90
    aggregated['SoT%'] = (aggregated['SoT'] / aggregated['Shots'] * 100).fillna(0)
    aggregated['G/Sh'] = (aggregated['Goals'] / aggregated['Shots']).fillna(0)
    aggregated['G/SoT'] = (aggregated['Goals'] / aggregated['SoT']).fillna(0)
    aggregated['PasTotCmp%'] = (aggregated['PasTotCmp'] / aggregated['PasTotAtt'] * 100).fillna(0)
    aggregated['PasShoCmp%'] = (aggregated['PasShoCmp'] / aggregated['PasShoAtt'] * 100).fillna(0)
    aggregated['PasMedCmp%'] = (aggregated['PasMedCmp'] / aggregated['PasMedAtt'] * 100).fillna(0)
    aggregated['PasLonCmp%'] = (aggregated['PasLonCmp'] / aggregated['PasLonAtt'] * 100).fillna(0)
    aggregated['TklDri%'] = (aggregated['TklDri'] / aggregated['TklDriAtt'] * 100).fillna(0)
    aggregated['Press%'] = (aggregated['PresSucc'] / aggregated['Press'] * 100).fillna(0)
    aggregated['DriSucc%'] = (aggregated['DriSucc'] / aggregated['DriAtt'] * 100).fillna(0)
    aggregated['Rec%'] = (aggregated['Rec'] / aggregated['RecTarg'] * 100).fillna(0)
    aggregated['AerWon%'] = (aggregated['AerWon'] / (aggregated['AerWon'] + aggregated['AerLost']) * 100).fillna(0)
    aggregated['ShoDist'] = (aggregated['ShoDist_weighted'] / aggregated['Shots']).fillna(0)

    aggregated = aggregated.drop(columns=['ShoDist_weighted'])
    aggregated = aggregated.replace([np.inf, -np.inf], 0)
    aggregated = aggregated.reset_index()

    aggregated['Pos'] = aggregated['Pos'].apply(clean_positions)
    aggregated['Num_Pos'] = aggregated['Pos'].apply(lambda x: len(x.split(', ')) if x else 0)

    # Born is redundant with Age once aggregated
    aggregated = aggregated.drop(columns=['Born'])
    aggregated['Age'] = aggregated['Age'].astype('Int64')

    return aggregated
