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
    # If file already exists locally do not re-download game
    if os.path.isfile(f"{local_file_name}.json"):
        return

    response = requests.get(f"{S3_BUCKET_URL}/{file_name}.json.gz")

    if response.status_code == 200:
        # try:
        gzip_bytes = BytesIO(response.content)
        with gzip.GzipFile(fileobj=gzip_bytes, mode="rb") as gzipped_file:
            # Load the JSON data into a list of dictionaries
            data = json.load(gzipped_file)
            first_kill_found, first_turret_found = False, False
            data_to_load = dict()

            for entry in data:
                if entry["eventType"] == "champion_kill" and not first_kill_found:
                    data_to_load["champion_kill"] = entry
                    first_kill_found = True
                if entry["eventType"] == "building_destroyed" and not first_turret_found:
                    data_to_load["building_destroyed"] = entry
                    first_turret_found = True
                if first_kill_found and first_turret_found:
                    break

            end_stats = data[-2]

            team1_TD, team2_TD, team1_TL, team2_TL = 0, 0, 0, 0

            for participant in end_stats["participants"]:
                if participant["teamID"] == 100:
                    if participant["stats"][34]["name"] != "TOTAL_DAMAGE_DEALT":
                        print("GETTING THE WRONG VALUE FOR TOTAL DAMANGE DEALT")
                    team1_TD += participant["stats"][34]["value"]
                    team1_TL += participant["level"]
                else:
                    if participant["stats"][34]["name"] != "TOTAL_DAMAGE_DEALT":
                        print("GETTING THE WRONG VALUE FOR TOTAL DAMANGE DEALT")
                    team2_TD += participant["stats"][34]["value"]
                    team2_TL += participant["level"]

            data_to_load["end_stats"] = data[-2]["teams"]
            for team in data_to_load["end_stats"]:
                if team["teamID"] == 100:
                    team["totalDamage"] = team1_TD
                    team["totalLevel"] = team1_TL
                else:
                    team["totalDamage"] = team2_TD
                    team["totalLevel"] = team2_TL

            data_to_load["game_end"] = data[-1]

            with open(f"{local_file_name}.json", 'w') as output_file:
                json.dump(data_to_load, output_file, indent=4)

        # except Exception as e:
        #     print("Error:", e)
    else:
        print(f"Failed to download {file_name}")


def download_games(year):
    start_time = time.time()
    with open("Data/tournaments.json", "r") as json_file:
        tournaments_data = json.load(json_file)
    with open("Data/mapping_data.json", "r") as json_file:
        mappings_data = json.load(json_file)

    directory = "games"
    if not os.path.exists(directory):
        os.makedirs(directory)

    mappings = {
        esports_game["esportsGameId"]: esports_game for esports_game in mappings_data
    }

    game_counter = 0

    for tournament in tournaments_data:
        start_date = tournament.get("startDate", "")
        if start_date.startswith(str(year)):

            # if "msi" not in tournament['slug'] and "worlds" not in tournament['slug']:
            #     continue

            print(f"Processing {tournament['slug']}")
            for stage in tournament["stages"]:
                for section in stage["sections"]:
                    for match in section["matches"]:
                        for game in match["games"]:
                            if game["state"] == "completed":
                                # try:
                                #     platform_game_id = mappings[game["id"]]["platformGameId"]
                                # except KeyError:
                                #     print(f"{platform_game_id} {game['id']} not found in the mapping table")
                                #     continue
                                #
                                # download_gzip_and_write_to_json(f"{directory}/{platform_game_id}")
                                game_counter += 1

                            # if game_counter % 10 == 0:
                            #     print(
                            #         f"----- Processed {game_counter} games, current run time: \
                            #        {round((time.time() - start_time) / 60, 2)} minutes"
                            #     )
            print(game_counter)



if __name__ == "__main__":
    download_games(2023)
