# EDA Findings — 2021/22 Season

Summary of the exploratory analysis and feature engineering performed in
`notebooks/season2122_eda.ipynb`, ahead of dimension reduction and clustering
(project-plan.md milestone 3). See `data-dictionary.md` for column definitions and
`src/scripts/build_player_featureset.py` for the standalone pipeline that reproduces
this processing outside the notebook.

## Data preparation

- Source: `data/processed/2021-2022 Football Player Stats.csv` (FBref, one row per
  player per club).
- Goalkeepers excluded — GK metrics and requirements are different enough from
  outfield play that a shared model isn't appropriate at this stage.
- Players with under 600 minutes (at any single club) excluded, to avoid small-sample
  noise skewing the data.
- Players who moved clubs mid-season produce duplicate rows. These are aggregated into
  one row per player (`player_identifier = Player_Nation_Born`, since `Player` alone
  isn't unique):
  - Counts are summed across clubs.
  - Percentages/ratios/averages (`SoT%`, `PasTotCmp%`, `TklDri%`, `Press%`, `DriSucc%`,
    `Rec%`, `AerWon%`, etc.) are **recalculated from the summed counts**, not naively
    averaged, so a player's combined rate is statistically correct.
  - `ShoDist` (average shot distance) has no underlying count to recalculate from, so
    it's reconstructed via a shots-weighted average across clubs.
  - `Pos` is the union of positions played, cleaned into sorted 2-letter codes (e.g.
    `DF, MF`); `Primary_Pos` is the position at the club where the player played the
    most minutes.
  - `Comp`/`Squad` are array-aggregated for reference only, and excluded from
    clustering (too high cardinality / not a player attribute). League minutes are
    additionally captured as `{league}_pct_mins` columns, also excluded from
    clustering for the same reason.
  - `Born` is dropped after aggregation — redundant with `Age`.
- All raw counts are normalised to a per-90-minutes basis (`_p90` suffix) so playing
  time doesn't dominate the comparison between players.

## Per-group findings and decisions

| Group | Key finding | Decision |
| --- | --- | --- |
| Matches played | `90s` is a pure transform of `Min`; avg. minutes/match and starts% show a "rotation vs. core XI" split, and defenders dominate high-minutes players. | Pruned `90s`, `Starts`; kept `MP`, `Min`, `avg_minutes_per_match`, `starts_pct`. |
| Finishing | Raw output (`Goals_p90`, `Shots_p90`, `SoT_p90`) is highly correlated and forward-dominated; rate metrics (`SoT%`, `G/Sh`, `ShoDist`) are noisy for low-volume shooters (mostly defenders). | Kept all 6 — rate metrics need volume context but aren't redundant with it. |
| Chance creation | Weaker inter-correlation than other groups (passing vs. dribbling creators are genuinely different players); may need PCA on its own. | Kept all 15, no pruning. |
| Set pieces | Heavily right-skewed; only `ShoPK` and dead-ball SCA/GCA metrics indicate any success, the rest (corner/FK/throw-in volume) mostly reflect being "entrusted" with set pieces, not quality. A `penalty_success_rate` metric was tried and dropped: ~87% of players never take a penalty (undefined rate), and even takers have too few attempts per season for the rate to be a real skill signal rather than noise. | Cut down to `ShoFK_p90`, `ShoPK_p90`, `CK_p90`, `GcaPassDead_p90`. |
| Passing | 37 raw dimensions with direct duplicates (`PasCmp_p90`/`PasTotCmp_p90`) and heavy semantic overlap. Engineered rate features added: `forward_distance_pct`, `progressive_pass_pct`, `intercepted_pass_rate`, `oob_pass_rate`, `offside_pass_rate`, `pressure_pass_rate`, plus a footedness `passing_two_footedness_entropy` and a binned `passing_foot_pref` category. | Pruned 13 duplicate/derivable columns; kept completion %s, volume metrics, and the engineered rates. |
| Positioning | `Off_p90` (offsides) lacks any success context (e.g. runs that led to a chance) to make it useful on its own. | Dropped entirely from the final featureset. |
| Defensive actions | `Tkl_p90`, `TklWon_p90`, `Tkl+Int_p90` move together almost linearly; rare-event columns (`BlkShSv_p90`, `Err_p90`, `OG_p90`, `PKcon_p90`) are extremely skewed. Added `Tkl_success% = TklWon_p90/Tkl_p90` (fillna 0 — only 1/1760 players have zero tackles, so the bias risk is negligible, unlike the penalty case). | Pruned `TklWon_p90`, `TklW_p90`, `Tkl+Int_p90`; kept the rest plus `Tkl_success%`. |
| Aerial ability | `AerWon%` is well-distributed and the more useful "ability" signal vs. `AerWon_p90`/`AerLost_p90`, which mostly reflect involvement (centre-backs, target men). | Pruned `AerLost_p90`; kept `AerWon%`, `AerWon_p90`. |
| Pressures | `Press_p90`, `PresSucc_p90`, `PresMid3rd_p90` are strongly correlated (r ~0.83–0.94). Added `forward_pressing_index` (zone skew relative to total pressures) as a scale-independent signal. | Pruned `PresSucc_p90`; kept the rest plus `forward_pressing_index`. |
| Match involvement | `Touches_p90`/`Rec_p90` and `TouDefPen_p90`/`TouDef3rd_p90` are highly correlated pairs. Added `forward_touch_index` (zone skew, mirroring the pressing index) — **note:** this was originally computed but not wired into the final featureset due to a missing `.extend()` call; fixed in both the notebook and the pipeline. | Pruned `Rec_p90`, `TouDef3rd_p90`, `TouMid3rd_p90`, `TouAtt3rd_p90`; kept the rest plus `forward_touch_index`. |
| Dribbling | `DriSucc_p90`, `DriAtt_p90`, `DriPast_p90` are almost perfectly correlated (r ~0.95–0.99). Added `CarProg%` (share of carries that progress the ball) as a scale-independent complement to raw carry volume. | Pruned `DriSucc_p90`, `DriAtt_p90`, `CarTotDist_p90`; kept the rest plus `CarProg%`. |
| Discipline | Card-based metrics are extremely rare-event/skewed; `Fls_p90` is the only well-spread column and best general "combative style" indicator. | Kept all 4, no pruning. |

A second bug was found and fixed while assembling the final featureset: the closing
`prune_features(final_featureset, ['PasAtt_p90'], target_featureset=final_featureset)`
call was self-referential (it extended the same list it was pruning from), so
`PasAtt_p90` was never actually removed despite the apparent intent. Both the notebook
and the standalone pipeline now filter it out directly.

## Considerations for dimension reduction & clustering

- **Position is likely to dominate cluster structure.** Nearly every group (finishing,
  defensive actions, aerial ability, matches played) shows strong `Primary_Pos`
  separation. Per the project plan, if clusters just reproduce DF/MF/FW, splitting the
  analysis by position group before clustering may be necessary to find archetypes
  *within* a position.
- **Within-group correlation is uneven** — chance creation and finishing show weaker
  inter-correlation (multiple distinct "creation styles"), while defensive actions,
  pressures, and dribbling have several near-linear trios/pairs already partially
  pruned above. Per-group PCA/FA (as planned in milestone 3) is a reasonable next step
  before combining into a single reduced space, but the correlation thresholds used
  here (0.95–0.96) were applied within groups only — worth re-checking for
  cross-group redundancy once the full featureset is assembled.
- **Mixed scales**: the final featureset mixes raw per-90 counts, percentages (0–100),
  and ratios/indices (roughly -1 to 1 or 0 to 1). Standardisation is required before
  any distance-based method (KMeans, hierarchical, PCA).
- **Skew**: several kept columns are still heavily right-skewed or rare-event in
  nature (e.g. `BlkShSv_p90`, `OG_p90`, card counts, several chance-creation columns).
  These may need a transform (log/Box-Cox) or explicit down-weighting so they don't
  dominate PCA loadings purely due to scale of variance.
- **Excluded-but-retained descriptive columns** (`Squad`, `Comp`, league
  `_pct_mins`, `signed_preference_score`) are kept in the featureset output for
  post-clustering enrichment/analysis, not as clustering inputs — they should be
  dropped from the feature matrix passed to any clustering algorithm, not from the
  output CSV itself.
- **Data gaps flagged for phase 2**: set pieces, positioning (offsides), and
  discipline all lack a "success" or "context" signal (e.g. successful runs in behind,
  fouls that stopped promising attacks) that would make those groups more useful for
  identifying skill rather than just involvement/volume.
