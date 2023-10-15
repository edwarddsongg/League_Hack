class Region:
    def __init__(self, name, ids):
        self.name = name 
        self.teams = {}
        self.team_id = []
        self.rating = 0
        self.tournament = []
        self.international_score = 0
        self.id = ids
        self.elo_teams = []

    def add_tournament(self, id):
        self.tournament.append(id)
    
    def print_tournament(self):
        print(self.name)
        print("------")
        print(self.tournament)
        print("-------")

    def get_tournaments(self):
        return self.tournament

    def add_team(self, ids, name):
        self.teams[ids] = name

    def print_team(self):
        print(self.name)
        print("----------")
        for team_name in self.teams.values():  # Iterate over the values (team names)
            print(team_name)
        print("------")

    def add_international_score(self, score):
        self.international_score += score
    
    def get_international_score(self):
        return self.international_score