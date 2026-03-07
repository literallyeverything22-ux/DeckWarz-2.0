import json

squads = {
    "India": ["Suryakumar Yadav", "Abhishek Sharma", "Tilak Varma", "Sanju Samson", "Shivam Dube", "Ishan Kishan", "Hardik Pandya", "Arshdeep Singh", "Jasprit Bumrah", "Harshit Rana", "Varun Chakaravarthy", "Kuldeep Yadav", "Axar Patel", "Washington Sundar", "Rinku Singh"],
    "Australia": ["Mitchell Marsh", "Xavier Bartlett", "Cooper Connolly", "Tim David", "Ben Dwarshuis", "Cameron Green", "Nathan Ellis", "Travis Head", "Josh Inglis", "Matthew Kuhnemann", "Glenn Maxwell", "Matthew Renshaw", "Marcus Stoinis", "Adam Zampa", "Steve Smith"],
    "England": ["Harry Brook", "Rehan Ahmed", "Jofra Archer", "Tom Banton", "Jacob Bethell", "Jos Buttler", "Sam Curran", "Liam Dawson", "Ben Duckett", "Will Jacks", "Jamie Overton", "Adil Rashid", "Phil Salt", "Josh Tongue", "Luke Wood"],
    "Pakistan": ["Salman Ali Agha", "Abrar Ahmed", "Babar Azam", "Faheem Ashraf", "Fakhar Zaman", "Khawaja Mohammad Nafay", "Mohammad Nawaz", "Mohammad Salman Mirza", "Naseem Shah", "Sahibzada Farhan", "Saim Ayub", "Shaheen Shah Afridi", "Shadab Khan", "Usman Khan", "Usman Tariq"],
    "South Africa": ["Aiden Markram", "Corbin Bosch", "Dewald Brevis", "Quinton de Kock", "Marco Jansen", "George Linde", "Keshav Maharaj", "Kwena Maphaka", "David Miller", "Lungi Ngidi", "Anrich Nortje", "Kagiso Rabada", "Ryan Rickelton", "Jason Smith", "Tristan Stubbs"],
    "New Zealand": ["Mitchell Santner", "Finn Allen", "Mark Chapman", "Devon Conway", "Jacob Duffy", "Lockie Ferguson", "Matt Henry", "Kyle Jamieson", "Daryl Mitchell", "James Neesham", "Glenn Phillips", "Rachin Ravindra", "Tim Seifert", "Ish Sodhi", "Cole McConchie"],
    "Sri Lanka": ["Dasun Shanaka", "Pathum Nissanka", "Kamil Mishara", "Kusal Mendis", "Kamindu Mendis", "Kusal Janith Perera", "Charith Asalanka", "Janith Liyanage", "Pavan Rathnayake", "Dushan Hemantha", "Dunith Wellalage", "Maheesh Theekshana", "Dushmantha Chameera", "Matheesha Pathirana", "Eshan Malinga"],
    "West Indies": ["Shai Hope", "Shimron Hetmyer", "Johnson Charles", "Roston Chase", "Matthew Forde", "Jason Holder", "Akeal Hosein", "Shamar Joseph", "Brandon King", "Gudakesh Motie", "Rovman Powell", "Sherfane Rutherford", "Quentin Sampson", "Jayden Seales", "Romario Shepherd"],
    "Bangladesh": ["Litton Das", "Tanzid Hasan", "Parvez Hossain Emon", "Saif Hassan", "Tawhid Hridoy", "Shamim Hossain", "Quazi Nurul Hasan Sohan", "Shak Mahedi Hasan", "Rishad Hossain", "Nasum Ahmed", "Mustafizur Rahman", "Tanzim Hasan Sakib", "Taskin Ahmed", "Shaif Uddin", "Shoriful Islam"],
    "Afghanistan": ["Rashid Khan", "Noor Ahmad", "Abdullah Ahmadzai", "Sediqullah Atal", "Fazalhaq Farooqi", "Rahmanullah Gurbaz", "Naveen Ul Haq", "Mohammad Ishaq", "Shahidullah Kamal", "Mohammad Nabi", "Gulbadin Naib", "Azmatullah Omarzai", "Mujeeb Ur Rahman", "Darwish Rasooli", "Ibrahim Zadran"],
    "Ireland": ["Paul Stirling", "Lorcan Tucker", "Mark Adair", "Ross Adair", "Ben Calitz", "Curtis Campher", "Gareth Delany", "George Dockrell", "Matthew Humphreys", "Josh Little", "Barry McCarthy", "Harry Tector", "Tim Tector", "Ben White", "Craig Young"],
    "Zimbabwe": ["Sikandar Raza", "Brian Bennett", "Ryan Burl", "Graeme Cremer", "Bradley Evans", "Clive Madande", "Tinotenda Maposa", "Tadiwanashe Marumani", "Wellington Masakadza", "Tony Munyonga", "Tashinga Musekiwa", "Blessing Muzarabani", "Dion Myers", "Richard Ngarava", "Brendan Taylor"]
}

def add_missing_squads():
    with open("cricsheet_aggregated.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    with open("t20i_players_stats.json", "r", encoding="utf-8") as f:
        existing_stats = json.load(f)
        
    with open("players names.json", "r", encoding="utf-8") as f:
        players_names = json.load(f)
        
    cricsheet_names = list(data.keys())
    
    all_dataset_names = set()
    for country, players in existing_stats.items():
        for p in players:
            all_dataset_names.add(p["name"].lower().strip())
            
    all_tokens = {name: set(name.split()) for name in all_dataset_names}
    
    missing_players = {}
    
    for country, squad in squads.items():
        missing_players[country] = []
        for player in squad:
            p_lower = player.lower().strip()
            
            if p_lower in all_dataset_names:
                continue
                
            p_parts = set(p_lower.split())
            found = False
            for db_name, db_parts in all_tokens.items():
                if p_lower in db_name or db_name in p_lower:
                    found = True
                    break
                intersection = p_parts.intersection(db_parts)
                if len(intersection) >= 2:
                    found = True
                    break
                if len(p_parts) >= 2 and len(db_parts) >= 2:
                    db_first, db_last = list(db_parts)[0], list(db_parts)[-1]
                    p_first, p_last = list(p_parts)[0], list(p_parts)[-1]
                    if p_first == db_first and (p_last in db_last or db_last in p_last):
                        found = True
                        break
            
            if not found:
                missing_players[country].append(player)
    
    def find_player(full_name, country):
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
                valid_matches.append(m)
                    
            if len(valid_matches) == 1:
                return valid_matches[0]
            elif len(valid_matches) > 1:
                for v in valid_matches:
                    if parts[0] in v:
                        return v
                return valid_matches[0]
        return None

    success = 0
    not_found_in_db = []
    
    for country, missing in missing_players.items():
        if country not in existing_stats:
            existing_stats[country] = []
        if country not in players_names:
            players_names[country] = []
            
        for p in missing:
            if p not in players_names[country]:
                players_names[country].append(p)
                
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
                formatted = {
                    "name": p,
                    "profile_url": "debutant_or_not_found",
                    "stats": {
                        "Personal Information": { "Date of Birth": None },
                        "Batting Statistics": { "Matches Played": 0, "Innings Played": 0, "Not Outs": 0, "Runs / Total Runs": 0, "Highest Score": 0, "Average / Batting Average": None, "Balls Faced": 0, "Bating Strike Rate": None, "4s": 0, "6s": 0, "50s": 0, "100s": 0 },
                        "Bowling Statistics": { "Innings Pl.": 0, "Overs": None, "Runs conceded": None, "Wickets": None, "Best Bowling": None, "Avg. Ball": None, "Economy / Eco. Rate": None, "Bowling Strike Rate": None }
                    }
                }
                existing_stats[country].append(formatted)
                not_found_in_db.append(p)

    with open("t20i_players_stats.json", "w", encoding="utf-8") as f:
        json.dump(existing_stats, f, indent=4)
        
    with open("players names.json", "w", encoding="utf-8") as f:
        json.dump(players_names, f, indent=4)
        
    print(f"Added {success} players with full stats from offline DB.")
    print(f"Added {len(not_found_in_db)} players as blank debutants: {not_found_in_db}")

if __name__ == "__main__":
    add_missing_squads()
