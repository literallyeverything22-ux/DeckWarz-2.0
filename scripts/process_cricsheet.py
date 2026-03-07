import os
import json
from collections import defaultdict

def calculate_stats():
    # We want to match existing JSON structure
    # {
    #   "Batting Statistics": { "Matches Played", "Innings Played", "Not Outs", "Runs / Total Runs", "Highest Score", "Average / Batting Average", "Balls Faced", "Bating Strike Rate", "4s", "6s", "50s", "100s" },
    #   "Bowling Statistics": { "Innings Pl.", "Overs", "Runs conceded", "Wickets", "Best Bowling", "Avg. Ball", "Economy / Eco. Rate", "Bowling Strike Rate" }
    # }
    
    players_data = defaultdict(lambda: {
        "matches_played": set(),
        "batting": {"innings": 0, "not_outs": 0, "runs": 0, "highest": 0, "balls_faced": 0, "4s": 0, "6s": 0, "50s": 0, "100s": 0, "scores": []},
        "bowling": {"innings": 0, "balls_bowled": 0, "runs_conceded": 0, "wickets": 0, "best": [0,0], "match_wickets": defaultdict(int), "match_runs": defaultdict(int)}
    })

    files = [f for f in os.listdir("t20s_data") if f.endswith(".json")]
    
    for count, f in enumerate(files):
        if count % 1000 == 0:
            print(f"Processed {count}/{len(files)} matches")
            
        with open(os.path.join("t20s_data", f), encoding="utf-8") as file:
            try:
                data = json.load(file)
            except:
                continue
                
        # Only process T20Is
        info = data.get("info", {})
        if info.get("match_type") != "T20" and info.get("match_type") != "IT20":
            # wait, cricsheet T20Is are called "IT20" or "T20I"?
            pass
        
        # actually, any International T20 in this zip should be T20I. We can rely on gender="male" and teams are international
        if info.get("gender") != "male":
            continue
            
        match_id = f.replace(".json", "")
        
        # Register matches for players in the squads/playing XI
        roster = info.get("players", {}) # {'Australia': ['DA Warner', ...]}
        for team, squad in roster.items():
            for p in squad:
                players_data[p]["matches_played"].add(match_id)
                players_data[p]["country"] = team

        innings = data.get("innings", [])
        for inn in innings:
            team = inn.get("team")
            overs = inn.get("overs", [])
            
            # keep track of dismissal status in this match to calculate not outs
            out_players = set()
            batting_match_runs = defaultdict(int)
            batting_match_balls = defaultdict(int)
            batting_match_4s = defaultdict(int)
            batting_match_6s = defaultdict(int)
            
            bowling_match_balls = defaultdict(int)
            bowling_match_runs = defaultdict(int)
            bowling_match_wickets = defaultdict(int)
            
            for over in overs:
                for delivery in over.get("deliveries", []):
                    batter = delivery.get("batter")
                    bowler = delivery.get("bowler")
                    runs = delivery.get("runs", {})
                    
                    bat_runs = runs.get("batter", 0)
                    total_runs = runs.get("total", 0)
                    extras = delivery.get("extras", {})
                    
                    # Batting
                    batting_match_runs[batter] += bat_runs
                    if "wides" not in extras:
                        batting_match_balls[batter] += 1
                        
                    if bat_runs == 4 and "non_boundary" not in delivery:
                        batting_match_4s[batter] += 1
                    if bat_runs == 6 and "non_boundary" not in delivery:
                        batting_match_6s[batter] += 1
                        
                    if "wickets" in delivery:
                        for w in delivery["wickets"]:
                            out_players.add(w.get("player_out"))
                            # Bowling wickets (run outs don't count for bowler)
                            if w.get("kind") not in ["run out", "obstructing the field", "retired hurt", "retired out", "timed out", "handled the ball"]:
                                bowling_match_wickets[bowler] += 1
                                
                    # Bowling
                    # Penalty runs and byes/legbyes don't count against bowler, wides/noballs do
                    bowler_runs = total_runs - extras.get("byes", 0) - extras.get("legbyes", 0) - extras.get("penalty", 0)
                    bowling_match_runs[bowler] += bowler_runs
                    if "wides" not in extras and "noballs" not in extras:
                        bowling_match_balls[bowler] += 1
            
            # Aggregate match stats into career stats
            for batter, runs in batting_match_runs.items():
                b = players_data[batter]["batting"]
                b["innings"] += 1
                b["runs"] += runs
                b["balls_faced"] += batting_match_balls[batter]
                b["4s"] += batting_match_4s[batter]
                b["6s"] += batting_match_6s[batter]
                b["scores"].append(runs)
                
                if batter not in out_players:
                    b["not_outs"] += 1
                    
                if runs > b["highest"]:
                    b["highest"] = runs
                    
                if runs >= 100: b["100s"] += 1
                elif runs >= 50: b["50s"] += 1
                
            for bowler, balls in bowling_match_balls.items():
                w = players_data[bowler]["bowling"]
                if balls > 0 or bowling_match_runs[bowler] > 0 or bowling_match_wickets[bowler] > 0:
                    w["innings"] += 1
                    
                w["balls_bowled"] += balls
                w["runs_conceded"] += bowling_match_runs[bowler]
                wks = bowling_match_wickets.get(bowler, 0)
                w["wickets"] += wks
                
                # Check best bowling
                old_w, old_r = w["best"]
                if wks > old_w or (wks == old_w and bowling_match_runs[bowler] < old_r):
                    w["best"] = [wks, bowling_match_runs[bowler]]
                    
    print("Done crunching numbers.")
    
    # Save processed aggregate logic
    with open("cricsheet_aggregated.json", "w") as f:
        # Convert sets to lists
        out = {}
        for p, d in players_data.items():
            d["matches_played"] = len(d["matches_played"])
            d["batting"].pop("scores")
            out[p] = dict(d)
        json.dump(out, f, indent=2)

if __name__ == "__main__":
    calculate_stats()
