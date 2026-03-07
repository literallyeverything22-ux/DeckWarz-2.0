import json

def merge_final():
    with open("cricsheet_aggregated.json", "r") as f:
        data = json.load(f)
        
    with open("players names.json", "r", encoding="utf-8") as f:
        players_to_find = json.load(f)
        
    with open("t20i_players_stats_merged.json", "r", encoding="utf-8") as f:
        existing_stats = json.load(f)
        
    cricsheet_names = list(data.keys())
    
    # Custom map for known hard ones
    custom_map = {
        "Rohit Sharma": "RG Sharma",
        "Dinesh Karthik": "KD Karthik",
        "Bhuvneshwar Kumar": "B Kumar",
        "Mohit Sharma": "MM Sharma",
        "Karn Sharma": "KV Sharma",
        "Axar Patel": "AR Patel",
        "Khaleel Ahmed": "KK Ahmed",
        "Varun Chakravarthy": "CV Varun",
        "Parthiv Patel": "PA Patel",
        "Rahul Sharma": "R Sharma",
        "Munaf Patel": "MM Patel",
        "Sreesanth": "S Sreesanth",
        "Rishi Dhawan": "R Dhawan",
        "Shardul Thakur": "SN Thakur",
        "Harshal Patel": "HV Patel",
        "Venkatesh Iyer": "VR Iyer",
        "Vinay Kumar": "R Vinay Kumar",
        "Prasidh Krishna": "M Prasidh Krishna",
        "Jitesh Sharma": "JM Sharma",
        "Sai Sudharsan": "B Sai Sudharsan",
        "Tom Kohler-Cadmore": "T Kohler-Cadmore",
        "Shaheen Afridi": "Shaheen Shah Afridi",
        "Rassie van der Dussen": "HE van der Dussen",
        "Malinga Bandara": "CM Bandara",
        "Ajantha Mendis": "BAW Mendis",
        "Kusal Perera": "MDKJ Perera",
        "Kusal Mendis": "BKG Mendis",
        "Wanindu Hasaranga": "PWH de Silva",
        "Kamindu Mendis": "PHKD Mendis",
        "Dilshan Madushanka": "D Madushanka",
        "Binura Fernando": "B Fernando",
        "Dwayne Bravo": "DJ Bravo",
        "Kevon Cooper": "KK Cooper",
        "Mohammad Nabi": "M Nabi",
        "Rahmanullah Gurbaz": "R Gurbaz",
        "Fareed Ahmad": "Fareed Ahmad Malik",
        "Noor Ahmad": "Noor Ahmad Lakanwal",
        "Nijat Masood": "Nijat Masood",
        "Zubaid Akbari": "Z Akbari",
        "Wafadar Momand": "W Momand",
        "Ikram Alikhil": "I Alikhil",
        "Subashis Roy": "Subashis Roy",
        "Sanjamul Islam": "Sunzamul Islam"
    }
    
    # Just to be sure, check if our aliases exist
    for k, v in custom_map.items():
        if v not in data and v != "T Kohler-Cadmore": # Tom Kohler-Cadmore actually hasn't played T20I (played T10/franchise)
            # maybe fix aliases
            if "Hasaranga" in v: # Wanindu is usually 'PWH de Silva'
                pass

    def find_player(full_name, country):
        if full_name in custom_map and custom_map[full_name] in data:
            return custom_map[full_name]
            
        parts = full_name.split()
        if len(parts) >= 2:
            last = parts[-1]
            first_initial = parts[0][0]
            
            matches = []
            for n in cricsheet_names:
                n_parts = n.split()
                if len(n_parts) >= 2 and n_parts[-1] == last:
                    if first_initial in n_parts[0]:
                        matches.append(n)
            
            valid_matches = []
            for m in matches:
                p_data = data[m]
                if p_data.get("country") == country:
                    valid_matches.append(m)
                    
            if len(valid_matches) == 1:
                return valid_matches[0]
                
        return None

    success = 0
    missing = []
    
    for country, players in players_to_find.items():
        existing_names = [p["name"] for p in existing_stats[country]]
        for p in players:
            if p in existing_names:
                continue
                
            match_name = find_player(p, country)
            if not match_name and len(p.split()) > 2:
                parts = p.split()
                match_name = find_player(parts[0] + " " + parts[-1], country)
            
            if match_name:
                p_data = data[match_name]
                bat = p_data["batting"]
                bow = p_data["bowling"]
                
                bat_avg = None
                outs = bat["innings"] - bat["not_outs"]
                if outs > 0:
                    bat_avg = round(bat["runs"] / outs, 2)
                    
                bat_sr = None
                if bat["balls_faced"] > 0:
                    bat_sr = round((bat["runs"] / bat["balls_faced"]) * 100, 2)
                    
                bow_overs = round(bow["balls_bowled"] // 6 + (bow["balls_bowled"] % 6) / 10.0, 1)
                bow_eco = None
                if bow_overs > 0:
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
    print(f"Still missing {len(missing)} players (Likely never played a T20I match).")

if __name__ == "__main__":
    merge_final()
