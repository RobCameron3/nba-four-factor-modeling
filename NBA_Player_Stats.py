import requests
import pandas as pd
from bs4 import BeautifulSoup
from openpyxl import load_workbook
import os
import time
import random

# 🏠 New Folder Path & Excel File Name (Updated for OneDrive)
folder_path = "/Users/johnrcameron/Library/CloudStorage/OneDrive-Personal/NBA_STATS_FOLDER"
file_path = os.path.join(folder_path, "NBA_Player_Stats_2024_2025_Season.xlsx")

# 🏀 Player Stats URLs
player_urls = {
    "Player_Totals": "https://www.basketball-reference.com/leagues/NBA_2025_totals.html",
    "Player_Per_Game_Stats": "https://www.basketball-reference.com/leagues/NBA_2025_per_game.html",
    "Players_Per_36_Min": "https://www.basketball-reference.com/leagues/NBA_2025_per_minute.html",
    "Player_Stats_Per_100_Possesions": "https://www.basketball-reference.com/leagues/NBA_2025_per_poss.html",
    "Players_Advanced_Stats": "https://www.basketball-reference.com/leagues/NBA_2025_advanced.html",
    "Players_Play_By_Play_Stats": "https://www.basketball-reference.com/leagues/NBA_2025_play-by-play.html",
    "Player_Shooting": "https://www.basketball-reference.com/leagues/NBA_2025_shooting.html",
    "Player_Adjusted_Shooting": "https://www.basketball-reference.com/leagues/NBA_2025_adj_shooting.html",
}

# 🏀 NBA Team Abbreviations for Basic Game Logs
team_abbreviations = [
    "ATL", "BOS", "BRK", "CHO", "CHI", "CLE", "DAL", "DEN", "DET", "GSW",
    "HOU", "IND", "LAC", "LAL", "MEM", "MIA", "MIL", "MIN", "NOP", "NYK",
    "OKC", "ORL", "PHI", "PHO", "POR", "SAC", "SAS", "TOR", "UTA", "WAS"
]

# 📅 Function to Scrape & Clean Tables (Handles Rate Limits & Removes Extra Rows)
def scrape_table(url):
    time.sleep(random.uniform(10, 15))  # Wait 10-15 seconds to avoid being blocked
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 429:  # Rate limit hit
        print("🚨 Rate limited! Pausing for 2 minutes before retrying...")
        time.sleep(120)  # Wait 2 minutes before retrying
        response = requests.get(url, headers=headers)  # Retry request

    if response.status_code != 200:
        print(f"❌ Failed to fetch {url}. Status Code: {response.status_code}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find("table")

    if table:
        df = pd.read_html(str(table))[0]
        df = df.droplevel(0, axis=1) if isinstance(df.columns, pd.MultiIndex) else df

        # 🏀 Remove Duplicate Header Rows Inside Data
        if 'Rk' in df.columns:
            df = df[df['Rk'].astype(str) != 'Rk'].reset_index(drop=True)
        
        # 🔄 Remove the Last Row (Usually Summary Row)
        df = df.iloc[:-1] if len(df) > 1 else df
        
        return df
    else:
        print(f"⚠️ Warning: No table found for {url}")
        return None

# 📂 Ensure the folder exists
if not os.path.exists(folder_path):
    os.makedirs(folder_path)

# 🔄 Load existing Excel file (if it exists)
try:
    book = load_workbook(file_path)
except FileNotFoundError:
    book = None

# 🌟 Scrape Player Stats
print("\n🌟 Scraping Player Stats...")
with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    for sheet_name, url in player_urls.items():
        print(f"🔍 Scraping: {sheet_name} ({url})")
        df = scrape_table(url)

        if df is not None:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            print(f"✅ Successfully added: {sheet_name}")
        else:
            print(f"❌ Failed to retrieve {sheet_name}")

# 🏀 Scrape Basic Team Game Logs (without duplicate headers & last row removed)
print("\n🏀 Scraping Basic Team Game Logs...")
with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    for team in team_abbreviations:
        url = f"https://www.basketball-reference.com/teams/{team}/2025/gamelog/"
        print(f"📊 Scraping: {url}")

        df = scrape_table(url)

        if df is not None:
            sheet_name = f"{team}_Team_Game_Log"
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            print(f"✅ Successfully added: {sheet_name}")
        else:
            print(f"❌ Failed to retrieve data for {team}")

print(f"\n🏆 **All player stats and basic team game logs updated in {file_path}!**")