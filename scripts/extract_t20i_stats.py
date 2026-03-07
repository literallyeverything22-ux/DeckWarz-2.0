import json
import os
import requests
from bs4 import BeautifulSoup
import time
import concurrent.futures

# Using Cricbuzz's native internal search API/HTML
def get_cricbuzz_profile_native(player_name):
    # Cricbuzz search page
    search_url = f"https://www.cricbuzz.com/search?q={player_name.replace(' ', '%20')}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    }
    
    try:
        resp = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # In cricbuzz search results, profiles look like /profiles/1413/virat-kohli
        for a in soup.find_all('a', href=True):
            href = a['href']
            if '/profiles/' in href:
                if not href.startswith('http'):
                    href = 'https://www.cricbuzz.com' + href
                return href
                
    except Exception as e:
        pass
    return None

def fetch_t20i_stats(profile_link):
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
            
        dob = None
        personal_info_divs = cric.find_all("div", class_="text-sm text-cb-900")
        for i, div in enumerate(personal_info_divs):
            if div.text.strip() == "Born":
                next_div = div.find_next_sibling("div")
                if next_div:
                    dob = next_div.text.strip()
                else:
                    parent = div.parent
                    if parent:
                        val_div = parent.find_all("div")
                        if len(val_div) > 1:
                            dob = val_div[1].text.strip()
                break
                
        if not dob:
            for div in cric.find_all("div", class_="cb-col cb-col-40 text-bold"):
                if "Born" in div.text:
                    sibling = div.find_next_sibling("div", class_="cb-col cb-col-60")
                    if sibling:
                        dob = sibling.text.strip()
                        break

        batting_t20i = {}
        bowling_t20i = {}

        tables = cric.find_all("table")
        for table in tables:
            parent_text = table.parent.parent.text if table.parent and table.parent.parent else ""
            is_batting = "Batting Career Summary" in parent_text or "Batting" in parent_text
            is_bowling = "Bowling Career Summary" in parent_text or "Bowling" in parent_text
            
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
            
            t20i_idx = -1
            for i, h in enumerate(headers):
                if h == "t20i" or h == "t20":
                    t20i_idx = i
                    break
                    
            if t20i_idx == -1:
                continue
            
            tbody = table.find("tbody")
            if not tbody: continue
            
            for row in tbody.find_all("tr"):
                cols = row.find_all("td")
                if len(cols) >= t20i_idx + 1:
                    stat_name = cols[0].text.strip().lower()
                    val = cols[t20i_idx + 1].text.strip()
                    
                    if val == "-":
                        val = None
                    elif val is not None:
                        try:
                            if "." in val:
                                val = float(val)
                            else:
                                val = int(val)
                        except ValueError:
                            pass
                            
                    if is_batting:
                        batting_t20i[stat_name] = val
                    elif is_bowling:
                        bowling_t20i[stat_name] = val

        if not batting_t20i and not bowling_t20i:
            return None

        def get_stat(d, *keys):
            for k in keys:
                if k in d: return d[k]
            return None
            
        balls_bowled = get_stat(bowling_t20i, "balls")
        overs_bowled = None
        if isinstance(balls_bowled, int):
            overs_bowled = round(balls_bowled / 6.0, 1)
        elif isinstance(balls_bowled, float):
            overs_bowled = round(balls_bowled / 6.0, 1)

        formatted_stats = {
            "Personal Information": {
                "Date of Birth": dob
            },
            "Batting Statistics": {
                "Matches Played": get_stat(batting_t20i, "matches"),
                "Innings Played": get_stat(batting_t20i, "innings"),
                "Not Outs": get_stat(batting_t20i, "not out", "no"),
                "Runs / Total Runs": get_stat(batting_t20i, "runs"),
                "Highest Score": get_stat(batting_t20i, "highest", "hs"),
                "Average / Batting Average": get_stat(batting_t20i, "average", "avg"),
                "Balls Faced": get_stat(batting_t20i, "balls", "bf"),
                "Bating Strike Rate": get_stat(batting_t20i, "sr", "strike rate"),
                "4s": get_stat(batting_t20i, "fours", "4s"),
                "6s": get_stat(batting_t20i, "sixes", "6s"),
                "50s": get_stat(batting_t20i, "50s"),
                "100s": get_stat(batting_t20i, "100s")
            },
            "Bowling Statistics": {
                "Innings Pl.": get_stat(bowling_t20i, "innings"),
                "Overs": overs_bowled,
                "Runs conceded": get_stat(bowling_t20i, "runs"),
                "Wickets": get_stat(bowling_t20i, "wickets"),
                "Best Bowling": get_stat(bowling_t20i, "bbi", "best"),
                "Avg. Ball": get_stat(bowling_t20i, "avg", "average"),
                "Economy / Eco. Rate": get_stat(bowling_t20i, "eco", "economy"),
                "Bowling Strike Rate": get_stat(bowling_t20i, "sr", "strike rate")
            }
        }
        
        return {
            "profile_url": profile_link,
            "stats": formatted_stats
        }
    except Exception as e:
        return None

def process_player(args):
    player, country = args
    print(f"[{country}] Fetching {player}...")
    
    link = get_cricbuzz_profile_native(player) # use native search
    
    if link:
        result = fetch_t20i_stats(link)
        if result:
            result["name"] = player
            return {"status": "success", "data": result}
        else:
            return {"status": "skipped", "reason": "No T20I stats found", "player": player, "country": country}
    return {"status": "error", "reason": "Profile not found via Cricbuzz native search", "player": player, "country": country}

if __name__ == '__main__':
    with open("players names.json", "r", encoding="utf-8") as f:
        players_data = json.load(f)
        
    all_t20i_stats = {}
    success_count = 0
    skipped_count = 0
    error_count = 0
    
    # Load previously accumulated stats to avoid re-fetching the 100+ we already got perfectly
    if os.path.exists("t20i_players_stats.json"):
        try:
            with open("t20i_players_stats.json", "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    saved = json.loads(content)
                    if isinstance(saved, dict):
                        all_t20i_stats = saved
        except Exception:
            pass
            
    print("Starting extraction using native Cricbuzz HTML search...")
    
    for country, players in players_data.items():
        if country not in all_t20i_stats:
            all_t20i_stats[country] = []
            
        existing_names = [p["name"] for p in all_t20i_stats.get(country, [])]
        unique_players = list(dict.fromkeys(players))
        
        args = []
        for p in unique_players:
            if p not in existing_names:
                args.append((p, country))
            else:
                success_count += 1
                
        # Small concurrency
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            for r in executor.map(process_player, args):
                if r["status"] == "success":
                    all_t20i_stats[country].append(r["data"])
                    success_count += 1
                elif r["status"] == "skipped":
                    print(f"  -> Skipped {r['player']}: {r['reason']}")
                    skipped_count += 1
                else:
                    print(f"  -> Failed {r['player']}: {r['reason']}")
                    error_count += 1
                    
        with open("t20i_players_stats.json", "w", encoding="utf-8") as f:
            json.dump(all_t20i_stats, f, indent=4)
            
    print("\n--- Extraction Complete ---")
    print(f"Successfully processed (with T20I data): {success_count}")
    print(f"Skipped (No T20I stats): {skipped_count}")
    print(f"Errors (Profile not found): {error_count}")
