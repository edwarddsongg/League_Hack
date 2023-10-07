class Region:
    def __init__(self, name):
        self.name = name 
        self.teams = {}
        self.team_id = []
        self.rating = 0
        self.tournament = []
        self.interational_wins = 0

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

    def add_interational_wins(self):
        self.international_wins += 1