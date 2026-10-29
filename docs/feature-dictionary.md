 # Feature Dictionary — Player Archetype Analysis

   NB: Column group labels are only loose, as one column may reasonably fall under multiple categories.

   _e.g. Crosses could fall under 'Passing' or 'Chance Creation'_

   ---

   ## Pipeline Overview & Artefacts

   The pipeline processes raw per-club player match statistics into model-ready feature matrices across two modular stages:

1. Feature Engineering: _(`scripts.featureset` -> `data/processed/player_featureset.csv`)_
   - Filtering: outfield players only, and a minimum of 600 minutes played.
   - Aggregated: players with multiple rows (from playing from more than one club) are aggregated to one row, with metrics aggregated appropriately.
   - Normalisation: metrics are normalised to per-90-minutes, where appropriate. These columns are appended with a `_p90` suffix.
   - New features: new aggregates, tactical indicators, and rates are engineered.
   - Pruning: redundant columns are assessed (for high collinearity and similar semantic meaning) and pruned.

2. Modelling Preprocessing: _(`scripts.preprocessing` -> `data/processed/player_featureset_preprocessed.csv`)_
   - Modelling Feature Split: features unsuitable for modelling are split from those that are; e.g. contextual features (age, position, club, etc)
   - Skew Analysis: analyse the modelling featureset for skew and non-normal distributions.
   - Skew & Sparsity Engineering: transform highly skewed features, and handle sparse features via aggregation, new feature engineering, and pruning.
   - Scaling: scale the featureset, ready for dimension reduction and clustering.
   

   ### Feature Status Legend

   | Status | Definition |
   | :--- | :--- |
   | **Active Feature** | Retained in `player_features_scaled.csv` for clustering and dimensionality reduction. |
   | **Engineered (Active)** | Newly engineered metric included in `player_features_scaled.csv`. |
   | **Engineered (Metadata)** | Newly engineered contextual metric retained in `player_metadata.csv`. |
   | **Descriptive Metadata** | Player identity, club, competition, or playing time share in `player_metadata.csv`. |
   | **Retired to Metadata** | Sparse/zero-inflated raw metric moved to `player_metadata.csv` (available for stratified/per-position v2 models). |
   | **Pruned** | Dropped during initial featureset build to eliminate collinearity or duplicate signals. |

   ---

   ### Player Info

   | Column | Description / Calculation | Data Type | Status |
   | :--- | :--- | :--- | :--- |
   | player_identifier | Unique join key formatted as `Player_Nation_Born` | Qualitative | Descriptive Metadata |
   | Player | Player's name (unidecoded to ASCII) | Qualitative | Descriptive Metadata |
   | Nation | Player's nationality | Qualitative | Descriptive Metadata |
   | Pos | Union of positions played across clubs, sorted (e.g. `DF, MF`) | Qualitative | Descriptive Metadata |
   | Primary_Pos | Position at the club where the player accumulated the most minutes | Qualitative | Descriptive Metadata |
   | Age | Player's age at season end | Count | Descriptive Metadata |
   | Num_Pos | Number of distinct positions played during the season | Count | Descriptive Metadata |

   #### Pruned Player Info Features
   | Column | Original Description | Reason for Pruning | Replacement / Covered By |
   | :--- | :--- | :--- | :--- |
   | `Born` | Year of birth | Perfectly redundant with `Age` post-aggregation; retained inside `player_identifier`. | `Age`, `player_identifier` |

   ---

   ### Team Info

   | Column | Description / Calculation | Data Type | Status |
   | :--- | :--- | :--- | :--- |
   | Squad | Comma-separated list of clubs represented during the season | Qualitative | Descriptive Metadata |
   | Comp | Comma-separated list of leagues played in during the season | Qualitative | Descriptive Metadata |

   #### Pruned Team Info Features
   | Column | Original Description | Reason for Pruning | Replacement / Covered By |
   | :--- | :--- | :--- | :--- |
   | `Rk` | Raw dataset row index | Arbitrary file sorting index. | N/A |

   ---

   ### League Playtime

   | Column | Description / Calculation | Data Type | Status |
   | :--- | :--- | :--- | :--- |
   | Premier League_pct_mins | Minutes played in the Premier League divided by total minutes | Percentage (0–1) | Descriptive Metadata |
   | Ligue 1_pct_mins | Minutes played in Ligue 1 divided by total minutes | Percentage (0–1) | Descriptive Metadata |
   | Bundesliga_pct_mins | Minutes played in the Bundesliga divided by total minutes | Percentage (0–1) | Descriptive Metadata |
   | Serie A_pct_mins | Minutes played in Serie A divided by total minutes | Percentage (0–1) | Descriptive Metadata |
   | La Liga_pct_mins | Minutes played in La Liga divided by total minutes | Percentage (0–1) | Descriptive Metadata |

   ---

   ### Matches Played

   | Column | Description / Calculation | Data Type | Status |
   | :--- | :--- | :--- | :--- |
   | MP | Total matches played (appearances across all clubs) | Count | Active Feature |
   | Min | Total minutes played across all clubs ($\ge 600$ min filter applied) | Count | Active Feature |
   | avg_minutes_per_match | Average minutes played per match appearance: $\frac{\text{Min}}{\text{MP}}$ | Continuous | Engineered (Active) |
   | starts_pct | Percentage of appearances that were starting appearances: $\frac{\text{Starts}}{\text{MP}}$ | Percentage (0–1) | Engineered (Active) |

   #### Pruned Matches Played Features
   | Column | Original Description | Reason for Pruning | Replacement / Covered By |
   | :--- | :--- | :--- | :--- |
   | `90s` | Minutes divided by 90 | Exact linear transform of `Min`; causes artificial multicollinearity. | `Min` |
   | `Starts` | Matches started | Collinear with `MP` and `Min`; rotation vs. starter status captured by `starts_pct`. | `starts_pct`, `MP` |

   ---

   ### Finishing

   | Column | Description / Calculation | Data Type | Status |
   | :--- | :--- | :--- | :--- |
   | Goals_p90 | Goals scored per 90 minutes | Per-90 Rate | Active Feature (Yeo-Johnson transformed) |
   | Shots_p90 | Total shots taken per 90 (excluding penalty kicks) | Per-90 Rate | Active Feature |
   | SoT_p90 | Shots on target per 90 (excluding penalty kicks) | Per-90 Rate | Active Feature (Yeo-Johnson transformed) |
   | SoT% | Shots on target percentage: $\frac{\text{SoT}}{\text{Shots}} \times 100$ (recalculated from summed counts) | Percentage (0–100) | Active Feature |
   | G/Sh | Goals per shot (conversion efficiency): $\frac{\text{Goals}}{\text{Shots}}$ (recalculated from summed counts) | Ratio | Active Feature (Yeo-Johnson transformed) |
   | ShoDist | Average shot distance in yards (shot-weighted average across clubs) | Average | Active Feature |

   #### Pruned Finishing Features
   | Column | Original Description | Reason for Pruning | Replacement / Covered By |
   | :--- | :--- | :--- | :--- |
   | `G/SoT` | Goals per shot on target | Redundant combination of `G/Sh` and `SoT%`; extreme noise for low-volume shooters. | `G/Sh`, `SoT%` |

   ---

   ### Chance Creation

   | Column | Description / Calculation | Data Type | Status |
   | :--- | :--- | :--- | :--- |
   | Assists_p90 | Assists per 90 minutes | Per-90 Rate | Active Feature (Yeo-Johnson transformed) |
   | PasAss_p90 | Key passes (passes leading directly to a shot attempt) per 90 | Per-90 Rate | Active Feature |
   | SCA_p90 | Total shot-creating actions per 90 minutes | Per-90 Rate | Active Feature |
   | ScaPassLive_p90 | Completed live-ball passes leading to a shot attempt per 90 | Per-90 Rate | Active Feature |
   | ScaDrib_p90 | Successful dribbles leading to a shot attempt per 90 | Per-90 Rate | Active Feature (Yeo-Johnson transformed) |
   | ScaSh_p90 | Shots leading to another shot attempt (rebounds) per 90 | Per-90 Rate | Active Feature (Yeo-Johnson transformed) |
   | ScaFld_p90 | Fouls drawn leading to a shot attempt per 90 | Per-90 Rate | Active Feature (Yeo-Johnson transformed) |
   | ScaDef_p90 | Defensive actions leading to a shot attempt per 90 | Per-90 Rate | Active Feature (Yeo-Johnson transformed) |
   | GCA_p90 | Total goal-creating actions per 90 minutes | Per-90 Rate | Active Feature (Yeo-Johnson transformed) |
   | GcaPassLive_p90 | Completed live-ball passes leading to a goal per 90 | Per-90 Rate | Active Feature (Yeo-Johnson transformed) |
   | GcaSh_p90 | Shots leading to another goal-scoring shot (rebounds) per 90 | Per-90 Rate | Active Feature (Yeo-Johnson transformed) |
   | GcaDrib_p90 | Successful dribbles leading to a goal per 90 | Per-90 Rate | Retired to Metadata |
   | GcaFld_p90 | Fouls drawn leading to a goal per 90 | Per-90 Rate | Retired to Metadata |
   | GcaDef_p90 | Defensive actions leading to a goal per 90 | Per-90 Rate | Retired to Metadata |
   | PKwon_p90 | Penalty kicks won per 90 minutes | Per-90 Rate | Retired to Metadata |

   #### Pruned / Retired Chance Creation Features
   | Column | Original Description | Reason for Retirement to Metadata | Replacement / Covered By |
   | :--- | :--- | :--- | :--- |
   | `GcaDrib_p90` | Dribbles leading to a goal per 90 | 81.7% zero-inflated; conversion depends on teammate finishing. | `ScaDrib_p90`, `GCA_p90` |
   | `GcaFld_p90` | Fouls drawn leading to a goal per 90 | 76.8% zero-inflated; rare single-season event. | `ScaFld_p90`, `GCA_p90` |
   | `GcaDef_p90` | Defensive actions leading to a goal per 90 | 90.3% zero-inflated; rare single-season conversion. | `ScaDef_p90`, `GCA_p90` |
   | `PKwon_p90` | Penalty kicks won per 90 | 83.4% zero-inflated; highly stochastic over one season. | `CPA_p90`, `TouAttPen_p90`, `ScaFld_p90` |

   ---

   ### Set Pieces

   | Column | Description / Calculation | Data Type | Status |
   | :--- | :--- | :--- | :--- |
   | CK_p90 | Corner kicks taken per 90 minutes | Per-90 Rate | Active Feature (Yeo-Johnson transformed) |
   | ScaPassDead_p90 | Completed dead-ball passes leading to a shot attempt per 90 | Per-90 Rate | Active Feature (Yeo-Johnson transformed) |
   | is_pk_taker | Designated penalty taker: $1$ if $\text{ShoPK\_p90} > 0$ and $\ge 50\text{th}$ percentile of penalty shooters, else $0$ | Binary (0/1) | Engineered (Active) |
   | is_fk_taker | Designated direct FK taker: $1$ if $\text{ShoFK\_p90} > 0$ and $\ge 50\text{th}$ percentile of FK shooters, else $0$ | Binary (0/1) | Engineered (Active) |
   | ShoPK_p90 | Penalty kicks made per 90 minutes | Per-90 Rate | Retired to Metadata |
   | ShoFK_p90 | Shots taken from direct free kicks per 90 minutes | Per-90 Rate | Retired to Metadata |
   | GcaPassDead_p90 | Completed dead-ball passes leading to a goal per 90 minutes | Per-90 Rate | Retired to Metadata |

   #### Pruned / Retired Set Piece Features
   | Column | Original Description | Reason for Pruning / Retirement | Replacement / Covered By |
   | :--- | :--- | :--- | :--- |
   | `ShoPK_p90` | Penalty kicks made per 90 | 88.7% zero-inflated; continuous volume distorts distance metrics. | `is_pk_taker` |
   | `ShoFK_p90` | Free kicks shot per 90 | 74.7% zero-inflated; continuous volume distorts distance metrics. | `is_fk_taker` |
   | `GcaPassDead_p90` | Dead-ball passes leading to a goal per 90 | 83.6% zero-inflated; teammate finishing noise. | `CK_p90`, `ScaPassDead_p90` |
   | `PKatt` | Penalty kicks attempted | Redundant with penalty shot volume and designated taker status. | `is_pk_taker` |
   | `PasDead` | Total dead-ball passes | Volume reflects designated role/entrustment, not passing skill. | `CK_p90`, `ScaPassDead_p90` |
   | `PasFK` | Passes attempted from free kicks | Entrusted role indicator; highly collinear with total passes. | `ScaPassDead_p90` |
   | `TI` | Throw-ins taken | Positional role duty (fullbacks); uninformative for overall archetype. | N/A |
   | `CkIn`, `CkOut`, `CkStr` | Inswinging, outswinging, straight corners | Tactical trajectory nuance; redundant with overall corner volume. | `CK_p90` |

   ---

   ### Passing

   | Column | Description / Calculation | Data Type | Status |
   | :--- | :--- | :--- | :--- |
   | PasTotCmp% | Total pass completion percentage: $\frac{\text{PasTotCmp}}{\text{PasTotAtt}} \times 100$ | Percentage (0–100) | Active Feature |
   | PasShoCmp% | Short pass completion percentage (5–15 yds): $\frac{\text{PasShoCmp}}{\text{PasShoAtt}} \times 100$ | Percentage (0–100) | Active Feature |
   | PasMedCmp% | Medium pass completion percentage (15–30 yds): $\frac{\text{PasMedCmp}}{\text{PasMedAtt}} \times 100$ | Percentage (0–100) | Active Feature |
   | PasLonCmp% | Long pass completion percentage (>30 yds): $\frac{\text{PasLonCmp}}{\text{PasLonAtt}} \times 100$ | Percentage (0–100) | Active Feature |
   | PasShoCmp_p90 | Short passes completed per 90 (5–15 yds) | Per-90 Rate | Active Feature |
   | PasMedCmp_p90 | Medium passes completed per 90 (15–30 yds) | Per-90 Rate | Active Feature |
   | PasLonCmp_p90 | Long passes completed per 90 (>30 yds) | Per-90 Rate | Active Feature |
   | Pas3rd_p90 | Completed passes into the attacking final third per 90 | Per-90 Rate | Active Feature (Yeo-Johnson transformed) |
   | PPA_p90 | Completed passes into the penalty area per 90 (excl. crosses) | Per-90 Rate | Active Feature |
   | CrsPA_p90 | Completed crosses into the penalty area per 90 | Per-90 Rate | Active Feature (Yeo-Johnson transformed) |
   | TB_p90 | Through balls completed into open space per 90 | Per-90 Rate | Active Feature (Yeo-Johnson transformed) |
   | Sw_p90 | Switches of play (>40 yds width) completed per 90 | Per-90 Rate | Active Feature (Yeo-Johnson transformed) |
   | Crs_p90 | Crosses attempted per 90 | Per-90 Rate | Active Feature (Yeo-Johnson transformed) |
   | RecProg_p90 | Progressive passes received per 90 | Per-90 Rate | Active Feature |
   | PasGround_p90 | Ground passes attempted per 90 | Per-90 Rate | Active Feature |
   | PasLow_p90 | Low passes attempted (below shoulder) per 90 | Per-90 Rate | Active Feature (Yeo-Johnson transformed) |
   | PasHigh_p90 | High passes attempted (above shoulder) per 90 | Per-90 Rate | Active Feature |
   | PaswHead_p90 | Headed passes attempted per 90 | Per-90 Rate | Active Feature |
   | PaswOther_p90 | Passes attempted with other body parts per 90 | Per-90 Rate | Active Feature (Yeo-Johnson transformed) |
   | PasPress_p90 | Passes attempted while under opponent pressure per 90 | Per-90 Rate | Active Feature |
   | PasOut_p90 | Passes attempted that went out of bounds per 90 | Per-90 Rate | Active Feature |
   | PasInt_p90 | Passes attempted intercepted by an opponent per 90 | Per-90 Rate | Active Feature |
   | PasBlocks_p90 | Passes attempted blocked by an opponent per 90 | Per-90 Rate | Active Feature |
   | PasOff_p90 | Passes attempted leading to an offside per 90 | Per-90 Rate | Active Feature (Yeo-Johnson transformed) |
   | forward_distance_pct | Share of pass distance directed toward opponent goal: $\frac{\text{PasTotPrgDist\_p90}}{\text{PasTotDist\_p90}}$ | Percentage (0–1) | Engineered (Active) |
   | progressive_pass_pct | Share of completed passes that are progressive: $\frac{\text{PasProg\_p90}}{\text{PasCmp\_p90}}$ | Percentage (0–1) | Engineered (Active) |
   | intercepted_pass_rate | Pass interception rate: $\frac{\text{PasInt\_p90}}{\text{PasAtt\_p90}}$ | Percentage (0–1) | Engineered (Active) |
   | oob_pass_rate | Out of bounds pass rate: $\frac{\text{PasOut\_p90}}{\text{PasAtt\_p90}}$ | Percentage (0–1) | Engineered (Active) |
   | offside_pass_rate | Offside pass rate: $\frac{\text{PasOff\_p90}}{\text{PasAtt\_p90}}$ | Percentage (0–1) | Engineered (Active, Yeo-Johnson transformed) |
   | pressure_pass_rate | Share of passes executed under pressure: $\frac{\text{PasPress\_p90}}{\text{PasAtt\_p90}}$ | Percentage (0–1) | Engineered (Active, Yeo-Johnson transformed) |
   | passing_two_footedness_entropy | Shannon entropy $H = -\sum p_i \log_2(p_i)$ of left/right foot pass attempts ($1.0 = 50/50$, $0.0 = 100/0$) | Continuous (0–1) | Engineered (Active) |
   | signed_preference_score | Directional foot dominance: $\text{sign}(\text{Right} - \text{Left}) \times (1.0 - H)$ (range $-1.0$ left to $+1.0$ right) | Continuous (-1 to +1) | Engineered (Metadata) |
   | passing_foot_pref | Categorical binned foot preference: _heavily prefers left, prefers left, indifferent, prefers right, heavily prefers right_ | Categorical | Engineered (Metadata) |

   #### Pruned Passing Features
   | Column | Original Description | Reason for Pruning | Replacement / Covered By |
   | :--- | :--- | :--- | :--- |
   | `PasCmp` | Passes completed | Exact duplicate of `PasTotCmp` in raw FBref data. | `PasTotCmp%`, completion breakdowns |
   | `PasTotCmp_p90` | Total passes completed per 90 | Derivable from completion rate and attempts; collinear with touches ($r > 0.95$). | `PasTotCmp%`, `Touches_p90` |
   | `PasAtt_p90`, `PasTotAtt_p90` | Total passes attempted per 90 | Duplicate definitions; collinear with short/med/long attempts and touches. | `Touches_p90`, distance breakdowns |
   | `PasShoAtt_p90` | Short pass attempts per 90 | Redundant with completions and short completion rate. | `PasShoCmp_p90`, `PasShoCmp%` |
   | `PasMedAtt_p90` | Medium pass attempts per 90 | Redundant with completions and medium completion rate. | `PasMedCmp_p90`, `PasMedCmp%` |
   | `PasLonAtt_p90` | Long pass attempts per 90 | Redundant with completions and long completion rate. | `PasLonCmp_p90`, `PasLonCmp%` |
   | `PasLive_p90` | Live-ball passes per 90 | Redundant with total pass volume minus set-piece deliveries. | `Touches_p90`, `CK_p90` |
   | `PasTotDist_p90` | Total passing distance per 90 | Volume-inflated proxy; progressive intent captured by relative ratio. | `forward_distance_pct` |
   | `PasTotPrgDist_p90` | Progressive pass distance per 90 | Scale-dependent; replaced by scale-independent percentage. | `forward_distance_pct` |
   | `PasProg_p90` | Progressive passes per 90 | Replaced by scale-independent progressive completion rate. | `progressive_pass_pct`, `RecProg_p90` |
   | `PasCrs_p90` | Crosses per 90 | Exact duplicate of `Crs_p90`. | `Crs_p90` |
   | `PaswLeft_p90`, `PaswRight_p90` | Left / right foot passes per 90 | Replaced by scale-invariant footedness entropy and preference score. | `passing_two_footedness_entropy`, `passing_foot_pref` |

   ---

   ### Positioning

   #### Pruned Positioning Features
   | Column | Original Description | Reason for Pruning | Replacement / Covered By |
   | :--- | :--- | :--- | :--- |
   | `Off` (`Off_p90`) | Offsides per 90 | Lacks success context (e.g. dangerous runs in behind) to reflect skill; offside passing delivery errors are retained in Passing. | `PasOff_p90`, `offside_pass_rate` |

   ---

   ### Defensive Plays

   | Column | Description / Calculation | Data Type | Status |
   | :--- | :--- | :--- | :--- |
   | Tkl_p90 | Number of players tackled per 90 minutes | Per-90 Rate | Active Feature |
   | TklDef3rd_p90 | Tackles made in defensive third per 90 | Per-90 Rate | Active Feature |
   | TklMid3rd_p90 | Tackles made in middle third per 90 | Per-90 Rate | Active Feature |
   | TklAtt3rd_p90 | Tackles made in attacking third per 90 (high-press tackling) | Per-90 Rate | Active Feature |
   | TklDri_p90 | Number of dribblers tackled per 90 | Per-90 Rate | Active Feature |
   | TklDriAtt_p90 | Dribble challenges contested (tackles + times dribbled past) per 90 | Per-90 Rate | Active Feature |
   | TklDri% | Percentage of dribblers tackled: $\frac{\text{TklDri}}{\text{TklDriAtt}} \times 100$ | Percentage (0–100) | Active Feature |
   | TklDriPast_p90 | Number of times dribbled past by an opponent per 90 | Per-90 Rate | Active Feature |
   | Blocks_p90 | Total shots and passes blocked per 90 | Per-90 Rate | Active Feature |
   | BlkSh_p90 | Shots blocked by standing in path per 90 | Per-90 Rate | Active Feature (Yeo-Johnson transformed) |
   | BlkPass_p90 | Passes blocked by standing in path per 90 | Per-90 Rate | Active Feature |
   | Int_p90 | Interceptions per 90 minutes | Per-90 Rate | Active Feature |
   | Clr_p90 | Clearances per 90 minutes | Per-90 Rate | Active Feature (Yeo-Johnson transformed) |
   | Recov_p90 | Loose balls recovered per 90 minutes | Per-90 Rate | Active Feature |
   | Tkl_success% | Tackle retention rate: $\frac{\text{TklWon\_p90}}{\text{Tkl\_p90}}$ (share of tackles won by team) | Percentage (0–1) | Engineered (Active) |
   | BlkShSv_p90 | Goal-bound shots blocked (saves by non-GK) per 90 | Per-90 Rate | Retired to Metadata |
   | Err_p90 | Mistakes leading to an opponent shot per 90 | Per-90 Rate | Retired to Metadata |
   | PKcon_p90 | Penalty kicks conceded per 90 minutes | Per-90 Rate | Retired to Metadata |
   | OG_p90 | Own goals scored per 90 minutes | Per-90 Rate | Retired to Metadata |

   #### Pruned / Retired Defensive Features
   | Column | Original Description | Reason for Pruning / Retirement | Replacement / Covered By |
   | :--- | :--- | :--- | :--- |
   | `TklWon_p90`, `TklW_p90` | Tackles won / team won possession per 90 | Highly collinear with `Tkl_p90` ($r > 0.95$); replaced by tackle win rate. | `Tkl_p90`, `Tkl_success%` |
   | `Tkl+Int_p90` | Tackles plus interceptions per 90 | Linear combination of `Tkl_p90` and `Int_p90`. | `Tkl_p90`, `Int_p90` |
   | `BlkShSv_p90` | Goal-line saves by outfield player per 90 | 88.4% zero-inflated; extreme outlier metric isolated to deep-block centre-backs. | `BlkSh_p90`, `Clr_p90` |
   | `Err_p90` | Errors leading to opponent shots per 90 | 72.8% zero-inflated; single-season stochastic noise. Underlying ball security is captured by continuous turnover stats. | `CarMis_p90`, `CarDis_p90`, `PasPress_p90`, `TouDefPen_p90` |
   | `PKcon_p90` | Penalties conceded per 90 | 77.0% zero-inflated; heavily dependent on referee/team siege context. Defender rashness is captured by continuous metrics. | `Fls_p90`, `card_points_p90`, `TklDriPast_p90`, `TklDri%` |
   | `OG_p90` | Own goals per 90 | 92.9% zero-inflated; pure stochastic noise over one season. | N/A |

   ---

   ### Aerial Ability

   | Column | Description / Calculation | Data Type | Status |
   | :--- | :--- | :--- | :--- |
   | AerWon% | Aerial duels won percentage: $\frac{\text{AerWon}}{\text{AerWon} + \text{AerLost}} \times 100$ | Percentage (0–100) | Active Feature |
   | AerWon_p90 | Aerial duels won per 90 minutes | Per-90 Rate | Active Feature (Yeo-Johnson transformed) |

   #### Pruned Aerial Ability Features
   | Column | Original Description | Reason for Pruning | Replacement / Covered By |
   | :--- | :--- | :--- | :--- |
   | `AerLost_p90` | Aerial duels lost per 90 | Redundant with aerial duel volume and win rate (`AerWon%`). | `AerWon%`, `AerWon_p90` |

   ---

   ### Pressures

   | Column | Description / Calculation | Data Type | Status |
   | :--- | :--- | :--- | :--- |
   | Press% | Successful pressure percentage: $\frac{\text{PresSucc}}{\text{Press}} \times 100$ | Percentage (0–100) | Active Feature |
   | Press_p90 | Total pressing actions per 90 minutes | Per-90 Rate | Active Feature |
   | PresDef3rd_p90 | Pressures applied in defensive third per 90 | Per-90 Rate | Active Feature |
   | PresMid3rd_p90 | Pressures applied in middle third per 90 | Per-90 Rate | Active Feature |
   | PresAtt3rd_p90 | Pressures applied in attacking third per 90 | Per-90 Rate | Active Feature |
   | forward_pressing_index | Spatial pressing bias: $\frac{\text{PresAtt3rd\_p90} - \text{PresDef3rd\_p90}}{\text{Press\_p90}}$ (range $-1.0$ to $+1.0$) | Continuous (-1 to +1) | Engineered (Active) |

   #### Pruned Pressures Features
   | Column | Original Description | Reason for Pruning | Replacement / Covered By |
   | :--- | :--- | :--- | :--- |
   | `PresSucc_p90` | Successful pressures per 90 | Almost perfectly collinear with `Press_p90` ($r > 0.94$) and redundant with `Press%`. | `Press_p90`, `Press%` |

   ---

   ### Involvement

   | Column | Description / Calculation | Data Type | Status |
   | :--- | :--- | :--- | :--- |
   | Touches_p90 | Total ball touches per 90 minutes | Per-90 Rate | Active Feature |
   | TouDefPen_p90 | Touches in defensive penalty area per 90 | Per-90 Rate | Active Feature (Yeo-Johnson transformed) |
   | TouAttPen_p90 | Touches in attacking penalty area per 90 | Per-90 Rate | Active Feature (Yeo-Johnson transformed) |
   | RecTarg_p90 | Number of times targeted with a pass per 90 | Per-90 Rate | Active Feature |
   | Rec% | Percentage of targeted passes successfully received: $\frac{\text{Rec}}{\text{RecTarg}} \times 100$ | Percentage (0–100) | Active Feature (Yeo-Johnson transformed) |
   | forward_touch_index | Spatial touch bias: $\frac{\text{TouAtt3rd\_p90} - \text{TouDef3rd\_p90}}{\text{Touches\_p90}}$ (range $-1.0$ to $+1.0$) | Continuous (-1 to +1) | Engineered (Active) |

   #### Pruned Involvement Features
   | Column | Original Description | Reason for Pruning | Replacement / Covered By |
   | :--- | :--- | :--- | :--- |
   | `Rec_p90` | Passes received per 90 | Collinear with `Touches_p90` and `RecTarg_p90` ($r > 0.98$). | `Touches_p90`, `RecTarg_p90`, `Rec%` |
   | `TouDef3rd_p90` | Touches in defensive third per 90 | Collinear with `TouDefPen_p90`; spatial position captured by index. | `TouDefPen_p90`, `forward_touch_index` |
   | `TouMid3rd_p90` | Touches in middle third per 90 | Highly collinear with total touches ($r > 0.92$); captured by touch index. | `Touches_p90`, `forward_touch_index` |
   | `TouAtt3rd_p90` | Touches in attacking third per 90 | Collinear with `TouAttPen_p90`; spatial position captured by index. | `TouAttPen_p90`, `forward_touch_index` |

   ---

   ### Dribbling

   | Column | Description / Calculation | Data Type | Status |
   | :--- | :--- | :--- | :--- |
   | DriSucc% | Percentage of successful dribbles: $\frac{\text{DriSucc}}{\text{DriAtt}} \times 100$ | Percentage (0–100) | Active Feature |
   | DriPast_p90 | Opponents successfully dribbled past per 90 | Per-90 Rate | Active Feature (Yeo-Johnson transformed) |
   | DriMegs_p90 | Nutmegs completed per 90 | Per-90 Rate | Active Feature (Yeo-Johnson transformed) |
   | Carries_p90 | Total ball carries per 90 minutes | Per-90 Rate | Active Feature |
   | CarPrgDist_p90 | Progressive carrying distance in yards towards opponent goal per 90 | Per-90 Rate | Active Feature |
   | CarProg_p90 | Progressive carries ($\ge 5$ yds forward or into penalty box) per 90 | Per-90 Rate | Active Feature |
   | Car3rd_p90 | Carries entering the attacking final third per 90 | Per-90 Rate | Active Feature |
   | CPA_p90 | Carries into the 18-yard penalty box per 90 | Per-90 Rate | Active Feature (Yeo-Johnson transformed) |
   | CarMis_p90 | Miscontrols (failed attempts to control ball) per 90 | Per-90 Rate | Active Feature |
   | CarDis_p90 | Dispossessions (tackled while controlling ball) per 90 | Per-90 Rate | Active Feature |
   | Fld_p90 | Fouls drawn per 90 minutes | Per-90 Rate | Active Feature |
   | CarProg% | Progressive carry share: $\frac{\text{CarProg\_p90}}{\text{Carries\_p90}}$ | Percentage (0–1) | Engineered (Active) |

   #### Pruned Dribbling Features
   | Column | Original Description | Reason for Pruning | Replacement / Covered By |
   | :--- | :--- | :--- | :--- |
   | `DriSucc_p90` | Successful dribbles per 90 | Near-perfect collinearity with `DriPast_p90` ($r > 0.99$); redundant with `DriSucc%`. | `DriPast_p90`, `DriSucc%` |
   | `DriAtt_p90` | Dribbles attempted per 90 | Collinear with `DriPast_p90` ($r > 0.96$); redundant with `DriSucc%`. | `DriPast_p90`, `DriSucc%` |
   | `CarTotDist_p90` | Total carrying distance per 90 | Highly collinear with `Carries_p90` ($r > 0.95$); progressive intent captured by `CarPrgDist_p90`. | `Carries_p90`, `CarPrgDist_p90` |

   ---

   ### Discipline

   | Column | Description / Calculation | Data Type | Status |
   | :--- | :--- | :--- | :--- |
   | Fls_p90 | Fouls committed per 90 minutes | Per-90 Rate | Active Feature |
   | card_points_p90 | UEFA Fair Play discipline index: $1.0 \times \text{CrdY\_p90} + 3.0 \times \text{CrdR\_p90}$, Yeo-Johnson transformed | Continuous | Engineered (Active, Yeo-Johnson transformed) |
   | CrdY_p90 | Yellow cards received per 90 minutes | Per-90 Rate | Retired to Metadata |
   | CrdR_p90 | Red cards received per 90 minutes | Per-90 Rate | Retired to Metadata |
   | 2CrdY_p90 | Second yellow cards received per 90 minutes | Per-90 Rate | Retired to Metadata |

   #### Pruned / Retired Discipline Features
   | Column | Original Description | Reason for Retirement to Metadata | Replacement / Covered By |
   | :--- | :--- | :--- | :--- |
   | `CrdY_p90` | Yellow cards per 90 | Subsumed into UEFA Fair Play discipline index `card_points_p90`. | `card_points_p90` |
   | `CrdR_p90` | Red cards per 90 | 99.1% zero-inflated; subsumed into `card_points_p90` (reduces zero-inflation from ~99% to ~6%). | `card_points_p90` |
   | `2CrdY_p90` | Second yellow cards per 90 | 99.5% zero-inflated; second yellows are already counted inside `CrdR_p90` in raw FBref data (double-counting). | `card_points_p90` |

   ---

   ## Dataset Parity Summary

   | Artefact | Total Columns | Description                                                                                                                                                                                                                            |
   | :--- | :--- |:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
   | **`data/processed/player_featureset.csv`** | **126** | 16 descriptive context columns + 110 clean performance metrics (including 11 initial engineered metrics).                                                                                                                              |
   | **`data/processed/player_metadata.csv`** | **30** | 16 descriptive context columns + 14 retired sparse performance metrics (`COLS_TO_METADATA`).                                                                                                                                           |
   | **`data/processed/player_features_scaled.csv`** | **100** | `player_identifier` join key + **99 standardized numeric modelling features** (32 transformed via Yeo-Johnson reshape step + 1 engineered transformed `card_points_p90` + 2 binary taker indicators + 64 standard continuous metrics). |
   | **`data/processed/player_featureset_preprocessed.csv`** | **123** | 30 metadata columns combined with 99 scaled modelling features (joined on player index).                                                                                                                                               |
   | **Total Pruned Raw Metrics** | **38** | Columns dropped across the featureset and preprocessing pipelines to eliminate collinearity, duplicate definitions, and stochastic noise.                                                                                              |

