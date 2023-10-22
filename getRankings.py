import pandas as pd
import numpy as np
import json
import os

def getStrength(teamId):
  with open("region_strengths/team_region.json", 'r') as json_file:
    teams = json.load(json_file)

  with open("region_strengths/2023_region_strength.json", 'r') as json_file:
    regions = json.load(json_file)

  teamRegion = teams.get(teamId)

  try:
     return regions.get(teamRegion)
  except KeyError:
     print(teamRegion + "REGION NOT FOUND")
     return 1

def get_stomp_factor(gameId):
   with open("model_results.json", 'r') as json_file:
      games = json.load(json_file)
      
      try:
        return games[gameId]
      except KeyError:
         return 0.5

def calculate_expected_result(rating_a, rating_b):
    """
    Calculate the expected outcome for player A based on their Elo ratings.
    """
    return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))


def update_ratings(rating_a, rating_b, teamOneGames, teamTwoGames, outcome, scale, stomp):
    """
    Update Elo ratings for two players based on the outcome of a match.
    """
    expected_a = calculate_expected_result(rating_a, rating_b)
    expected_b = 1 - expected_a

    winScale = scale
    loseScale = 1 if scale > 2 else scale

    new_rating_a = rating_a + winScale * stomp * (50/(1+(teamOneGames / 300))) * (outcome - expected_a)
    new_rating_b = rating_b + loseScale * stomp * (50/(1+(teamTwoGames / 300))) * ((1 - outcome) - expected_b)

    return new_rating_a, new_rating_b


def get_prio(tournamentId):
  with open('esports-data/leagues.json', 'r') as json_file:
    leagues = json.load(json_file)

    for league in leagues:
      prio = league.get("priority")
      tournaments = league.get("tournaments")
      for tourn in tournaments:
        if tourn.get("id") == tournamentId:
          return prio

  
  return 1000

teams = []
initial_ratings = []
with open('tournaments_game_info.json', 'r') as json_file:
    tour = json.load(json_file)

for game in tour: 
  teamOne = game.get('teamOne')
  teamTwo = game.get('teamTwo')
  if teamOne not in teams:
      teams.append(teamOne)
      adjFactor = get_prio(game.get("tournamentId"))
      if adjFactor < 10: adjFactor = 1
      elif 100 < adjFactor: adjFactor = 10
      initial_ratings.append(1500 / adjFactor)

  if teamTwo not in teams:
      teams.append(teamTwo)
      if adjFactor < 10: adjFactor = 1
      elif 100 < adjFactor < 1000: adjFactor = 10
      else: adjFactor = 50
      initial_ratings.append(1500 / adjFactor)

total_games = np.full(
  shape=len(teams),
  fill_value=0,
  dtype=np.int64
)
# Create a DataFrame to store ratings
df = pd.DataFrame({"team": teams, "Rating": initial_ratings, "gamesPlayed": total_games})

with open('tournaments_game_info.json', 'r') as json_file:
  results = json.load(json_file)
for tour in results:
    teamOne = tour.get("teamOne")
    teamTwo = tour.get("teamTwo")
    weight = tour.get("weight")
    outcome = 1 if tour.get("winTeam") == teamOne else 0

    stomp = get_stomp_factor(tour.get("platformId"))
      

    print(tour.get("platformId"))
    print(stomp)
    
    new_rating_one, new_rating_two = update_ratings(df.loc[df["team"] == teamOne, "Rating"].values[0],
                                                    df.loc[df["team"] == teamTwo, "Rating"].values[0],
                                                    df.loc[df["team"] == teamTwo, "gamesPlayed"].values[0],
                                                    df.loc[df["team"] == teamTwo, "gamesPlayed"].values[0], outcome, weight, stomp)

    df.loc[df["team"] == teamOne, "Rating"] = new_rating_one
    df.loc[df["team"] == teamOne, "gamesPlayed"] = df.loc[df["team"] == teamOne, "gamesPlayed"].values[0] + 1
    df.loc[df["team"] == teamTwo, "Rating"] = new_rating_two
    df.loc[df["team"] == teamTwo, "gamesPlayed"] = df.loc[df["team"] == teamTwo, "gamesPlayed"].values[0] + 1


returnDict = df.to_dict('records')

with open('esports-data/teams.json', 'r') as json_file:
    proTeams = json.load(json_file)

for val in returnDict:
    teamId = val.get("team")
    val["Rating"] = getStrength(teamId) * val.get("Rating")

    for pro in proTeams:
        if pro.get("team_id") == teamId:
            val.update({"name": pro.get("name")})

print(returnDict)
with open("test_rankings.json", "w") as outfile:
    json.dump(
        sorted(returnDict, key=lambda x: x['Rating'], reverse=True), outfile, indent=2)