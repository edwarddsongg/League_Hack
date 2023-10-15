import requests
import json
import gzip
import shutil
import time
import os
from io import BytesIO


S3_BUCKET_URL = "https://power-rankings-dataset-gprhack.s3.us-west-2.amazonaws.com"

def download_gzip_and_write_to_json(file_name, pathName, priority):
   local_path_name = pathName.replace(":", "_")
   # If file already exists locally do not re-download game
   if os.path.isfile(f"{local_path_name}.json"):
       return

   response = requests.get(f"{S3_BUCKET_URL}/{file_name}.json.gz")
   if response.status_code == 200:
      gzip_bytes = BytesIO(response.content)
      with gzip.GzipFile(fileobj=gzip_bytes, mode="rb") as gzipped_file:
        gameData = json.load(gzipped_file)

      gameResults = gameData[-1]

      extracted_data = {
        # "platformId": "ESPORTSTMNT01:3303528",
        # "teamOne": "105550042327365041",
        # "teamTwo": "105550051809743868",
        # "winningTeam": "105550051809743868",
        # "losingTeam": "105550042327365041",
        # "priority": "lmao?"
      }

      if "platformGameId" in gameResults and "winningTeam" in gameResults:
        with open('esports-data/mapping_data.json', 'r') as json_file:
          mapp = json.load(json_file)

        platformId = gameResults.get('platformGameId')
        winningTeam = gameResults.get('winningTeam')
        for m in mapp:
            if m.get('platformGameId') == platformId:
              extracted_data.update({
                  "priority": priority,
                  "platformId": platformId,
                  "teamOne": m.get('teamMapping').get('100'),
                  "teamTwo": m.get('teamMapping').get('200')
              })
        
        mappedWinTeam = extracted_data.get("teamOne") if winningTeam == '100' else extracted_data.get("teamTwo")
        mappedLoseTeam = extracted_data.get("teamTwo") if winningTeam == '100' else extracted_data.get("teamOne")
        extracted_data.update({'winningTeam': mappedWinTeam, 'losingTeam': mappedLoseTeam})
      
        with open(f"{local_path_name}.json", 'w') as output_file:
            json.dump(extracted_data, output_file, indent=2)

        print(f"{local_path_name}.json written")
   else:
       print(f"Failed to download {file_name}")

def getTournamentIDs(region):
  start_time = time.time()
  with open("esports-data/leagues.json", "r") as json_file:
    league_data = json.load(json_file)

  tournament_ids = []

  for league in league_data:
    if league['region'] == region:
      tourneys = league['tournaments']
      for tourn in tourneys:
        tournament_ids.append({"id": tourn['id'], "prio": league['priority']})
  
  return tournament_ids

def downloadTourneyData(ids):
  with open("esports-data/tournaments.json", "r") as json_file:
    tournaments_data = json.load(json_file)
  with open("esports-data/mapping_data.json", "r") as json_file:
    mappings_data = json.load(json_file)

  mappings = {
    esports_game["esportsGameId"]: esports_game for esports_game in mappings_data
  }
  count = 0
  for tournament in tournaments_data:
    tourneyId = tournament['id']
    tourneyStart = tournament.get("startDate", "")
    directory = "games/" + tournament['slug']
    if any(obj['id'] == tourneyId for obj in ids) and tourneyStart.startswith("2023"):
      if count == 0:
        count += 1
        continue
      print(f"Processing {tournament['slug']}")
      if not os.path.exists(directory):
          os.makedirs(f"games/{tournament['slug']}")
                      
      for stage in tournament["stages"]:
          for section in stage["sections"]:
              for match in section["matches"]:
                  for game in match["games"]:
                      if game["state"] == "completed":
                          try:
                              platform_game_id = mappings[game["id"]]["platformGameId"]
                          except KeyError:
                              print(f"{platform_game_id} {game['id']} not found in the mapping table")
                              continue
                          
                          priority = 0

                          for ide in ids:
                             if ide.get('id') == tourneyId:
                                priority = ide.get('prio')
                          download_gzip_and_write_to_json(f"{'games'}/{platform_game_id}", f"{directory}/{platform_game_id}", priority)
      
      
    

ids = getTournamentIDs("KOREA")
downloadTourneyData(ids)