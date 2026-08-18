# Data Dictionary

This data dictionary provides a comprehensive overview of the dataset, which contains player statistics for the 2021-2022 football season. The data is sourced from [FBRef](https://fbref.com/en/comps/Big5/Big-5-European-Leagues-Stats).

## Player Details

| Name   | Description                               | Type        | Aggregation                  |
|--------|-------------------------------------------|-------------|------------------------------|
| Rk     | Rank                                      | Qualitative | `Drop Column`                |
| Player | Player's name                             | Qualitative | `Unique`                     |
| Nation | Player's nation                           | Qualitative | `Unique`                     |
| Pos    | Position                                  | Qualitative | `Concat`                     |
| Squad  | Squad                                     | Qualitative | `Array Agg`                  |
| Comp   | Competition                               | Qualitative | `Array Agg & One-hot-encode` |
| Age    | Player's age                              | Qualitative | `MAX`                        |
| Born   | Year born                                 | Qualitative | `Unique`                     |

## Playing Time

| Name  | Description                                                                                                   | Type    | Aggregation                                                              |
|-------|---------------------------------------------------------------------------------------------------------------|---------|--------------------------------------------------------------------------|
| MP    | Matches Played                                                                                                | Numeric | `SUM`                                                                    |
| Starts| Games started                                                                                                 | Numeric | `SUM`                                                                    |
| Min   | Minutes played                                                                                                | Numeric | `SUM`                                                                    |
| 90s   | Minutes played divided by 90                                                                                  | Numeric | Recalculate: `SUM(Min) / 90`                                             |
| Mn/MP | Minutes per match                                                                                             | Numeric | Recalculate: `SUM(Min) / SUM(MP)`                                        |
| Min%  | Minutes played as a percentage of total team minutes                                                          | Numeric | Drop column (Requires total team minutes) |
| Compl | Number of matches where player played the full 90 minutes                                                     | Numeric | `SUM`                                                                    |
| onG   | Goals scored by team while player on pitch                                                                    | Numeric | `SUM`                                                                    |
| onGA  | Goals conceded by team while player on pitch                                                                  | Numeric | `SUM`                                                                    |
| +/-   | Goal difference while player on pitch (`onG` - `onGA`)                                                        | Numeric | Recalculate: `SUM(onG) - SUM(onGA)`                                      |
| +/-90 | Goal difference per 90 minutes while player on pitch                                                          | Numeric | Recalculate: `(SUM(onG) - SUM(onGA)) / (SUM(Min) / 90)`                   |
| On-Off| `+/-` per 90 minutes minus `+/-` per 90 minutes while player is off pitch                                       | Numeric | Drop column (Requires team off-pitch stats) |

## Performance - Standard

| Name      | Description                                          | Type    | Aggregation                                           |
|-----------|------------------------------------------------------|---------|-------------------------------------------------------|
| Gls       | Goals                                                | Numeric | `SUM`                                                 |
| Ast       | Assists                                              | Numeric | `SUM`                                                 |
| G-PK      | Non-penalty goals                                    | Numeric | Recalculate: `SUM(Gls) - SUM(PK)`                     |
| PK        | Penalty kicks made                                   | Numeric | `SUM`                                                 |
| PKatt     | Penalty kicks attempted                              | Numeric | `SUM`                                                 |
| CrdY      | Yellow cards                                         | Numeric | `SUM`                                                 |
| CrdR      | Red cards                                            | Numeric | `SUM`                                                 |
| xG        | Expected goals                                       | Numeric | `SUM`                                                 |
| npxG      | Non-penalty expected goals                           | Numeric | `SUM`                                                 |
| xAG       | Expected assisted goals                              | Numeric | `SUM`                                                 |
| npxG+xAG  | Non-penalty expected goals plus expected assisted goals| Numeric | Recalculate: `SUM(npxG) + SUM(xAG)`                   |
| PrgC      | Progressive carries                                  | Numeric | `SUM`                                                 |
| PrgP      | Progressive passes                                   | Numeric | `SUM`                                                 |
| PrgR      | Progressive passes received                          | Numeric | `SUM`                                                 |
| Gls.1     | Goals per 90 minutes                                 | Numeric | Recalculate: `SUM(Gls) / (SUM(Min) / 90)`             |
| Ast.1     | Assists per 90 minutes                               | Numeric | Recalculate: `SUM(Ast) / (SUM(Min) / 90)`             |
| G+A       | Goals and assists                                    | Numeric | Recalculate: `SUM(Gls) + SUM(Ast)`                    |
| G-PK.1    | Non-penalty goals per 90 minutes                     | Numeric | Recalculate: `(SUM(Gls) - SUM(PK)) / (SUM(Min) / 90)` |
| G+A-PK    | Non-penalty goals and assists                        | Numeric | Recalculate: `SUM(Gls) + SUM(Ast) - SUM(PK)`          |
| xG.1      | Expected goals per 90 minutes                        | Numeric | Recalculate: `SUM(xG) / (SUM(Min) / 90)`             |
| xAG.1     | Expected assisted goals per 90 minutes               | Numeric | Recalculate: `SUM(xAG) / (SUM(Min) / 90)`            |
| xG+xAG    | Expected goals and expected assisted goals           | Numeric | Recalculate: `SUM(xG) + SUM(xAG)`                     |
| npxG.1    | Non-penalty expected goals per 90 minutes            | Numeric | Recalculate: `SUM(npxG) / (SUM(Min) / 90)`           |
| npxG+xAG.1| Non-penalty expected goals and expected assisted goals per 90 minutes | Numeric | Recalculate: `(SUM(npxG) + SUM(xAG)) / (SUM(Min) / 90)` |

## Performance - Shooting

| Name    | Description                               | Type    | Aggregation                                                         |
|---------|-------------------------------------------|---------|---------------------------------------------------------------------|
| Sh      | Shots total                               | Numeric | `SUM`                                                               |
| SoT     | Shots on target                           | Numeric | `SUM`                                                               |
| SoT%    | Shots on target percentage                | Numeric | Recalculate: `SUM(SoT) / SUM(Sh) * 100`                              |
| Sh/90   | Shots per 90 minutes                      | Numeric | Recalculate: `SUM(Sh) / (SUM(Min) / 90)`                             |
| SoT/90  | Shots on target per 90 minutes            | Numeric | Recalculate: `SUM(SoT) / (SUM(Min) / 90)`                            |
| G/Sh    | Goals per shot                            | Numeric | Recalculate: `SUM(Gls) / SUM(Sh)`                                   |
| G/SoT   | Goals per shot on target                  | Numeric | Recalculate: `SUM(Gls) / SUM(SoT)`                                  |
| Dist    | Average shot distance                     | Numeric | Recalculate: Weighted average using Shots. `SUM(Dist * Sh) / SUM(Sh)` |
| FK      | Free kicks taken as shots                 | Numeric | `SUM`                                                               |
| npxG/Sh | Non-penalty expected goals per shot       | Numeric | Recalculate: `SUM(npxG) / SUM(Sh)`                                  |
| G-xG    | Goals minus expected goals                | Numeric | Recalculate: `SUM(Gls) - SUM(xG)`                                   |
| np:G-xG | Non-penalty goals minus non-penalty expected goals | Numeric | Recalculate: `(SUM(Gls) - SUM(PK)) - SUM(npxG)`                     |

## Performance - Passing

| Name          | Description                               | Type    | Aggregation                             |
|---------------|-------------------------------------------|---------|-----------------------------------------|
| Cmp           | Passes completed                          | Numeric | `SUM`                                   |
| Att           | Passes attempted                          | Numeric | `SUM`                                   |
| Cmp%          | Pass completion percentage                | Numeric | Recalculate: `SUM(Cmp) / SUM(Att) * 100` |
| TotDist       | Total distance of completed passes        | Numeric | `SUM`                                   |
| PrgDist       | Progressive distance of completed passes    | Numeric | `SUM`                                   |
| Cmp (Short)   | Completed short passes (5-15 yards)       | Numeric | `SUM`                                   |
| Att (Short)   | Attempted short passes                    | Numeric | `SUM`                                   |
| Cmp% (Short)  | Short pass completion percentage          | Numeric | Recalculate: `SUM(Cmp (Short)) / SUM(Att (Short)) * 100` |
| Cmp (Medium)  | Completed medium passes (15-30 yards)     | Numeric | `SUM`                                   |
| Att (Medium)  | Attempted medium passes                   | Numeric | `SUM`                                   |
| Cmp% (Medium) | Medium pass completion percentage         | Numeric | Recalculate: `SUM(Cmp (Medium)) / SUM(Att (Medium)) * 100` |
| Cmp (Long)    | Completed long passes (>30 yards)         | Numeric | `SUM`                                   |
| Att (Long)    | Attempted long passes                     | Numeric | `SUM`                                   |
| Cmp% (Long)   | Long pass completion percentage           | Numeric | Recalculate: `SUM(Cmp (Long)) / SUM(Att (Long)) * 100` |
| Ast           | Assists                                   | Numeric | `SUM`                                   |
| xAG           | Expected assisted goals                   | Numeric | `SUM`                                   |
| xA            | Expected assists                          | Numeric | `SUM`                                   |
| A-xAG         | Assists minus expected assisted goals     | Numeric | Recalculate: `SUM(Ast) - SUM(xAG)`      |
| KP            | Key passes                                | Numeric | `SUM`                                   |
| 1/3           | Passes that enter the final third         | Numeric | `SUM`                                   |
| PPA           | Passes into the penalty area              | Numeric | `SUM`                                   |
| CrsPA         | Crosses into the penalty area             | Numeric | `SUM`                                   |
| PrgP          | Progressive passes                        | Numeric | `SUM`                                   |

## Performance - Pass Types

| Name | Description               | Type    | Aggregation |
|------|---------------------------|---------|-------------|
| Att  | Passes attempted          | Numeric | `SUM`       |
| Live | Live-ball passes          | Numeric | `SUM`       |
| Dead | Dead-ball passes          | Numeric | `SUM`       |
| FK   | Free-kick passes          | Numeric | `SUM`       |
| TB   | Through balls             | Numeric | `SUM`       |
| Sw   | Switches                  | Numeric | `SUM`       |
| Crs  | Crosses                   | Numeric | `SUM`       |
| TI   | Throw-ins                 | Numeric | `SUM`       |
| CK   | Corner kicks              | Numeric | `SUM`       |
| In   | In-swinging corner kicks  | Numeric | `SUM`       |
| Out  | Out-swinging corner kicks | Numeric | `SUM`       |
| Str  | Straight corner kicks     | Numeric | `SUM`       |
| Cmp  | Passes completed          | Numeric | `SUM`       |
| Off  | Offsides                  | Numeric | `SUM`       |
| Blocks| Passes blocked by opponent| Numeric | `SUM`       |

## Performance - Goal and Shot Creation

| Name      | Description                               | Type    | Aggregation                                  |
|-----------|-------------------------------------------|---------|----------------------------------------------|
| SCA       | Shot-creating actions                     | Numeric | `SUM`                                        |
| SCA90     | Shot-creating actions per 90 minutes      | Numeric | Recalculate: `SUM(SCA) / (SUM(Min) / 90)`    |
| PassLive  | Live-ball passes leading to a shot        | Numeric | `SUM`                                        |
| PassDead  | Dead-ball passes leading to a shot        | Numeric | `SUM`                                        |
| TO        | Take-ons leading to a shot                | Numeric | `SUM`                                        |
| Sh        | Shots leading to another shot             | Numeric | `SUM`                                        |
| Fld       | Fouls drawn leading to a shot             | Numeric | `SUM`                                        |
| Def       | Defensive actions leading to a shot       | Numeric | `SUM`                                        |
| GCA       | Goal-creating actions                     | Numeric | `SUM`                                        |
| GCA90     | Goal-creating actions per 90 minutes      | Numeric | Recalculate: `SUM(GCA) / (SUM(Min) / 90)`    |
| PassLive.1| Live-ball passes leading to a goal        | Numeric | `SUM`                                        |
| PassDead.1| Dead-ball passes leading to a goal        | Numeric | `SUM`                                        |
| TO.1      | Take-ons leading to a goal                | Numeric | `SUM`                                        |
| Sh.1      | Shots leading to another goal             | Numeric | `SUM`                                        |
| Fld.1     | Fouls drawn leading to a goal             | Numeric | `SUM`                                        |
| Def.1     | Defensive actions leading to a goal       | Numeric | `SUM`                                        |

## Performance - Defensive Actions

| Name                | Description                               | Type    | Aggregation                                           |
|---------------------|-------------------------------------------|---------|-------------------------------------------------------|
| Tkl                 | Tackles                                   | Numeric | `SUM`                                                 |
| TklW                | Tackles won                               | Numeric | `SUM`                                                 |
| Def 3rd             | Tackles in defensive 3rd                  | Numeric | `SUM`                                                 |
| Mid 3rd             | Tackles in middle 3rd                     | Numeric | `SUM`                                                 |
| Att 3rd             | Tackles in attacking 3rd                  | Numeric | `SUM`                                                 |
| Tkl (vs Dribblers)  | Tackles vs dribblers                      | Numeric | `SUM`                                                 |
| Att (vs Dribblers)  | Dribblers tackled                         | Numeric | `SUM`                                                 |
| Tkl% (vs Dribblers) | Percentage of dribblers tackled           | Numeric | Recalculate: `SUM(Tkl (vs Dribblers)) / SUM(Att (vs Dribblers)) * 100` |
| Lost (vs Dribblers) | Dribbled past by an opponent              | Numeric | `SUM`                                                 |
| Blocks              | Blocks                                    | Numeric | `SUM`                                                 |
| Sh                  | Shots blocked                             | Numeric | `SUM`                                                 |
| Pass                | Passes blocked                            | Numeric | `SUM`                                                 |
| Int                 | Interceptions                             | Numeric | `SUM`                                                 |
| Tkl+Int             | Tackles and interceptions                 | Numeric | Recalculate: `SUM(Tkl) + SUM(Int)`                    |
| Clr                 | Clearances                                | Numeric | `SUM`                                                 |
| Err                 | Errors leading to an opponent's shot      | Numeric | `SUM`                                                 |

## Performance - Possession

| Name               | Description                               | Type    | Aggregation                                           |
|--------------------|-------------------------------------------|---------|-------------------------------------------------------|
| Touches            | Number of touches                         | Numeric | `SUM`                                                 |
| Def Pen            | Touches in defensive penalty area         | Numeric | `SUM`                                                 |
| Def 3rd            | Touches in defensive 3rd                  | Numeric | `SUM`                                                 |
| Mid 3rd            | Touches in middle 3rd                     | Numeric | `SUM`                                                 |
| Att 3rd            | Touches in attacking 3rd                  | Numeric | `SUM`                                                 |
| Att Pen            | Touches in attacking penalty area         | Numeric | `SUM`                                                 |
| Live               | Live-ball touches                         | Numeric | `SUM`                                                 |
| Att (Take-Ons)     | Attempted take-ons                        | Numeric | `SUM`                                                 |
| Succ (Take-Ons)    | Successful take-ons                       | Numeric | `SUM`                                                 |
| Succ% (Take-Ons)   | Successful take-on percentage             | Numeric | Recalculate: `SUM(Succ (Take-Ons)) / SUM(Att (Take-Ons)) * 100` |
| Tkld% (Take-Ons)   | Percentage of take-ons tackled by an opponent | Numeric | Recalculate: `SUM(Tkld (Take-Ons)) / SUM(Att (Take-Ons)) * 100` |
| Carries            | Number of carries                         | Numeric | `SUM`                                                 |
| TotDist            | Total carry distance                      | Numeric | `SUM`                                                 |
| PrgDist            | Progressive carry distance                | Numeric | `SUM`                                                 |
| PrgC               | Progressive carries                       | Numeric | `SUM`                                                 |
| 1/3                | Carries into the final third              | Numeric | `SUM`                                                 |
| CPA                | Carries into the penalty area             | Numeric | `SUM`                                                 |
| Mis                | Miscontrols                               | Numeric | `SUM`                                                 |
| Dis                | Dispossessed                              | Numeric | `SUM`                                                 |
| Rec                | Passes received                           | Numeric | `SUM`                                                 |
| PrgR               | Progressive passes received               | Numeric | `SUM`                                                 |

## Performance - Miscellaneous

| Name                 | Description                               | Type    | Aggregation                                           |
|----------------------|-------------------------------------------|---------|-------------------------------------------------------|
| CrdY                 | Yellow cards                              | Numeric | `SUM`                                                 |
| CrdR                 | Red cards                                 | Numeric | `SUM`                                                 |
| 2CrdY                | Second yellow card                        | Numeric | `SUM`                                                 |
| Fls                  | Fouls committed                           | Numeric | `SUM`                                                 |
| Fld                  | Fouls drawn                               | Numeric | `SUM`                                                 |
| Off                  | Offsides                                  | Numeric | `SUM`                                                 |
| Crs                  | Crosses                                   | Numeric | `SUM`                                                 |
| Int                  | Interceptions                             | Numeric | `SUM`                                                 |
| TklW                 | Tackles won                               | Numeric | `SUM`                                                 |
| PKwon                | Penalty kicks won                         | Numeric | `SUM`                                                 |
| PKcon                | Penalty kicks conceded                    | Numeric | `SUM`                                                 |
| OG                   | Own goals                                 | Numeric | `SUM`                                                 |
| Recov                | Recoveries                                | Numeric | `SUM`                                                 |
| Won (Aerial Duels)   | Aerial duels won                          | Numeric | `SUM`                                                 |
| Lost (Aerial Duels)  | Aerial duels lost                         | Numeric | `SUM`                                                 |
| Won% (Aerial Duels)  | Percentage of aerial duels won            | Numeric | Recalculate: `SUM(Won (Aerial Duels)) / (SUM(Won (Aerial Duels)) + SUM(Lost (Aerial Duels))) * 100` |
