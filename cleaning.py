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
