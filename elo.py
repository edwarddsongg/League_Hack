import math 
from dataclasses import dataclass

@dataclass
class Elo:
    teams: list 
    team_dict: dict 
    team_elos: dict
    team_games_played: dict
    team_k_score: dict
    team_region: dict

    def init(self):
        self.team_k_score = {team: 0 for team in self.team_dict.keys()}
        self.team_games_played = {team: 0 for team in self.team_dict.keys()}


    def estimated_win(self, r_a, r_b):
        e_a = 1/(1+10**((r_b - r_a)/400))
        e_b = 1 - e_a
        
        return e_a, e_b

    def update_score(self, t_a, t_b, t1wins):
        e_a, e_b = self.estimated_win(self.team_elos[t_a], self.team_elos[t_b])
        
        self.team_games_played[t_a] = 1
        self.team_games_played[t_b] += 1
        
        self.team_k_score[t_a] = 50/(1+self.team_games_played[t_a]/300)
        self.team_k_score[t_b] = 50/(1+self.team_games_played[t_b]/300)

        self.team_elos[t_a] = self.team_elos[t_a] + self.team_k_score[t_a] * (t1wins - e_a)
        self.team_elos[t_b] = self.team_elos[t_b] + self.team_k_score[t_b] * ((1 - t1wins) - e_b)


    def region_print(self, ids):
        region = self.team_region[ids]
        print(region.name)
        for team in region.teams.keys():
            print(self.team_dict[team]["slug"] + ":" + str(self.team_elos[team]))
        print("-------")

    def team_elo_print(self, ids):
        print(self.team_dict[ids]["slug"] + ":" + str(self.team_elos[ids]))

    def print_elo_list(self, team_list):
        elo_list = []
        for team in team_list:
            elo_list.append({self.team_dict[team]["slug"]:self.team_elos[team]})
        
        sorted_array = sorted(elo_list, key=lambda x: list(x.values())[0], reverse=True)

        for team in sorted_array:
            team_name, score = list(team.items())[0]
            print(f"{team_name}: {score}")

    def print_all_regions(self):
        for region in self.team_region.keys():
            self.region_print(region)

    def return_elo_list(self, team_list):
        elo_list = []
        for team in team_list:
            elo_list.append({self.team_dict[team]["slug"]:self.team_elos[team]})
        
        sorted_array = sorted(elo_list, key=lambda x: list(x.values())[0], reverse=True)

        return sorted_array

