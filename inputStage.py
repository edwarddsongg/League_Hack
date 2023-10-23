import os
import json

def addEsportsId():
  for tourney in os.listdir('FilteredData'):
    updatedName = tourney.split('.')[0]
    print(updatedName)
    outputArray = []
    with open('FilteredData/'+tourney, 'r') as json_file:
      results = json.load(json_file)
    
    with open('esports-data/tournaments.json', 'r') as json_file:
      tourneyData = json.load(json_file)
      
    with open('esports-data/mapping_data.json', 'r') as json_file:
      mappingData = json.load(json_file)

    for res in results:
      platgormId = res.get('platformId')

      for mop in mappingData:
        if mop.get("platformGameId") == platgormId:
          res.update({"esportsId": mop.get("esportsGameId")})
        
          outputArray.append(res)
    
    with open('FilteredData/'+updatedName+'.json', "w") as outfile:
      json.dump(outputArray, outfile, indent=2)

def addStage():
  for tourney in os.listdir('FilteredData'):
    updatedName = tourney.split('.')[0]

    outputArray = []

    with open('FilteredData/'+tourney, 'r') as json_file:
      results = json.load(json_file)
    
    with open('esports-data/tournaments.json', 'r') as json_file:
      tourneyData = json.load(json_file)
      
    with open('esports-data/mapping_data.json', 'r') as json_file:
      mappingData = json.load(json_file)

    for data in tourneyData:
      if data.get("slug")+"_results" != updatedName:
        continue
      
      stages = data.get("stages")
      count = 0
      for stage in stages:
        name = stage.get("slug")
        sections = stage.get("sections")
        for sec in sections:
          matches = sec.get('matches')
          for match in matches:
            if name == 'playoffs' or 'knockouts':
              count += 1
            games = match.get('games')

            for game in games:
              gameId = game.get('id')

              for res in results: 
                if res.get("esportsId") == gameId:
                  weight = 1
                  if name == 'playoffs' or name == 'knockout':
                    weight = 2
                  if count > 4:
                    weight = 3
                  if weight > 6:
                    weight = 4
                  res.update({"stage": name, "weight": weight})
                  outputArray.append(res)

    with open('FilteredData/'+updatedName+'.json', "w") as outfile:
      json.dump(outputArray, outfile, indent=2)

addStage()