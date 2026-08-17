### **Project Objective**: 
Gather football player and team data to create a player scouting dashboard, 
which utilises data analyses and Machine Learning to identify player architects, 
and lesser-known players that may fit these.
---

### **Techniques & Project Plan**:
- Data gathering, exploring multiple potential sources
- Exploratory analysis of player stats and performance
- Unsupervised learning to identify player architects
- Supervised learning to predict future player value
  - Need to consider how to handle uncertainty. 
  - Especially as 'value' is very subjective, and some players may remain undiscovered.
---

### **Data Sources**:
Primary sources:
- FBref
- Transfermarkt
- [StatsBomb open data](https://github.com/hudl/open-data)

Secondary sources:
- [FBref player stats '21/22-'22/23 (pre-compiled on Kaggle)](https://www.kaggle.com/datasets/vivovinco/20222023-football-player-stats)
- [Transfermarkt Data (pre-scaped on Kaggle)](https://www.kaggle.com/datasets/davidcariboo/player-scores?select=game_lineups.csv)
- [FBref, Transfermarkt, Understat (via R package)](https://github.com/JaseZiv/worldfootballR)
- [Similar to above, but Python](https://github.com/ian-shepherd/reus)
- [ggshaker, an R package for using FBRef and Understat data](https://ggshaker.github.io/)

Other resources:
- [How to extract data from FBref tutorial](https://www.youtube.com/watch?v=fuNQRKSAwWg)
- [Useful sport analysis Python packages](https://docs.google.com/spreadsheets/d/1LPe8xYduoep9qCrNzBGdJHaHZ8dnmdHNnu7UXZKzawU/edit?gid=1127780030#gid=1127780030)