import requests
import json
import gzip
import shutil
import time
import os
from io import BytesIO


S3_BUCKET_URL = "https://power-rankings-dataset-gprhack.s3.us-west-2.amazonaws.com"

def download_gzip_and_write_to_json(file_name, pathName):
   local_file_name = file_name.replace(":", "_")
   local_path_name = pathName.replace(":", "_")
   # If file already exists locally do not re-download game
   if os.path.isfile(f"{local_path_name}.json"):
       return

   response = requests.get(f"{S3_BUCKET_URL}/{file_name}.json.gz")
   if response.status_code == 200:
       try:
           gzip_bytes = BytesIO(response.content)
           with gzip.GzipFile(fileobj=gzip_bytes, mode="rb") as gzipped_file:
               with open(f"{local_path_name}.json", 'wb') as output_file:
                   shutil.copyfileobj(gzipped_file, output_file)
               print(f"{local_path_name}.json written")
       except Exception as e:
           print("Error:", e)
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
        tournament_ids.append(tourn['id'])
  
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
    if tourneyId in ids and tourneyStart.startswith("2023"):
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

                          download_gzip_and_write_to_json(f"{'games'}/{platform_game_id}", f"{directory}/{platform_game_id}")
      
      
    

ids = getTournamentIDs("KOREA")
downloadTourneyData(ids)