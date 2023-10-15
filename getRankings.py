import pandas as pd
import numpy as np
import json
import os


def calculate_expected_result(rating_a, rating_b):
    """
    Calculate the expected outcome for player A based on their Elo ratings.
    """
    return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))


def update_ratings(rating_a, rating_b, outcome, k=32):
    """
    Update Elo ratings for two players based on the outcome of a match.
    """
    expected_a = calculate_expected_result(rating_a, rating_b)
    expected_b = 1 - expected_a

    new_rating_a = rating_a + k * (outcome - expected_a)
    new_rating_b = rating_b + k * ((1 - outcome) - expected_b)

    return new_rating_a, new_rating_b


teams = []
initial_ratings = []
for tournaments in os.listdir('FilteredData'):
  with open('FilteredData/'+tournaments, 'r') as json_file:
    results = json.load(json_file)

  for tour in results:
      teamOne = tour.get('teamOne')
      teamTwo = tour.get('teamTwo')
      if teamOne not in teams:
        teams.append(teamOne)
        adjFactor = tour.get('priority')
        if adjFactor < 10: adjFactor = 1
        initial_ratings.append(1500 / adjFactor)

      if teamTwo not in teams:
        teams.append(teamTwo)
        if adjFactor < 10: adjFactor = 1
        initial_ratings.append(1500 / adjFactor)

# Create a DataFrame to store ratings
df = pd.DataFrame({"team": teams, "Rating": initial_ratings})

for tournaments in os.listdir('FilteredData'):
  with open('FilteredData/'+tournaments, 'r') as json_file:
    results = json.load(json_file)
  for tour in results:
      teamOne = tour.get("teamOne")
      teamTwo = tour.get("teamTwo")
      outcome = 1 if tour.get("winningTeam") == teamOne else 0

      new_rating_one, new_rating_two = update_ratings(df.loc[df["team"] == teamOne, "Rating"].values[0],
                                                      df.loc[df["team"] == teamTwo, "Rating"].values[0], outcome)

      df.loc[df["team"] == teamOne, "Rating"] = new_rating_one
      df.loc[df["team"] == teamTwo, "Rating"] = new_rating_two


returnDict = df.to_dict('records')

with open('esports-data/teams.json', 'r') as json_file:
    proTeams = json.load(json_file)

for val in returnDict:
    teamId = val.get("team")
    for pro in proTeams:
        if pro.get("team_id") == teamId:
            val.update({"name": pro.get("name")})

print(returnDict)
with open("randomLeague_rankings.json", "w") as outfile:
    json.dump(
        sorted(returnDict, key=lambda x: x['Rating'], reverse=True), outfile)
