import json 
import os 
import time
from Region import Region

import numpy as np
import pandas as pd

def rank():
    start_time = time.time()



    directory = '../international-games/games'

    print(len(directory))
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
                                
    for tournament in international_tournament_data:
        max_score = len(tournament["teams"])
        
        for idx, team in enumerate(tournament["teams"]):
        
            team_region = team_region_map[team]
            
            region = region_dictionary[team_region]
        
            region.add_international_score(max_score - idx)


    #ranking international teams:
    #store the matrices for each stage
    data_grids = []

    #team_data for international tournaments
    international_tournament_map = {tournament["id"]: tournament for tournament in international_tournament_data}

    for tournament in tournament_data:
        if "msi" not in tournament["slug"] and "worlds" not in tournament["slug"]:
            continue
        print(tournament["slug"])
        for stage in tournament["stages"]:       
            for section in stage["sections"]:
                if len(section["rankings"]) == 0:
                    print(section["name"]) 

                total_teams = len(section["rankings"])
                team_list = []


                for team in section["rankings"]:
                    print
                    team_list.append(team["teams"][0]["id"])

                team_grid_spot = {team:idx for idx, team in enumerate(team_list)}
                

                data_grid = np.zeros([total_teams, total_teams])
                data_vector = np.zeros(total_teams)


                for match in section["matches"]: 
                    for game in match["games"]:
                        if game["state"] == "completed":
                            try:
                                t1 = match["teams"][0]["id"]
                                t2 = match["teams"][1]["id"]
                            
                                team_index_one = team_grid_spot[t1]
                                team_index_two = team_grid_spot[t2]
                             
                                data_grid[team_index_one][team_index_one] += 1 
                                data_grid[team_index_two][team_index_two] += 1
                                data_grid[team_index_one][team_index_two] -= 1
                                data_grid[team_index_two][team_index_one] -= 1

                                if match["teams"][0]["result"]["outcome"] == "win":
                                    data_vector[team_index_one] += 1
                                    data_vector[team_index_two] -= 1
                                else:
                                    data_vector[team_index_one] -= 1
                                    data_vector[team_index_two] += 1

                            except:
                                return
                
                print(section["name"])
                
                print("--------") 
                print("ONE SECTION:")
                diag = data_grid.diagonal() + 2
                np.fill_diagonal(data_grid, diag)
                print(data_grid)
                for i, value in enumerate(data_vector):
                    data_vector[i] = data_vector[i]/2
                    data_vector[i] += 1
                print(data_vector)
                r = np.linalg.solve(data_grid, diag)
                print(r)
                indices = r.argsort()[::-1]
                
                for idx in indices:
                    print(str(r[idx]), team_name_dict[team_list[idx]]["name"])
            
                        

    print("--- %s seconds ---" % (time.time() - start_time))


if __name__== '__main__':
    rank()