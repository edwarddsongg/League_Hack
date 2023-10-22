import os
import json

with open("esports-data/tournaments.json", "r") as json_file:
  tournaments_data = json.load(json_file)

def getPlatformId(id):
  with open("esports-data/mapping_data.json", "r") as json_file:
    mapping_data = json.load(json_file)

    
    for mop in mapping_data:
      if mop.get("esportsGameId") == id:
        return mop.get("platformGameId")


export_array = []

for tournament in tournaments_data:
  startDate = tournament.get("startDate")
  stages = tournament.get("stages")

  # if tournament.get("slug") != "vcs_summer_2023":
  #   continue

  print(tournament.get("slug"))

  for stage in stages:
    stageName = stage.get("slug")
    sections = stage.get("sections")
    for sec in sections: 
      matches = sec.get("matches")
      gameCount = 1
      for match in matches:
        if match.get("state") == "unstarted":
          continue
        games = match.get("games")
        for game in games:
          try: 
            gameId = game.get("id")
            teamOne = game.get("teams")[0].get("id")
            teamTwo = game.get("teams")[1].get("id")
            winningTeam = teamOne if game.get("teams")[0].get("result").get("outcome") == "win" else teamTwo
            losingTeam = teamOne if game.get("teams")[1].get("result").get("outcome") == "win" else teamTwo
          except KeyError:
            print("ERROR WITH " + gameId)
            continue
          weight = 1
          if stageName == "knockouts" or stageName == "playoffs":
            if gameCount == 7:
              weight = 3
            elif gameCount < 5:
              weight = 2
            elif gameCount < 7:
              weight = 2.5


          platformId = ""

          
          outputObj = {
            "tournament": tournament.get("slug"),
            "gameId": gameId,
            "platformId": getPlatformId(gameId),
            "startDate": startDate,
            "teamOne": teamOne,
            "teamTwo": teamTwo,
            "winTeam": winningTeam,
            "loseTeam": losingTeam,
            "weight": weight,
            "stage": stageName
          }

          export_array.append(outputObj)

        if stageName == "knockouts" or stageName == "playoffs":
            gameCount += 1


with open(f"tournaments_game_info.json", 'w') as output_file:
  json.dump(export_array, output_file, indent=2)
