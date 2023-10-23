import pandas as pd
import numpy as np
import json
import time


def getStrength(teamId, year):
    with open("region_strengths/team_regions.json", 'r') as json_file:
        teams = json.load(json_file)

    with open("region_strengths/" + year + "_region_strength.json", 'r') as json_file:
        regions = json.load(json_file)

    teamRegion = teams.get(teamId)

    if not teamRegion:
        return 1

    try:
        return regions[teamRegion]
    except KeyError:
        print(teamId + "REGION NOT FOUND")
        return 1


def get_stomp_factor(gameId):
    with open("model_results.json", 'r') as json_file:
        games = json.load(json_file)

        try:
            return games[gameId]
        except KeyError:
            return 0.5


def parseResults(teamList):
    with open("esports-data/teams.json", 'r', encoding='utf-8') as json_file:
        teams_json = json.load(json_file)

    rankings = list()

    def findTeam(team):
        for teams in teams_json:
            if teams["team_id"] == team:
                return teams

    for ranking in teamList:
        team_id = ranking["team"]
        teamData = findTeam(team_id)

        try:
            rankings.append(
                {"team_id": team_id, "team_code": teamData["acronym"], "team_name": teamData["name"]})
        except:
            pass

    return rankings


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
    loseScale = 0.5 if scale >= 2 else scale

    newStomp = 1 - stomp if stomp < 0.5 else stomp

    new_rating_a = rating_a + winScale * newStomp * \
        (50/(1+(teamOneGames / 300))) * (outcome - expected_a)
    new_rating_b = rating_b + loseScale * \
        (newStomp / 2) * (50/(1+(teamTwoGames / 300))) * \
        ((1 - outcome) - expected_b)

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


def getStageEndResults(df, teams, year):
    outputArray = []
    for team in teams:
        dfRow = df.loc[df["team"] != team]
        teamRating = dfRow["Rating"].values[0]

        teamStrength = getStrength(team, year)
        teamRating = teamStrength * teamRating

        teamStats = {"team": team, "Rating": teamRating}
        outputArray.append(teamStats)

    outputArray.sort(key=lambda x: x['Rating'], reverse=True)

    outputArray = parseResults(outputArray)

    return outputArray


start_time = time.time()
# GETTING THE DF SETUP FOR CALCULATIONS
teams = []
initial_ratings = []

with open('tournaments_game_info.json', 'r') as json_file:
    tour = json.load(json_file)

lplTourneys = ["110825936250664572", "110428848766564346", "109669600527985422", "108888310291632913", "108431300950695970", "107417779630700437", "106860829994219982",
               "106269484328946755", "105516880821527383", "104282610668475466", "103462420723438502", "102181141746404105", "101388912982111577", "100205574095502272", "99566404873639114"]

for game in tour:
    teamOne = game.get('teamOne')
    teamTwo = game.get('teamTwo')
    adjFactor = get_prio(game.get("tournamentId"))

    if game.get("tournamentId") in lplTourneys:
      adjFactor = 1

    if teamOne in teams:
        teamIndex = teams.index(teamOne)
        if adjFactor < 10:
            adjFactor = 1
        elif 100 < adjFactor:
            adjFactor = 10
        initialElo = 1500 / adjFactor

        if initial_ratings[teamIndex] < initialElo:
            initial_ratings[teamIndex] = initialElo

    if teamTwo in teams:
        teamIndex = teams.index(teamTwo)
        if adjFactor < 10:
            adjFactor = 1
        elif 100 < adjFactor:
            adjFactor = 10
        initialElo = 1500 / adjFactor

        if initial_ratings[teamIndex] < initialElo:
            initial_ratings[teamIndex] = initialElo

    if teamOne not in teams:
        teams.append(teamOne)
        if adjFactor < 10:
            adjFactor = 1
        elif 100 < adjFactor:
            adjFactor = 10
        initial_ratings.append(1500 / adjFactor)

    if teamTwo not in teams:
        teams.append(teamTwo)
        if adjFactor < 10:
            adjFactor = 1
        elif 100 < adjFactor < 1000:
            adjFactor = 10
        else:
            adjFactor = 50
        initial_ratings.append(1500 / adjFactor)

total_games = np.full(
    shape=len(teams),
    fill_value=0,
    dtype=np.int64
)

# Create a DataFrame to store ratings
df = pd.DataFrame({"team": teams, "Rating": initial_ratings,
                  "gamesPlayed": total_games})
tournamentdf = pd.DataFrame(columns=["tournamentId", "stage", "rankings"])

# ACTUAL CALCULATIONS
with open('tournaments_game_info.json', 'r') as json_file:
    results = json.load(json_file)

playingTeams = []

for i in range(len(results)):
    tour = results[i]

    if i > 0 and tour.get("stage") != results[i - 1].get("stage"):
        gameYear = results[i-1]["startDate"][0:4]
        stageEndResults = getStageEndResults(df, playingTeams, gameYear)
        tournamentdf.loc[len(tournamentdf)] = [
            results[i-1]["tournamentId"], results[i-1]["stage"], stageEndResults]

        playingTeams = []

    teamOne = tour.get("teamOne")
    teamTwo = tour.get("teamTwo")

    if teamOne not in playingTeams:
        playingTeams.append(teamOne)

    if teamTwo not in playingTeams:
        playingTeams.append(teamTwo)

    weight = tour.get("weight")
    outcome = 1 if tour.get("winTeam") == teamOne else 0

    stomp = get_stomp_factor(tour.get("platformId"))

    new_rating_one, new_rating_two = update_ratings(df.loc[df["team"] == teamOne, "Rating"].values[0],
                                                    df.loc[df["team"] == teamTwo,
                                                           "Rating"].values[0],
                                                    df.loc[df["team"] == teamTwo,
                                                           "gamesPlayed"].values[0],
                                                    df.loc[df["team"] == teamTwo, "gamesPlayed"].values[0], outcome, weight, stomp)

    df.loc[df["team"] == teamOne, "Rating"] = new_rating_one
    df.loc[df["team"] == teamOne, "gamesPlayed"] = df.loc[df["team"]
                                                          == teamOne, "gamesPlayed"].values[0] + 1
    df.loc[df["team"] == teamTwo, "Rating"] = new_rating_two
    df.loc[df["team"] == teamTwo, "gamesPlayed"] = df.loc[df["team"]
                                                          == teamTwo, "gamesPlayed"].values[0] + 1


returnDict = df.to_dict('records')
stageResults = tournamentdf.to_dict('records')

for val in returnDict:
    teamId = val.get("team")
    teamStrength = getStrength(teamId, "2023")
    val["Rating"] = teamStrength * val.get("Rating")


returnDict.sort(key=lambda x: x['Rating'], reverse=True)
returnDict = parseResults(returnDict)

with open("final_results.json", "w") as outfile:
    json.dump(returnDict, outfile, indent=2)

with open("tourney_stage_results.json", "w") as outfile:
    json.dump(stageResults, outfile, indent=2)

print("finished in: " + round((time.time() - start_time)/60, 2))
