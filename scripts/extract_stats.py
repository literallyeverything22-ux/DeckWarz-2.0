import json
import os
import requests
from bs4 import BeautifulSoup
from ddgs import DDGS
import time
import random
import concurrent.futures
import re

ddgs = DDGS(timeout=10)

def get_wiki_players(country):
    url = f"https://en.wikipedia.org/wiki/List_of_{country}_ODI_cricketers"
    if country == "West_Indies":
        url = "https://en.wikipedia.org/wiki/List_of_West_Indies_ODI_cricketers"
    elif country == "South_Africa":
        url = "https://en.wikipedia.org/wiki/List_of_South_Africa_ODI_cricketers"
    elif country == "New_Zealand":
        url = "https://en.wikipedia.org/wiki/List_of_New_Zealand_ODI_cricketers"
    elif country == "Sri_Lanka":
        url = "https://en.wikipedia.org/wiki/List_of_Sri_Lanka_ODI_cricketers"

    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        url = f"https://en.wikipedia.org/wiki/List_of_{country}_Test_cricketers"
        resp = requests.get(url, headers=headers)
        if resp.status_code != 200:
            print(f"Failed to fetch {country}")
            return []
            
    soup = BeautifulSoup(resp.text, 'html.parser')
    players = []
    
    tables = soup.find_all("table", class_="wikitable")
    if not tables:
        return []
        
    for row in tables[0].find_all("tr")[1:]: 
        cols = row.find_all(["th", "td"])
        if len(cols) >= 2:
            if len(cols) > 2 and 'Name' in cols[1].text: 
                continue
                
            name_tag = cols[1].find("a")
            if name_tag:
                name = name_tag.text.strip()
            else:
                name = cols[1].text.strip()
                
            for char in ['*', '†', '‡', '\u2021', '\u2020']:
                name = name.replace(char, '')
            name = re.sub(r'\[.*?\]', '', name).strip()
            name = name.strip()
            if name and name.lower() != 'name' and not name.isdigit():
                players.append(name)
            
            if len(players) >= 100:
                break
    return players

def get_cricbuzz_profile(player_name, country):
    query = f"{player_name} {country} cricket cricbuzz profile"
    try:
        results = ddgs.text(query, max_results=3)
        for r in results:
            link = r.get('href', '')
            if "cricbuzz.com/profiles/" in link:
                parts = link.split('/')
                if len(parts) >= 6:
                    return f"https://www.cricbuzz.com/profiles/{parts[4]}/{parts[5]}"
                return link
    except Exception as e:
        print(f"[{player_name}] DDGS error: {e}")
    return None

def fetch_player_stats(profile_link):
    try:
        c = requests.get(profile_link, headers={"User-Agent": "Mozilla/5.0"}, timeout=10).text
        cric = BeautifulSoup(c, "html.parser")
        
        name = "Unknown"
        for span in cric.find_all(["span", "h1", "div"]):
            if span.get("class") and "text-xl" in span.get("class") and "font-bold" in span.get("class"):
                name = span.text.strip()
                break
                
        if name == "Unknown":
            name_elem = cric.find("h1", class_="cb-font-40")
            if name_elem: name = name_elem.text.strip()

        batting_stats = {}
        bowling_stats = {}

        tables = cric.find_all("table")
        for table in tables:
            parent_text = table.parent.parent.text if table.parent and table.parent.parent else ""
            is_batting = "Batting Career Summary" in parent_text
            is_bowling = "Bowling Career Summary" in parent_text
            
            prev = table.find_previous("div", class_="text-sm font-semibold")
            if prev:
                if "Batting Career Summary" in prev.text:
                    is_batting, is_bowling = True, False
                elif "Bowling Career Summary" in prev.text:
                    is_batting, is_bowling = False, True

            if not is_batting and not is_bowling:
                continue
                
            thead = table.find("thead")
            if not thead: continue
            headers = [th.text.strip().lower() for th in thead.find_all("th") if th.text.strip()]
            
            tbody = table.find("tbody")
            if not tbody: continue
            for row in tbody.find_all("tr"):
                cols = row.find_all("td")
                if len(cols) >= len(headers) + 1:
                    stat_name = cols[0].text.strip().lower()
                    for i, h in enumerate(headers):
                        val = cols[i+1].text.strip()
                        if is_batting:
                            if h not in batting_stats: batting_stats[h] = {}
                            batting_stats[h][stat_name] = val
                        elif is_bowling:
                            if h not in bowling_stats: bowling_stats[h] = {}
                            bowling_stats[h][stat_name] = val

        return {
            "name": name,
            "profile_url": profile_link,
            "batting_stats": batting_stats,
            "bowling_stats": bowling_stats
        }
    except Exception as e:
        print(f"Scraper error: {e}")
        return None

def process_player(args):
    player, country = args
    time.sleep(1) # Wait between requests
    print(f"[{country}] Fetching {player}...")
    link = get_cricbuzz_profile(player, country.replace('_', ' '))
    if link:
        stats = fetch_player_stats(link)
        if stats:
            stats["country"] = country.replace('_', ' ')
            return stats
    return {"name": player, "country": country.replace('_', ' '), "error": "No stats found"}

if __name__ == '__main__':
    countries = [
        "India", "Australia", "England", "South_Africa", 
        "New_Zealand", "Pakistan", "Sri_Lanka", "West_Indies", 
        "Bangladesh", "Afghanistan"
    ]
    
    all_data = {}
    
    for country in countries:
        print(f"--- Fetching players for {country} ---")
        players = get_wiki_players(country)
        print(f"Found {len(players)} players for {country}")
        
        country_data = []
        args = [(p, country) for p in players]
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            for r in executor.map(process_player, args):
                 if r: 
                     country_data.append(r)
                     # Save incrementally so results appear immediately
                     with open(f"stats_{country}.json", "w", encoding="utf-8") as f:
                         json.dump(country_data, f, indent=4)
                
        all_data[country] = country_data
            
    with open("all_players_stats.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=4)
    print("Finished extraction.")
