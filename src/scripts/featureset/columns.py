"""
Column-group definitions and pruning lists for the player featureset.

Ported from the column-group cells in notebooks/season2122_eda.ipynb. Each group is
already defined in its post-feature-engineering form (i.e. including derived columns
such as Tkl_success% or forward_pressing_index), paired with the columns to prune from
it before it's added to the final featureset.

Two fixes vs. the notebook's original behaviour are applied here (see
docs/eda-findings.md): `forward_touch_index` is included in INVOLVEMENT_COLS, and
`PasAtt_p90` is actually removed from the final featureset rather than left in by a
no-op prune call.
"""

from scripts.prune_featureset import prune_features

DESCRIPTIVE_COLS = [
    'player_identifier', 'Player', 'Nation', 'Age', 'Pos', 'Primary_Pos', 'Num_Pos',
    'Squad', 'Comp', 'passing_foot_pref',
]

MATCHES_PLAYED_COLS = ['MP', 'Starts', 'Min', '90s', 'avg_minutes_per_match', 'starts_pct']
MATCHES_PLAYED_PRUNE = ['90s', 'Starts']

FINISHING_COLS = ['SoT%', 'G/Sh', 'ShoDist', 'Goals_p90', 'Shots_p90', 'SoT_p90']
FINISHING_PRUNE = []

CHANCE_CREATION_COLS = [
    'Assists_p90', 'PasAss_p90', 'SCA_p90', 'ScaPassLive_p90', 'ScaDrib_p90',
    'ScaSh_p90', 'ScaFld_p90', 'ScaDef_p90', 'GCA_p90', 'GcaPassLive_p90',
    'GcaDrib_p90', 'GcaSh_p90', 'GcaFld_p90', 'GcaDef_p90', 'PKwon_p90',
]
CHANCE_CREATION_PRUNE = []

# Already cut down to the columns that indicate set-piece success/volume, rather than
# just being entrusted with them (see docs/eda-findings.md).
SET_PIECES_COLS = ['ShoFK_p90', 'ShoPK_p90', 'CK_p90', 'GcaPassDead_p90']
SET_PIECES_PRUNE = []

PASSING_COLS = [
    'PasTotCmp%', 'PasShoCmp%', 'PasMedCmp%', 'PasLonCmp%', 'PasTotCmp_p90',
    'PasTotAtt_p90', 'PasTotDist_p90', 'PasTotPrgDist_p90', 'PasShoCmp_p90',
    'PasShoAtt_p90', 'PasMedCmp_p90', 'PasMedAtt_p90', 'PasLonCmp_p90', 'PasLonAtt_p90',
    'Pas3rd_p90', 'PPA_p90', 'CrsPA_p90', 'PasProg_p90', 'PasAtt_p90', 'PasLive_p90',
    'TB_p90', 'PasPress_p90', 'Sw_p90', 'PasCrs_p90', 'PasGround_p90', 'PasLow_p90',
    'PasHigh_p90', 'PaswLeft_p90', 'PaswRight_p90', 'PaswHead_p90', 'PaswOther_p90',
    'PasCmp_p90', 'PasOut_p90', 'PasInt_p90', 'PasBlocks_p90', 'RecProg_p90',
    'Crs_p90', 'PasOff_p90',
    'forward_distance_pct', 'progressive_pass_pct', 'intercepted_pass_rate',
    'oob_pass_rate', 'offside_pass_rate', 'pressure_pass_rate',
    'passing_two_footedness_entropy',
]
PASSING_PRUNE = [
    'PasTotCmp_p90', 'PasTotAtt_p90', 'PasCrs_p90', 'PasShoAtt_p90', 'PasMedAtt_p90',
    'PasLonAtt_p90', 'PasLive_p90', 'PasTotPrgDist_p90', 'PasTotDist_p90',
    'PasProg_p90', 'PasCmp_p90', 'PaswLeft_p90', 'PaswRight_p90',
]

# Positioning (Off_p90) is intentionally excluded from the final featureset entirely —
# it lacks any success/context signal on its own (see docs/eda-findings.md) — so no
# POSITIONING_COLS group is defined or pruned here.

DEFENSIVE_PLAYS_COLS = [
    'TklDri%', 'Tkl_p90', 'TklWon_p90', 'TklDef3rd_p90', 'TklMid3rd_p90',
    'TklAtt3rd_p90', 'TklDri_p90', 'TklDriAtt_p90', 'TklDriPast_p90', 'Blocks_p90',
    'BlkSh_p90', 'BlkShSv_p90', 'BlkPass_p90', 'Int_p90', 'Tkl+Int_p90', 'Clr_p90',
    'Err_p90', 'TklW_p90', 'PKcon_p90', 'OG_p90', 'Recov_p90', 'Tkl_success%',
]
DEFENSIVE_PLAYS_PRUNE = ['TklWon_p90', 'TklW_p90', 'Tkl+Int_p90']

AERIAL_ABILITY_COLS = ['AerWon%', 'AerWon_p90', 'AerLost_p90']
AERIAL_ABILITY_PRUNE = ['AerLost_p90']

PRESSURES_COLS = [
    'Press%', 'Press_p90', 'PresSucc_p90', 'PresDef3rd_p90', 'PresMid3rd_p90',
    'PresAtt3rd_p90', 'forward_pressing_index',
]
PRESSURES_PRUNE = ['PresSucc_p90']

INVOLVEMENT_COLS = [
    'Rec%', 'Touches_p90', 'TouDefPen_p90', 'TouDef3rd_p90', 'TouMid3rd_p90',
    'TouAtt3rd_p90', 'TouAttPen_p90', 'RecTarg_p90', 'Rec_p90', 'forward_touch_index',
]
INVOLVEMENT_PRUNE = ['Rec_p90', 'TouDef3rd_p90', 'TouMid3rd_p90', 'TouAtt3rd_p90']

DRIBBLING_COLS = [
    'DriSucc%', 'DriSucc_p90', 'DriAtt_p90', 'DriPast_p90', 'DriMegs_p90',
    'Carries_p90', 'CarTotDist_p90', 'CarPrgDist_p90', 'CarProg_p90', 'Car3rd_p90',
    'CPA_p90', 'CarMis_p90', 'CarDis_p90', 'Fld_p90', 'CarProg%',
]
DRIBBLING_PRUNE = ['DriSucc_p90', 'DriAtt_p90', 'CarTotDist_p90']

DISCIPLINE_COLS = ['CrdY_p90', 'CrdR_p90', '2CrdY_p90', 'Fls_p90']
DISCIPLINE_PRUNE = []

# Order matters: mirrors the sequence of prune_features calls in the notebook.
GROUPS = [
    (MATCHES_PLAYED_COLS, MATCHES_PLAYED_PRUNE),
    (FINISHING_COLS, FINISHING_PRUNE),
    (CHANCE_CREATION_COLS, CHANCE_CREATION_PRUNE),
    (SET_PIECES_COLS, SET_PIECES_PRUNE),
    (PASSING_COLS, PASSING_PRUNE),
    (DEFENSIVE_PLAYS_COLS, DEFENSIVE_PLAYS_PRUNE),
    (AERIAL_ABILITY_COLS, AERIAL_ABILITY_PRUNE),
    (PRESSURES_COLS, PRESSURES_PRUNE),
    (INVOLVEMENT_COLS, INVOLVEMENT_PRUNE),
    (DRIBBLING_COLS, DRIBBLING_PRUNE),
    (DISCIPLINE_COLS, DISCIPLINE_PRUNE),
]

# Never actually pruned by the notebook's final (buggy) prune call; removed directly.
FINAL_EXTRA_PRUNE = ['PasAtt_p90']


def build_final_featureset():
    """Assembles the final featureset column list, in the same order as the notebook."""

    final_featureset = []
    for cols, cols_to_prune in GROUPS:
        final_featureset = prune_features(cols, cols_to_prune, target_featureset=final_featureset)

    final_featureset = [col for col in final_featureset if col not in FINAL_EXTRA_PRUNE]

    return DESCRIPTIVE_COLS + final_featureset
