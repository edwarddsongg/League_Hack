import os
import json

path = '/Users/shawnxue/Documents/Code Projects/League Hackathon/games'

pathtwo = '/Users/shawnxue/Documents/Code Projects/League Hackathon/esports-data'


def filterResults():
  for folder in os.listdir('games'):
    export_array = []
    for filename in os.listdir('games/'+folder):
      if filename.endswith('.json'):
        with open('games/'+folder+'/'+filename, 'r') as json_file:
          results = json.load(json_file)

        with open('esports-data/mapping_data.json', 'r') as json_file:
          mapp = json.load(json_file)

        found = False

        gameData = {}

        for index in results:
          keys = index.keys()
          if "platformGameId" in keys and not found:
            found = True
            gameId = index.get("platformGameId")
            print(gameId)
            for m in mapp:
              if m.get("platformGameId") == gameId:
                teamData = {
                  'platformId': gameId,
                  'teamOne': m.get('teamMapping').get('100'),
                  'teamTwo': m.get('teamMapping').get('200')
                }
                gameData.update(teamData)

        for index in results: 
          keys = index.keys()
          if "winningTeam" in keys:
            winningTeam = index.get('winningTeam')
            mappedWinTeam = gameData.get("teamOne") if winningTeam == '100' else gameData.get("teamTwo")
            mappedLoseTeam = gameData.get("teamTwo") if winningTeam == '100' else gameData.get("teamOne")
            gameData.update({'winningTeam': mappedWinTeam, 'losingTeam': mappedLoseTeam})

        export_array.append(gameData)

    with open(folder+"_results.json", "w") as outfile:
      json.dump(export_array, outfile)



filterResults()