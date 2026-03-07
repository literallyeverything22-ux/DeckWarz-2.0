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

def verify_squads():
    with open("t20i_players_stats.json", "r", encoding="utf-8") as f:
        dataset = json.load(f)
        
    all_dataset_names = set()
    for country, players in dataset.items():
        for p in players:
            all_dataset_names.add(p["name"].lower().strip())
            
    # Also create a reverse map to do fuzzy checking
    all_tokens = {name: set(name.split()) for name in all_dataset_names}
    
    missing_players = {}
    
    for country, squad in squads.items():
        missing_players[country] = []
        for player in squad:
            p_lower = player.lower().strip()
            
            # 1. Exact match
            if p_lower in all_dataset_names:
                continue
                
            # 2. Check if a very close alias exists (e.g., Kusal Janith Perera -> Kusal Perera)
            p_parts = set(p_lower.split())
            found = False
            for db_name, db_parts in all_tokens.items():
                # If they share at least 2 common meaningful words (e.g. first + last name)
                # or if one is exactly contained within the other
                if p_lower in db_name or db_name in p_lower:
                    found = True
                    break
                
                # Check intersection of parts, ignoring common words like 'md', 'mohammad', 'ali'
                intersection = p_parts.intersection(db_parts)
                if len(intersection) >= 2:
                    found = True
                    break
                    
                # E.g. "Varun Chakaravarthy" vs "Varun Chakravarthy"
                if len(p_parts) >= 2 and len(db_parts) >= 2:
                    db_first, db_last = list(db_parts)[0], list(db_parts)[-1]
                    p_first, p_last = list(p_parts)[0], list(p_parts)[-1]
                    if p_first == db_first and (p_last in db_last or db_last in p_last):
                        found = True
                        break
            
            if not found:
                missing_players[country].append(player)
                
    total_missing = sum(len(m) for m in missing_players.values())
    
    if total_missing == 0:
        print("Success! All selected 15-player squad members are present in the dataset.")
    else:
        print(f"Warning: {total_missing} players from the current World Cup squads were not found:")
        for country, m in missing_players.items():
            if m:
                print(f"- {country}: {', '.join(m)}")

if __name__ == "__main__":
    verify_squads()
