import json
import math

def format_stats():
    # Load aggregated stats
    with open("cricsheet_aggregated.json", "r") as f:
        data = json.load(f)
        
    # Load player names
    with open("players names.json", "r", encoding="utf-8") as f:
        players_to_find = json.load(f)
        
    # Load existing scraped stats
    try:
        with open("t20i_players_stats.json", "r", encoding="utf-8") as f:
            existing_stats = json.load(f)
    except:
        existing_stats = {c: [] for c in players_to_find}
        
    for c in players_to_find:
        if c not in existing_stats:
            existing_stats[c] = []
            
    # Normalize cricsheet names vs players_names.json
    # cricsheet names are usually 'SL Malinga' or 'MS Dhoni'
    # we need a smart fuzzy match
    
    cricsheet_names = list(data.keys())
    
    def find_player(full_name, country):
        # exact match
        if full_name in data: return full_name
        
        # 'Lasith Malinga' -> 'L Malinga' or 'SL Malinga'
        parts = full_name.split()
        if len(parts) >= 2:
            last = parts[-1]
            first_initial = parts[0][0]
            
            # check matches
            matches = [n for n in cricsheet_names if n.endswith(last) and n.startswith(first_initial)]
            if len(matches) == 1:
                return matches[0]
                
            # If still multiples, find one that played for country
            # This is hard because cricsheet doesn't strictly store country per player easily here, 
            # wait, I did store it in the script!
            for m in matches:
                # wait, I didn't save the country in cricsheet_aggregated.json directly in the output, let me check.
                pass
                
        return None

    success = 0
    missing = []
    
    for country, players in players_to_find.items():
        existing_names = [p["name"] for p in existing_stats[country]]
        for p in players:
            if p in existing_names:
                continue
                
            match_name = find_player(p, country)
            if not match_name:
                # Try dropping middle names
                parts = p.split()
                if len(parts) > 2:
                    match_name = find_player(parts[0] + " " + parts[-1], country)
            
            if match_name:
                p_data = data[match_name]
                bat = p_data["batting"]
                bow = p_data["bowling"]
                
                # Format exactly as stats template
                bat_avg = None
                outs = bat["innings"] - bat["not_outs"]
                if outs > 0:
                    bat_avg = round(bat["runs"] / outs, 2)
                    
                bat_sr = None
                if bat["balls_faced"] > 0:
                    bat_sr = round((bat["runs"] / bat["balls_faced"]) * 100, 2)
                    
                bow_overs = bow["balls_bowled"] // 6 + (bow["balls_bowled"] % 6) / 10.0
                bow_eco = None
                if bow_overs > 0:
                    # actually eco is runs / (balls/6)
                    bow_eco = round(bow["runs_conceded"] / (bow["balls_bowled"] / 6.0), 2)
                    
                bow_avg = None
                if bow["wickets"] > 0:
                    bow_avg = round(bow["runs_conceded"] / bow["wickets"], 2)
                    
                bow_sr = None
                if bow["wickets"] > 0:
                    bow_sr = round(bow["balls_bowled"] / bow["wickets"], 1)
                
                best_bowl = None
                if bow["best"][0] > 0:
                    best_bowl = f"{bow['best'][0]}/{bow['best'][1]}"
                
                formatted = {
                    "name": p,
                    "profile_url": "offline_cricsheet",
                    "stats": {
                        "Personal Information": {
                            "Date of Birth": None
                        },
                        "Batting Statistics": {
                            "Matches Played": p_data["matches_played"],
                            "Innings Played": bat["innings"],
                            "Not Outs": bat["not_outs"],
                            "Runs / Total Runs": bat["runs"],
                            "Highest Score": bat["highest"],
                            "Average / Batting Average": bat_avg,
                            "Balls Faced": bat["balls_faced"],
                            "Bating Strike Rate": bat_sr,
                            "4s": bat["4s"],
                            "6s": bat["6s"],
                            "50s": bat["50s"],
                            "100s": bat["100s"]
                        },
                        "Bowling Statistics": {
                            "Innings Pl.": bow["innings"],
                            "Overs": bow_overs if bow_overs > 0 else None,
                            "Runs conceded": bow["runs_conceded"] if bow["innings"] > 0 else None,
                            "Wickets": bow["wickets"] if bow["innings"] > 0 else None,
                            "Best Bowling": best_bowl,
                            "Avg. Ball": bow_avg,
                            "Economy / Eco. Rate": bow_eco,
                            "Bowling Strike Rate": bow_sr
                        }
                    }
                }
                
                existing_stats[country].append(formatted)
                success += 1
            else:
                missing.append(p)
                
    with open("t20i_players_stats_merged.json", "w", encoding="utf-8") as f:
        json.dump(existing_stats, f, indent=4)
        
    print(f"Successfully added {success} players.")
    print(f"Still missing {len(missing)} players.")

if __name__ == "__main__":
    format_stats()
