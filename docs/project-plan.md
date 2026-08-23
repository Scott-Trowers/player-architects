### **Project Objective**: 
Gather football player and team data to create a player scouting dashboard, 
which utilises data analyses and Machine Learning to identify player architects, 
and lesser-known players that may fit these.

- Identify player profiles from performance statistics. This enables profile matching as a scouting tool. 
- Furthermore, the early-career statistics of well-established high-performers can be profiles, and the metrics of current
young players can be compared, to identify players with the potential to grow into high-performing archetypes.


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


### Project Plan:

Milestones:
1. Data Prep
  - Import data and create a data dictionary
  - Check data quality (data types, missingness, duplicates)
2. EDA
  - Qualitative EDA (counts & distributions)
  - Quantitative EDA
    - Descriptive exploration (distribution, uniqueness)
    - Skew & Kurtosis
    - Outliers
    - Relationships & Redundant Columns (correlation, heirarchical clustering)
    - Check scaling
  - Combined EDA (check for relationships between Qualitative and Quantitative data)
3. Cluster Analysis
  - Dimension Reduction (possibly on manually selected metric groups)
  - Clustering
    - Baseline: K-means
    - Additional: GMM, Heirarchical, HDBSCAN, possibly Spectral
    - Validation and Interpretation (can compare to reduced and original dimensions)
    - Enrichment & Analysis (visualisation, compare to qualitative features, identify high-profile players)
  - If clusters form too strongly on position, may need to split the data up around this and re-perform.
4. Player Profile Matching
  - Take a reference profile (either a single established player, or an archetype from clustering)
  - Utilise a KNN query to rank all datapoints by distance to this reference point (k = desired shortlist size)
  - Compare & evaluate distance metrics:
    - Mahalabonis, Cosine similarity, Euclidean Distance on PCs
  - Shortlist candidates, and player value data from Transfermarkt to enable rough identification of under-rated players
5. High Potential Profile Matching
  - Same as (4.), but takes established high-performers, finds early-career metrics, and compares to current young players
  - Backtest against other established high-performers to validate performance
6. Convert into re-usable pipelines
7. Develop Dashboard/UI
  - Qualitative features as filters
  - Cluster visualisation (t-SNE, UMAP, PCA)
  - Clear visualisation & interpretation of archetypes
    - Top players for each, and contributing metrics
    - Build Radar graphs from most important metrics, and then evaluate players from graph area?
  - Any player can be clicked on and visualisation of their metrics displayed (radar graph and bars, similar players section and list of archetypes (and % match for both))
  - Multiple players can be directly compared

Future Phases:
 - Convert to a supervised learning problem, either via named labels, or estimated player values. 
   - Then can use metric learning, RF proximity, autoencoder embeddings to identify under-valued players.
   - Enables feature importance to highlight which metrics drive high-performance per archetype
 - Use time-based clustering (e.g. Dynamic Time-Warped) to analyse how high-performer's metrics evolved over time, and find young players who match the early trajectory of these
