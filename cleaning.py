import pandas as pd

lebrons = pd.read_csv('lebrons.csv')
college_stats = pd.read_csv('nba_draft_college_stats.csv')

def top_n(df, column, n):
    return df.nlargest(n, column)

lebrons_ordered = lebrons.sort_values(by=['Player', 'Season'], ascending=[True, False])

# Remove rows where 'Totals_Season' is non-numeric
college_stats = college_stats[college_stats['Totals_Season'].str.match(r'^\d{4}-\d{2}$', na=False)]

# Extract the last year from "YYYY-YY" format
college_stats['Year'] = college_stats['Totals_Season'].str.split('-').str[1].astype(int) + 2000  # Convert to full year

# Keep most recent college year
college_stats_best_year = college_stats.sort_values(by=['Player', 'Totals_Season'], ascending=[True, False]).drop_duplicates(subset='Player')
# Keep top 3 Lebron WAR seasons for each player
lebrons_ordered = lebrons.groupby('Player').apply(top_n, 'LEBRON WAR', n=3).reset_index(drop=True)

# Keep players in lebrons who have college stats
for player in lebrons_ordered['Player']:
    if player not in college_stats_best_year['Player'].values:
        lebrons_ordered = lebrons_ordered[lebrons_ordered['Player'] != player]

# Keep players in college_stats who have LEBRON stats
for player in college_stats_best_year['Player']:
    if player not in lebrons_ordered['Player'].values:
        college_stats_best_year = college_stats_best_year[college_stats_best_year['Player'] != player]

# Merge dfs to have each players' mean LEBRON WAR with their college stats, easier for modeling
mean_lebron = lebrons_ordered.groupby('Player')['LEBRON WAR'].mean().reset_index()
mean_lebron.columns = ['Player', 'Mean LEBRON WAR']
merged = pd.merge(college_stats_best_year, mean_lebron, on='Player', how='inner')
merged['Totals_3P%'] = merged['Totals_3P%'].fillna(0)
merged.iloc[256, -3] = 21
merged.iloc[317,-3] = 20

merged = merged.drop(['Totals_Team', 'Totals_Season', 'Totals_Awards', 'Advanced_Season', 'Advanced_Team', 'Advanced_Conf', 'Advanced_Conf', 'Advanced_Class', 'Advanced_Pos', 'Advanced_G', 'Advanced_GS', 'Advanced_MP', 'Advanced_Awards'], axis=1)
merged["Power_Conference"] = [s in ['Big Ten', 'SEC', 'Pac-12', 'ACC', 'Big 12', 'Big East'] for s in merged['Totals_Conf']]
merged = merged[merged['Year'] != 2010]

merged.to_csv("lebron_draft_data.csv", index=False)