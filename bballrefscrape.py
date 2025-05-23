import requests
from bs4 import BeautifulSoup, Comment
import pandas as pd
import time
import warnings
import html5lib
warnings.simplefilter(action='ignore', category=FutureWarning)

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
        link = row.find('td', {'data-stat': 'player'}).find('a').get('href')
        
        if name_tag and college_tag and college_tag.text.strip():
            players.append((name_tag.text.strip(), college_tag.text.strip(), link))
    
    return players

def get_player_url(link):
    """Format player URL based on their name."""
    nba_response = requests.get('https://www.basketball-reference.com/' + link)
    soup = BeautifulSoup(nba_response.text, 'html.parser')
    container = soup.find('div', attrs={'id':'all_all_college_stats'})
    age = soup.find_all('td', attrs={'data-stat':'age'})
    if len(age) > 0:
        age = int(age[0].text) - 1
    if not container:
        return None
    return [container.find('a').get('href'), age]

def convert_height(s):
    return int(s[0]) * 12 + int(s[2:])

def get_college_stats(link):
    """Scrape college stats (Totals and Advanced) for a given player."""
    player_url = get_player_url(link)
    if not player_url:
        print('college stats not found')
        return None
    
    age = player_url[1]
    response = requests.get(player_url[0])
    if response.status_code != 200:
        print(response.status_code)
        return None  # Page not found

    player_soup = BeautifulSoup(response.text, 'html5lib')
    if response.text.find('id="div_players_advanced"') != -1:
        print("in raw text", response.text.find('id="players_advanced"'))
    if 'id="players_advanced"' in player_soup.get_text():
        print("in soup")
    #for element in player_soup(text=lambda text: isinstance(text, Comment)):
    #    element.extract()
    # Extract Totals table
    totals_table = player_soup.find('table', attrs={'id':'players_totals'})
    totals_df = pd.read_html(str(totals_table))[0] if totals_table else pd.DataFrame()
    
    # Extract Advanced table
    raw_html = response.text
    start = raw_html.find('id="div_players_advanced"') - 53  # Find the start of the first table
    end = raw_html.find("</table>", start) + 8 # Find the end of the first table
    advanced_soup = 0
    if start != -1 and end != -1:
        table_html = raw_html[start:end]
        print("Extracted table HTML: ", start, end)
        advanced_soup = BeautifulSoup(table_html, "html.parser")
        #print(soup_table.prettify())
    else:
        print("Table not found in raw HTML.", start, end)

    advanced_table = advanced_soup.find('table', attrs={'id':'players_advanced'})
    #print(raw_html[start:start+10000])
    advanced_df = pd.read_html(str(advanced_table))[0] if advanced_table else pd.DataFrame()
    #print(advanced_df)

    if not totals_df.empty and not advanced_df.empty:
        totals_df = totals_df.add_prefix("Totals_")
        advanced_df = advanced_df.add_prefix("Advanced_")
        combined_df = pd.concat([totals_df, advanced_df], axis=1)
    elif not totals_df.empty:
        print('adv empty')
        combined_df = totals_df.add_prefix("Totals_")
    elif not advanced_df.empty:
        combined_df = advanced_df.add_prefix("Advanced_")
    else:
        print('tables empty')
        combined_df = None
    
    height = convert_height(player_soup.find('div', attrs={'id':'info'}).find_all('span')[1].text)
    print(height)
    height1 = [height for i in range(combined_df.shape[0])]
    agel = [age for i in range(combined_df.shape[0])]
    return combined_df.assign(age=agel).assign(height=height1)

def main():
    all_data = []
    for year in range(2010,2021):
        print(f'Scraping {year} Draft: \n')
        draft_url = f"https://www.basketball-reference.com/draft/NBA_{year}.html"
        players = get_drafted_players(draft_url)
        
        for name, college, link  in players:
            print(f"Scraping stats for {name} from {college}...")
            stats_df = get_college_stats(link)
            if stats_df is not None and not stats_df.empty:
                stats_df.insert(0, "Player", name)
                stats_df.insert(1, "College", college)
                all_data.append(stats_df)
            else:
                print('stats empty')
            time.sleep(5)  # To avoid getting blocked
            
    
    final_df = pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()
    final_df.to_csv("nba_draft_college_stats.csv", index=False)
    print("Scraping complete. Data saved to CSV file.")

if __name__ == "__main__":
    main()
