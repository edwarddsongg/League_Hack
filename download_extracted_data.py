import requests
import json
import gzip
import shutil
import time
import os
from io import BytesIO

S3_BUCKET_URL = "https://power-rankings-dataset-gprhack.s3.us-west-2.amazonaws.com"

def download_gzip_and_write_to_json(file_name):
    local_file_name = file_name.replace(":", "_")
    if os.path.isfile(f"{local_file_name}.json"):
        return

    response = requests.get(f"{S3_BUCKET_URL}/{file_name}.json.gz")
    if response.status_code == 200:
        try:
            gzip_bytes = BytesIO(response.content)
            with gzip.GzipFile(fileobj=gzip_bytes, mode="rb") as gzipped_file:
                with open(f"{local_file_name}.json", 'wb') as output_file:
                    shutil.copyfileobj(gzipped_file, output_file)
                print(f"{file_name}.json written")
        except Exception as e:
            print("Error:", e)
    else:
        print(f"Failed to download {file_name}")


# def download_gzip_and_write_to_json_extracted(file_name):
#     local_file_name = file_name.replace(":", "_")
#     if os.path.isfile(f"{local_file_name}.json"):
#         with open(f"{local_file_name}.json", 'r') as json_file:
#             data = json.load(json_file)

#         # Extract only the desired data
#         end_data = data[-2];
#         extracted_data = {
#             "team100TotalGold": 0,
#             "team100TotalDamage": 0,
#             "team200TotalDamage": 0,
#             "team200TotalGold": 0,
#         }

#         if "gameOver" in end_data and end_data["gameOver"] == True:
#             if "teams" in end_data:
#                 teams = end_data["teams"]
#                 for team in teams:
#                     if "teamID" in team and "totalGold" in team and team["teamID"] == 100:
#                         extracted_data["team100TotalGold"] = team["totalGold"]
#                     else:
#                         extracted_data["team200TotalGold"] = team["totalGold"]

#             if "participants" in end_data:
#                 participants = end_data["participants"]
#                 for participant in participants:
#                     total_damage = 0
#                     if "stats" in participant:
#                         stats = participant["stats"]
#                         for stat in stats:
#                             if "name" in stat and stat["name"] == "TOTAL_DAMAGE_DEALT_TO_CHAMPIONS":
#                                 total_damage = stat["value"]

#                     if "teamID" in participant and participant["teamID"] == 100:
#                         extracted_data["team100TotalDamage"] += total_damage
#                     else:
#                         extracted_data["team200TotalDamage"] += total_damage


#         # extracted_data["team100GoldToDamageRatio"] = extracted_data["team100TotalGold"] / extracted_data["team100TotalDamage"]
#         # extracted_data["team200GoldToDamageRatio"] = extracted_data["team200TotalGold"] / extracted_data["team200TotalDamage"]


        

#         # Save the extracted data to a new JSON file
#         with open(f"{local_file_name}_extracted.json", 'w') as output_file:
#             json.dump(extracted_data, output_file, indent=2)

#         print(f"{file_name}.json written")

#     else:
#         print(f"Failed to download {file_name}")

def download_gzip_and_write_to_json_extracted(file_name, team100ID, team200ID):
  local_file_name = file_name.replace(":", "_")
  if os.path.isfile(f"{local_file_name}.json"):
      return
  
  response = requests.get(f"{S3_BUCKET_URL}/{file_name}.json.gz")

  if response.status_code == 200:
    gzip_bytes = BytesIO(response.content)
    with gzip.GzipFile(fileobj=gzip_bytes, mode="rb") as gzipped_file:
        # Load the JSON data into a list of dictionaries
      data = json.load(gzipped_file)

    # Extract only the desired data
    end_data = data[-2];

    extracted_data = {
        "team100ID": team100ID,
        "team100TotalGold": 0,
        "team100TotalDamage": 0,
        "team200ID": team200ID,
        "team200TotalDamage": 0,
        "team200TotalGold": 0,
    }

    if "gameOver" in end_data and end_data["gameOver"] == True:
        if "teams" in end_data:
            teams = end_data["teams"]
            for team in teams:
                if "teamID" in team and "totalGold" in team and team["teamID"] == 100:
                    extracted_data["team100TotalGold"] = team["totalGold"]
                else:
                    extracted_data["team200TotalGold"] = team["totalGold"]

        if "participants" in end_data:
            participants = end_data["participants"]
            for participant in participants:
                total_damage = 0
                if "stats" in participant:
                    stats = participant["stats"]
                    for stat in stats:
                        if "name" in stat and stat["name"] == "TOTAL_DAMAGE_DEALT_TO_CHAMPIONS":
                            total_damage = stat["value"]

                if "teamID" in participant and participant["teamID"] == 100:
                    extracted_data["team100TotalDamage"] += total_damage
                else:
                    extracted_data["team200TotalDamage"] += total_damage


    extracted_data["team100GoldToDamageRatio"] = extracted_data["team100TotalGold"] / extracted_data["team100TotalDamage"]
    extracted_data["team200GoldToDamageRatio"] = extracted_data["team200TotalGold"] / extracted_data["team200TotalDamage"]


    

    # Save the extracted data to a new JSON file
    with open(f"{local_file_name}_extracted.json", 'w') as output_file:
        json.dump(extracted_data, output_file, indent=2)

    print(f"{file_name}.json written")

  else:
      print(f"Failed to download {file_name}")


def download_esports_files():
    directory = "esports-data"
    if not os.path.exists(directory):
        os.makedirs(directory)

    esports_data_files = ["leagues", "tournaments", "players", "teams", "mapping_data"]
    for file_name in esports_data_files:
        download_gzip_and_write_to_json(f"{directory}/{file_name}")

# def download_games_for_tournament(tournament_slug):
#     start_time = time.time()
#     with open("esports-data/tournaments.json", "r") as json_file:
#         tournaments_data = json.load(json_file)
#     with open("esports-data/mapping_data.json", "r") as json_file:
#         mappings_data = json.load(json_file)

#     directory = "games1"
#     if not os.path.exists(directory):
#         os.makedirs(directory)

#     mappings = {esports_game["esportsGameId"]: esports_game for esports_game in mappings_data}
#     game_counter = 0

#     for tournament in tournaments_data:
#         if tournament["slug"] == tournament_slug:
#             print(f"Processing {tournament['slug']}")
#             for stage in tournament["stages"]:
#                 for section in stage["sections"]:
#                     for match in section["matches"]:
#                         for game in match["games"]:
#                             if game["state"] == "completed":
#                                 try:
#                                     platform_game_id = mappings[game["id"]]["platformGameId"]
#                                 except KeyError:
#                                     print(f"{platform_game_id} {game['id']} not found in the mapping table")
#                                     continue

#                                 download_gzip_and_write_to_json_extracted(f"{directory}/{platform_game_id}")
#                                 game_counter += 1

#                             if game_counter % 10 == 0:
#                                 print(
#                                     f"----- Processed {game_counter} games, current run time: \
#                                     {round((time.time() - start_time)/60, 2)} minutes"
#                                 )

def download_games_for_tournament(tournament_slug):
    start_time = time.time()
    with open("esports-data/tournaments.json", "r") as json_file:
        tournaments_data = json.load(json_file)
    with open("esports-data/mapping_data.json", "r") as json_file:
        mappings_data = json.load(json_file)

    directory = "games"
    if not os.path.exists(directory):
        os.makedirs(directory)

    mappings = {esports_game["esportsGameId"]: esports_game for esports_game in mappings_data}
    game_counter = 0

    for tournament in tournaments_data:
        if tournament["slug"] == tournament_slug:
            print(f"Processing {tournament['slug']}")
            for stage in tournament["stages"]:
                for section in stage["sections"]:
                    for match in section["matches"]:
                        for game in match["games"]:
                            if game["state"] == "completed":
                                try:
                                    platform_game_id = mappings[game["id"]]["platformGameId"]
                                    team100ID = mappings[game["id"]]["teamMapping"]["100"]
                                    team200ID = mappings[game["id"]]["teamMapping"]["200"]
                                except KeyError:
                                    print(f"{platform_game_id} {game['id']} not found in the mapping table")
                                    continue
                                download_gzip_and_write_to_json_extracted(f"{directory}/{platform_game_id}", team100ID, team200ID)
                                game_counter += 1

                            if game_counter % 10 == 0:
                                print(
                                    f"----- Processed {game_counter} games, current run time: \
                                    {round((time.time() - start_time)/60, 2)} minutes"
                                )

if __name__ == "__main__":
    download_esports_files()
    
    # Specify the tournament slug for the desired tournament
    tournament_slug_to_download = "nacl_qualifiers_2_summer_2023"
    
    download_games_for_tournament(tournament_slug_to_download)
