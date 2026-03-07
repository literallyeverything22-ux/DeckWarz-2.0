import json
import glob
import os

def get_stat(d, *keys):
    if not d: return None
    for k in keys:
        if k in d: return d[k]
    return None

def clean_num(val):
    if val is None or val == "-": return None
    try:
        if "." in str(val): return float(val)
        return int(val)
    except:
        return val

def main():
    with open("players names.json", "r", encoding="utf-8") as f:
        players_names = json.load(f)
        
    final_output = {}
    success_count = 0
    skipped_count = 0
    error_count = 0
    
    # Load all the individual country stats files we previously generated
    # e.g. stats_India.json, stats_Australia.json
    all_local_profiles = []
    for filepath in glob.glob("stats_*.json"):
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Depending on how the individual stats files are structured,
            # they could be a list of player dicts, or a dict by country.
            print(f"Reading {filepath}...")
            if isinstance(data, list):
                all_local_profiles.extend(data)
            elif isinstance(data, dict):
                for k, v in data.items():
                    if isinstance(v, list):
                        all_local_profiles.extend(v)
                        
    print(f"Loaded {len(all_local_profiles)} total profiles from local country files.")
    
    for country, players in players_names.items():
        final_output[country] = []
        unique_players = list(dict.fromkeys(players))
        
        for player in unique_players:
            slug_guess = player.replace(' ', '-').lower()
            name_guess = player.lower()
            
            matched_data = None
            for p in all_local_profiles:
                p_name = p.get("name", "").lower()
                p_url = p.get("profile_url", "").lower()
                
                # Check direct match
                if name_guess == p_name or slug_guess in p_url:
                    matched_data = p
                    break
                    
            if not matched_data:
                # Fuzzy match URL
                for p in all_local_profiles:
                    p_url = p.get("profile_url", "").lower()
                    if any(part in p_url for part in slug_guess.split('-') if len(part) > 3):
                        matched_data = p
                        break
                        
            if not matched_data or "error" in matched_data:
                error_count += 1
                continue
                
            # Extract T20 stats
            batting_all = matched_data.get("batting_stats", {})
            bowling_all = matched_data.get("bowling_stats", {})
            
            batting_t20 = batting_all.get("t20i", batting_all.get("t20", {}))
            bowling_t20 = bowling_all.get("t20i", bowling_all.get("t20", {}))
            
            b_matches = get_stat(batting_t20, "matches")
            bo_matches = get_stat(bowling_t20, "matches")
            
            if (not b_matches or b_matches == "0") and (not bo_matches or bo_matches == "0"):
                skipped_count += 1
                continue

            balls_bowled = clean_num(get_stat(bowling_t20, "balls"))
            overs_bowled = None
            if isinstance(balls_bowled, (int, float)):
                overs_bowled = round(balls_bowled / 6.0, 1)

            formatted_stats = {
                "Personal Information": {
                    "Date of Birth": None
                },
                "Batting Statistics": {
                    "Matches Played": clean_num(get_stat(batting_t20, "matches")),
                    "Innings Played": clean_num(get_stat(batting_t20, "innings")),
                    "Not Outs": clean_num(get_stat(batting_t20, "not out")),
                    "Runs / Total Runs": clean_num(get_stat(batting_t20, "runs")),
                    "Highest Score": get_stat(batting_t20, "highest"),
                    "Average / Batting Average": clean_num(get_stat(batting_t20, "average")),
                    "Balls Faced": clean_num(get_stat(batting_t20, "balls")),
                    "Bating Strike Rate": clean_num(get_stat(batting_t20, "sr")),
                    "4s": clean_num(get_stat(batting_t20, "fours")),
                    "6s": clean_num(get_stat(batting_t20, "sixes")),
                    "50s": clean_num(get_stat(batting_t20, "50s")),
                    "100s": clean_num(get_stat(batting_t20, "100s"))
                },
                "Bowling Statistics": {
                    "Innings Pl.": clean_num(get_stat(bowling_t20, "innings")),
                    "Overs": overs_bowled,
                    "Runs conceded": clean_num(get_stat(bowling_t20, "runs")),
                    "Wickets": clean_num(get_stat(bowling_t20, "wickets")),
                    "Best Bowling": get_stat(bowling_t20, "bbi"),
                    "Avg. Ball": clean_num(get_stat(bowling_t20, "avg")),
                    "Economy / Eco. Rate": clean_num(get_stat(bowling_t20, "eco")),
                    "Bowling Strike Rate": clean_num(get_stat(bowling_t20, "sr"))
                }
            }
            
            final_output[country].append({
                "name": player,
                "stats": formatted_stats
            })
            success_count += 1
            
    with open("t20i_players_stats.json", "w", encoding="utf-8") as f:
        json.dump(final_output, f, indent=4)
        
    print("\n--- Processing Complete ---")
    print(f"Successfully processed: {success_count}")
    print(f"Skipped (No T20I stats): {skipped_count}")
    print(f"Errors (Profile not in downloaded dataset): {error_count}")

if __name__ == "__main__":
    main()
