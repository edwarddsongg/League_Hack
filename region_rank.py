import json 
import os 
import time
from Region import Region
from elo import Elo
import numpy as np
import pandas as pd
from statistics import mean

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

    list_teams = [team_id for team_id in team_name_dict.keys()]

    elo_system = Elo(list_teams, team_name_dict, {team_id:1500 for team_id in team_name_dict.keys()}, {}, {}, region_dictionary)
    elo_system.init()


    for tournament in tournament_data:
        if "msi" not in tournament["slug"] and "worlds" not in tournament["slug"]:
            continue
        print(tournament["slug"])
        for stage in tournament["stages"]:       
            for section in stage["sections"]:
                weight = 1

                playoffs = False
                print(section["name"])
                if("group" in section["name"].lower()): weight = 1.2
                elif("Play in Knockouts" == section["name"]): weight = 0.6
                elif("knockouts" == section["name"] or "playoffs" == section["name"].lower()): 
                    print("test")
                    weight = 1.6
                    playoffs = True
               
                count = 0

                for match in section["matches"]: 
                    count += 1
                    if(count == 5 and playoffs): weight += 0.2
                    if(count == 7 and playoffs): weight += 0.4
                    # print(weight)

                    for game in match["games"]:
                        if game["state"] == "completed":
                            try:
                                
                                t1 = match["teams"][0]["id"]
                                t2 = match["teams"][1]["id"]

                                if match["teams"][0]["result"]["outcome"] == "win":
                                    elo_system.update_score(t1, t2, 1, weight)
                                else:
                                    elo_system.update_score(t1, t2, 0, weight)
                                
                            except:
                                print("gailes")
                                return
        
    
    for region in region_array:
        if len(region.teams) == 0: continue

        team_arr = [team for team in region.teams.keys()]
        region.elo_teams = elo_system.return_elo_list(team_arr)
        
        rated_list = elo_system.return_rated_elo_list(team_arr)

        if len(rated_list) == 0:
            #this is because they have not played in international tournamnets 
            region.rating = 1200
        else:
            elos = [list(team.items())[0][1] for team in rated_list]
            region.rating = mean(elos)
    
    rated_regions = []
    total_scores = 0
    for region in region_array:
        if region.rating == 0 or region.rating == 1200: continue
        total_scores += region.rating
        rated_regions.append(region)
        print(region.name + ":" + str(region.rating))

    for region in rated_regions:
        if region.rating == 0 or region.rating == 1200: continue
    
        region.strength = region.rating/total_scores + 1

        print(region.name + ":" + str(region.strength))
      
    for region in rated_regions:
        region_score = 0
        for opponent in rated_regions:
            if region.name == opponent.name: continue 
            e_region = elo_system.estimated_win_for_regions(region.rating, opponent.rating)
            region_score += e_region    

    
                        

    print("--- %s seconds ---" % (time.time() - start_time))


if __name__== '__main__':
    rank()