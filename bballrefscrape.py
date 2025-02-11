import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def get_drafted_players(url):
    """Scrape players drafted in 2018 with their college information."""
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    players = []
    
    table = soup.find('table', {'id': 'stats'})
    for row in table.find('tbody').find_all('tr', class_=lambda x: x != 'thead'):
        cols = row.find_all('td')
        if not cols:
            continue
        name_tag = row.find('td', {'data-stat': 'player'}).find('a')
        college_tag = row.find('td', {'data-stat': 'college_name'})
        
        if name_tag and college_tag and college_tag.text.strip():
            players.append((name_tag.text.strip(), college_tag.text.strip()))
    
    return players

def format_player_url(player_name, college_url_base):
    """Format player URL based on their name."""
    formatted_name = player_name.lower().replace(" ", "-")
    return f"{college_url_base}players/{formatted_name}-1.html"

def get_college_stats(player_name, college_url_base):
    """Scrape college stats (Totals and Advanced) for a given player."""
    player_url = format_player_url(player_name, college_url_base)
    response = requests.get(player_url)
    if response.status_code != 200:
        return None  # Page not found
    
    player_soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract Totals table
    totals_table = player_soup.find("div", attrs={"id": "switcher_players_totals"}).find('table')
    totals_df = pd.read_html(str(totals_table))[0] if totals_table else pd.DataFrame()
    
    # Extract Advanced table
    advanced_table = player_soup.find("div", attrs={"id": "switcher_players_advanced"}).find('table')
    advanced_df = pd.read_html(str(advanced_table))[0] if advanced_table else pd.DataFrame()
    
    if not totals_df.empty and not advanced_df.empty:
        totals_df = totals_df.add_prefix("Totals_")
        advanced_df = advanced_df.add_prefix("Advanced_")
        combined_df = pd.concat([totals_df, advanced_df], axis=1)
    elif not totals_df.empty:
        combined_df = totals_df.add_prefix("Totals_")
    elif not advanced_df.empty:
        combined_df = advanced_df.add_prefix("Advanced_")
    else:
        combined_df = None
    
    return combined_df

def main():
    draft_url = "https://www.basketball-reference.com/draft/NBA_2018.html"
    college_url_base = "https://www.sports-reference.com/cbb/"
    
    players = get_drafted_players(draft_url)
    all_data = []
    
    for name, college in players:
        print(f"Scraping stats for {name} from {college}...")
        stats_df = get_college_stats(name, college_url_base)
        if stats_df is not None and not stats_df.empty:
            stats_df.insert(0, "Player", name)
            stats_df.insert(1, "College", college)
            all_data.append(stats_df)
        time.sleep(1)  # To avoid getting blocked
    
    final_df = pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()
    #final_df.to_csv("nba_draft_2018_college_stats.csv", index=False)
    #print("Scraping complete. Data saved to CSV file.")
    final_df.head()

if __name__ == "__main__":
    main()
