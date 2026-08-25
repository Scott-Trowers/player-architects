NB: Column group labels are only loose, as one column may reasonably fall under multiple categories.

_e.g. Crosses could fall under 'Passing' or 'Chance Creation'_

### Player Info

| Column | Description | Data Type |
| :--- | :--- | :--- |
| player_identifier | Unique identifier for the player | Qualitative |
| Player | Player's name | Qualitative |
| Nation | Player's nation | Qualitative |
| Pos | Position | Qualitative |
| Primary_Pos | Primary position of the player (first position listed in raw data, or main position of the club they played the most minutes for if they played for multiple clubs) | Qualitative |
| Age | Player's age | Qualitative |
| Born | Year of birth | Qualitative |
| Num_Pos | Number of positions played by the player | Count |

### Team Info

| Column | Description | Data Type |
| :--- | :--- | :--- |
| Squad | Squad’s name | Qualitative |
| Comp | League that squad occupies | Qualitative |

### Matches played

| Column | Description | Data Type |
| :--- | :--- | :--- |
| MP | Matches played | Count |
| Starts | Matches started | Count |
| Min | Minutes played | Count |
| 90s | Minutes played divided by 90 | Count |

### League Playtime

| Column | Description | Data Type |
| :--- | :--- | :--- |
| Premier League_pct_mins | Percentage of total minutes played in the Premier League | Percentage |
| Ligue 1_pct_mins | Percentage of total minutes played in Ligue 1 | Percentage |
| Bundesliga_pct_mins | Percentage of total minutes played in the Bundesliga | Percentage |
| Serie A_pct_mins | Percentage of total minutes played in Serie A | Percentage |
| La Liga_pct_mins | Percentage of total minutes played in La Liga | Percentage |

### Finishing

| Column | Description | Data Type |
| :--- | :--- | :--- |
| Goals | Goals scored or allowed | Count |
| Shots | Shots total (Does not include penalty kicks) | Count |
| SoT | Shots on target (Does not include penalty kicks) | Count |
| SoT% | Shots on target percentage (Does not include penalty kicks) | Percentage |
| G/Sh | Goals per shot | Ratio |
| G/SoT | Goals per shot on target (Does not include penalty kicks) | Ratio |
| ShoDist | Average distance, in yards, from goal of all shots taken (Does not include penalty kicks) | Average |

### Set Pieces

| Column | Description | Data Type |
| :--- | :--- | :--- |
| ShoFK | Shots from free kicks | Count |
| ShoPK | Penalty kicks made | Count |
| PKatt | Penalty kicks attempted | Count |
| PasDead | Dead-ball passes | Count |
| PasFK | Passes attempted from free kicks | Count |
| ScaPassDead | Completed dead-ball passes that lead to a shot attempt | Count |
| TI | Throw-Ins taken | Count |
| CK | Corner kicks | Count |
| CkIn | Inswinging corner kicks | Count |
| CkOut | Outswinging corner kicks | Count |
| CkStr | Straight corner kicks | Count |
| GcaPassDead | Completed dead-ball passes that lead to a goal | Count |

### Chance Creation

| Column | Description | Data Type |
| :--- | :--- | :--- |
| Assists | Assists | Count |
| PasAss | Passes that directly lead to a shot (assisted shots) | Count |
| ScaPassLive | Completed live-ball passes that lead to a shot attempt | Count |
| GcaPassLive | Completed live-ball passes that lead to a goal | Count |
| GCA | Goal-creating actions | Count |
| SCA | Shot-creating actions | Count |
| ScaDrib | Successful dribbles that lead to a shot attempt | Count |
| ScaSh | Shots that lead to another shot attempt | Count |
| ScaFld | Fouls drawn that lead to a shot attempt | Count |
| ScaDef | Defensive actions that lead to a shot attempt | Count |
| GcaDrib | Successful dribbles that lead to a goal | Count |
| GcaSh | Shots that lead to another goal-scoring shot | Count |
| GcaFld | Fouls drawn that lead to a goal | Count |
| GcaDef | Defensive actions that lead to a goal | Count |
| PKwon | Penalty kicks won | Count |

### Passing

| Column | Description | Data Type |
| :--- | :--- | :--- |
| PasCmp | Passes completed | Count |
| PasAtt | Passes attempted | Count |
| PasTotCmp | Passes completed | Count |
| PasTotAtt | Passes attempted | Count |
| PasTotCmp% | Pass completion percentage | Percentage |
| PasTotDist | Total distance, in yards, that completed passes have traveled in any direction | Count |
| PasTotPrgDist | Total distance, in yards, that completed passes have traveled towards the opponent's goal | Count |
| PasShoCmp | Passes completed (Passes between 5 and 15 yards) | Count |
| PasShoAtt | Passes attempted (Passes between 5 and 15 yards) | Count |
| PasShoCmp% | Pass completion percentage (Passes between 5 and 15 yards) | Percentage |
| PasMedCmp | Passes completed (Passes between 15 and 30 yards) | Count |
| PasMedAtt | Passes attempted (Passes between 15 and 30 yards) | Count |
| PasMedCmp% | Pass completion percentage (Passes between 15 and 30 yards) | Percentage |
| PasLonCmp | Passes completed (Passes longer than 30 yards) | Count |
| PasLonAtt | Passes attempted (Passes longer than 30 yards) | Count |
| PasLonCmp% | Pass completion percentage (Passes longer than 30 yards) | Percentage |
| Pas3rd | Completed passes that enter the 1/3 of the pitch closest to the goal | Count |
| PPA | Completed passes into the 18-yard box | Count |
| CrsPA | Completed crosses into the 18-yard box | Count |
| PasProg | Completed passes that move the ball towards the opponent's goal at least 10 yards from its furthest point in the last six passes, or any completed pass into the penalty area | Count |
| PasLive | Live-ball passes | Count |
| PasBlocks | Blocked by the opponent who was standing it the path | Count |
| TB | Completed pass sent between back defenders into open space | Count |
| Sw | Passes that travel more than 40 yards of the width of the pitch | Count |
| PasCrs | Crosses | Count |
| Crs | Crosses | Count |
| RecProg | Completed passes that move the ball towards the opponent's goal at least 10 yards from its furthest point in the last six passes, or any completed pass into the penalty area | Count |
| PasGround | Ground passes (passes that travel along the ground) | Count |
| PasLow | Low passes (passes that travel above the ground but below shoulder level) | Count |
| PasHigh | High passes (passes that travel above shoulder level) | Count |
| PaswLeft | Left-footed passes attempted | Count |
| PaswRight | Right-footed passes attempted | Count |
| PaswHead | Headed passes attempted | Count |
| PaswOther | Passes attempted with other body parts (e.g. chest, knee) | Count |
| PasPress | Passes attempted while under pressure from an opponent | Count |
| PasInt | Passes attempted that were intercepted by an opponent | Count |
| PasOut | Passes attempted that went out of bounds | Count |

### Positioning

| Column | Description | Data Type |
| :--- | :--- | :--- |
| PasOff | Offsides | Count |
| Off | Offsides | Count |

### Defensive Plays

| Column | Description | Data Type |
| :--- | :--- | :--- |
| Tkl | Number of players tackled | Count |
| TklWon | Tackles in which the tackler's team won possession of the ball | Count |
| TklDef3rd | Tackles in defensive 1/3 | Count |
| TklMid3rd | Tackles in middle 1/3 | Count |
| TklAtt3rd | Tackles in attacking 1/3 | Count |
| TklDri | Number of dribblers tackled | Count |
| TklDriAtt | Number of times dribbled past plus number of tackles | Count |
| TklDri% | Percentage of dribblers tackled | Percentage |
| TklDriPast | Number of times dribbled past by an opposing player | Count |
| Blocks | Number of times blocking the ball by standing in its path | Count |
| BlkSh | Number of times blocking a shot by standing in its path | Count |
| BlkShSv | Number of times blocking a shot that was traveling toward the goal (a save by a non-goalkeeper) | Count |
| BlkPass | Number of times blocking a pass by standing in its path | Count |
| Int | Interceptions | Count |
| Tkl+Int | Number of players tackled plus number of interceptions | Count |
| Clr | Clearances | Count |
| Err | Mistakes leading to an opponent's shot | Count |
| Recov | Number of loose balls recovered | Count |
| TklW | Tackles in which the tackler's team won possession of the ball | Count |
| PKcon | Penalty kicks conceded | Count |
| OG | Own goals | Count |

### Pressures

| Column | Description | Data Type |
| :--- | :--- | :--- |
| Press | Number of times applying pressure to an opposing player who is receiving, carrying or releasing the ball | Count |
| PresSucc | Number of times the team regained possession of the ball within 5 seconds of applying pressure | Count |
| Press% | Successful pressure percentage (percentage of time the team regained possession within 5 seconds of applying pressure) | Percentage |
| PresDef3rd | Pressures in defensive 1/3 | Count |
| PresMid3rd | Pressures in middle 1/3 | Count |
| PresAtt3rd | Pressures in attacking 1/3 | Count |

### Involvement

| Column | Description | Data Type |
| :--- | :--- | :--- |
| Touches | Number of times a player touched the ball. Note: Receiving a pass, then dribbling, then sending a pass counts as one touch | Count |
| TouDefPen | Touches in defensive penalty area | Count |
| TouDef3rd | Touches in defensive 1/3 | Count |
| TouMid3rd | Touches in middle 1/3 | Count |
| TouAtt3rd | Touches in attacking 1/3 | Count |
| TouAttPen | Touches in attacking penalty area | Count |
| TouLive | Live-ball touches. Does not include corner kicks, free kicks, throw-ins, kick-offs, goal kicks or penalty kicks. | Count |
| Rec | Number of times a player successfully received a pass | Count |
| RecTarg | Number of times a player was targeted with a pass | Count |
| Rec% | Percentage of passes targeted at the player that were successfully received | Percentage |

### Dribbling

| Column | Description | Data Type |
| :--- | :--- | :--- |
| DriSucc | Number of successful dribbles (dribbled past an opponent) | Count |
| DriAtt | Number of dribbles attempted | Count |
| DriSucc% | Percentage of completed/successful dribbles | Percentage |
| DriPast | Number of times a player successfully dribbled past an opponent | Count |
| DriMegs | Number of times a player dribbled the ball through an opponent's legs (nutmegs) | Count |
| Carries | Number of times the player controlled the ball with their feet | Count |
| CarTotDist | Total distance, in yards, a player moved the ball while controlling it with their feet, in any direction | Count |
| CarPrgDist | Total distance, in yards, a player moved the ball while controlling it with their feet towards the opponent's goal | Count |
| CarProg | Carries that move the ball towards the opponent's goal at least 5 yards, or any carry into the penalty area | Count |
| Car3rd | Carries that enter the 1/3 of the pitch closest to the goal | Count |
| CPA | Carries into the 18-yard box | Count |
| CarMis | Number of times a player failed when attempting to gain control of a ball | Count |
| CarDis | Number of times a player loses control of the ball after being tackled by an opposing player | Count |
| Fld | Fouls drawn | Count |

### Discipline

| Column | Description | Data Type |
| :--- | :--- | :--- |
| CrdY | Yellow cards | Count |
| CrdR | Red cards | Count |
| 2CrdY | Second yellow card | Count |
| Fls | Fouls committed | Count |

### Aerial Ability

| Column | Description | Data Type |
| :--- | :--- | :--- |
| AerWon | Aerials won | Count |
| AerLost | Aerials lost | Count |
| AerWon% | Percentage of aerials won | Percentage |