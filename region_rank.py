import json 
import os 
import time
from Region import Region

start_time = time.time()



directory = 'games'


#read all the files
with open('../esports-data/players.json', 'r', encoding='utf-8') as json_file:
    player_data = json.load(json_file)

with open('../esports-data/mapping_data.json', 'r', encoding='utf-8') as json_file:
    mapping_data = json.load(json_file)

with open('../esports-data/leagues.json', 'r', encoding='utf-8') as json_file:
    league_data = json.load(json_file)

with open('../esports-data/tournaments.json', 'r', encoding='utf-8') as json_file:
    tournament_data = json.load(json_file)

with open('../esports-data/teams.json', 'r', encoding='utf-8') as json_file:
    team_data = json.load(json_file)

#store info on regions: region[name] = region object
region_dictionary = {}
region_array = []

#store info on regions: tournament[id] = team_list
tournament_dictionary = {}

for league in league_data:
    region = Region(league["name"])
    region_array.append(region)
    region_dictionary[league["name"]] = region
    
    for tournament in league["tournaments"]:
        region.add_tournament(tournament["id"])

#team_names for readability:
team_name_dict = {team["team_id"]: team for team in team_data}

#tournamnet id for access
tournament_id_dict = {tournament["id"]: tournament for tournament in tournament_data}

for region in region_array:
    region_tournaments = region.get_tournaments()
  
    for tournament_id in region_tournaments:
        
        try:
            tournament = tournament_id_dict[tournament_id]
        except:
            continue
        
        if "msi" in tournament["slug"] or "worlds" in tournament["slug"]:
            continue

        for stage in tournament["stages"]:
            for section in stage["sections"]:
                for match in section["matches"]:
                    for game in match["games"]:
                        if game["state"] == "completed":
                            
                            try:
                                t1 = game["teams"][0]["id"]
                                t2 = game["teams"][1]["id"]

                                region.add_team(t1, team_name_dict[t1]["name"])
                                region.add_team(t2, team_name_dict[t2]["name"])
                            except:
                                continue
                            


#team_data for international tournaments
for tournament in tournament_data:
    
    if "msi" not in tournament["slug"] and "worlds" not in tournament["slug"]:
        continue
    
    print(tournament["slug"])
  
    last_stage = tournament["stages"][-1]  
  
    last_section = last_stage["sections"][-1]
    
    last_match = last_section["matches"][-1]
    
       
    recent_winner = ""

    for game in last_match["games"]:
        print(game["id"])
        if game["state"] == "completed":
            t1 = game["teams"][0]
            t2 = game["teams"][1]

            if t1["result"]["outcome"] == "win":
                recent_winner = t1
            elif t2["result"]["outcome"] == "win":
                recent_winner = t2
        else:
            break

    print(team_name_dict[recent_winner["id"]]["slug"], "is winner of ", tournament["slug"])

                        



print("--- %s seconds ---" % (time.time() - start_time))
                 

