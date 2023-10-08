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

with open('international_tournament_results.json', 'r', encoding='utf-8') as json_file:
    international_tournament_data = json.load(json_file)

#store info on regions: region[name] = region object
region_dictionary = {}
region_array = []

#store info on regions: tournament[id] = team_list
tournament_dictionary = {}

for league in league_data:
    region = Region(league["name"], league["id"])
    region_array.append(region)
    region_dictionary[league["id"]] = region
    
    for tournament in league["tournaments"]:
        region.add_tournament(tournament["id"])

#team_names for readability:
team_name_dict = {team["team_id"]: team for team in team_data}

#tournamnet id for access
tournament_id_dict = {tournament["id"]: tournament for tournament in tournament_data}

#map each league to its id
league_id_dict = {league["id"]: league for league in league_data}

# map each team to a region, we only care about international teams
team_region_map = {} 

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

                                team_region_map[t1] = region.id
                                team_region_map[t2] = region.id

                                region.add_team(t1, team_name_dict[t1]["name"])
                                region.add_team(t2, team_name_dict[t2]["name"])
                            except:
                                continue
                            


#team_data for international tournaments
for tournament in international_tournament_data:
    max_score = len(tournament["teams"])
    
    for idx, team in enumerate(tournament["teams"]):
        print(team_name_dict[team]["name"], team)
        team_region = team_region_map[team]
        
        region = region_dictionary[team_region]
        print(region.name)

        region.add_international_score(max_score - idx)


for region in region_dictionary.values():
    print(region.name, ":", region.get_international_score())
                        

print("--- %s seconds ---" % (time.time() - start_time))
                 