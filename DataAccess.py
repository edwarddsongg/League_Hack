# WE ARE FNINSHED DOWNLOADING UP TO vcs_spring_2023 !!!!!!!


import requests
import json
import gzip
import shutil
import time
import os
from io import BytesIO

S3_BUCKET_URL = "https://power-rankings-dataset-gprhack.s3.us-west-2.amazonaws.com"


def download_esports_data(file_name):
    local_file_name = file_name.replace(":", "_")
    # If file already exists locally do not re-download game
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


def calculate_damage_and_level(stats_update_event_obj):
    team1_TD, team1_TL, team2_TD, team2_TL = 0, 0, 0, 0
    for participant in stats_update_event_obj["participants"]:
        stats = participant["stats"]
        total_damage = 0

        for stat in stats:
            if "name" in stat and stat["name"] == "TOTAL_DAMAGE_DEALT_TO_CHAMPIONS":
                total_damage = stat["value"]
                break

        if participant["teamID"] == 100:
            team1_TD += total_damage
            team1_TL += participant["level"]
        else:
            team2_TD += total_damage
            team2_TL += participant["level"]

    return (team1_TD, team2_TD, team1_TL, team2_TL)


def updateDamageAndLevel(data_to_load, stats_string, team1_TD, team2_TD, team1_TL, team2_TL):
    for team in data_to_load[stats_string]:
        if team["teamID"] == 100:
            team["totalDamage"] = team1_TD
            team["totalLevel"] = team1_TL
        else:
            team["totalDamage"] = team2_TD
            team["totalLevel"] = team2_TL



def download_game_data(file_name):
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
            midgame_stats = {}
            ninety_stats = {}

            total_length_of_game = data[-1]["gameTime"]
            halfway_game_time = total_length_of_game / 2
            total_number_of_events = len(data)
            halfway_start_index = round(total_number_of_events * 0.4)

            ninety_percent_game_time = total_length_of_game/ 10 * 9
            ninety_start_index = round(total_number_of_events * 0.8)

            # loop from around 40% point of events until midpoint stats_update is found
            for i in range(halfway_start_index, total_number_of_events):
                if data[i]["eventType"] == "stats_update" and (halfway_game_time - 1000) <= data[i]["gameTime"] <= (
                        halfway_game_time + 1000):
                    midgame_stats = data[i]
                    break

            for i in range(ninety_start_index, total_number_of_events):
                if data[i]["eventType"] == "stats_update" and (ninety_percent_game_time - 1000) <= data[i]["gameTime"] <= (ninety_percent_game_time + 1000):
                    ninety_stats = data[i]
                    break

            # TD = total damage, TL = total level
            (midgame_team1_TD, midgame_team2_TD, midgame_team1_TL, midgame_team2_TL) = calculate_damage_and_level(midgame_stats)
            (endgame_team1_TD, endgame_team2_TD, endgame_team1_TL, endgame_team2_TL) = calculate_damage_and_level(end_stats)
            (ninety_team1_TD, ninety_team2_TD, ninety_team1_TL, ninety_team2_TL) = calculate_damage_and_level(ninety_stats)

            # TD = total damage, TL = total level

            data_to_load["end_stats"] = data[-2]["teams"]
            data_to_load["midgame_stats"] = midgame_stats["teams"]
            data_to_load["ninety_stats"] = ninety_stats["teams"]

            updateDamageAndLevel(data_to_load, "midgame_stats", midgame_team1_TD, midgame_team2_TD, midgame_team1_TL, midgame_team2_TL)
            updateDamageAndLevel(data_to_load, "end_stats", endgame_team1_TD, endgame_team2_TD, endgame_team1_TL, endgame_team2_TL)
            updateDamageAndLevel(data_to_load, "ninety_stats", ninety_team1_TD, ninety_team2_TD, ninety_team1_TL, ninety_team2_TL)


            data_to_load["game_end"] = data[-1]

            with open(f"{local_file_name}.json", 'w') as output_file:
                json.dump(data_to_load, output_file, indent=4)

    else:
        print(f"Failed to download {file_name}")


def download_esports_files():
    directory = "esports-data"
    if not os.path.exists(directory):
        os.makedirs(directory)

    esports_data_files = ["leagues", "tournaments", "players", "teams", "mapping_data"]
    for file_name in esports_data_files:
        download_esports_data(f"{directory}/{file_name}")


def download_games(year):
    start_time = time.time()
    with open("esports-data/tournaments.json", "r") as json_file:
        tournaments_data = json.load(json_file)
    with open("esports-data/mapping_data.json", "r") as json_file:
        mappings_data = json.load(json_file)

    directory = "games"
    if not os.path.exists(directory):
        os.makedirs(directory)

    mappings = {
        esports_game["esportsGameId"]: esports_game for esports_game in mappings_data
    }

    game_counter = 0
    already_downloaded = True
    for tournament in tournaments_data:

        start_date = tournament.get("startDate", "")
        if start_date.startswith(str(year)):
            if tournament['slug'] != "lck_summer_2023":
                continue
            print(f"Processing {tournament['slug']}")
            # if already_downloaded:
            #     continue
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

                                download_game_data(f"{directory}/{platform_game_id}")
                                game_counter += 1

                            if game_counter % 10 == 0:
                                print(
                                    f"----- Processed {game_counter} games, current run time: \
                                   {round((time.time() - start_time) / 60, 2)} minutes"
                                )
            print(game_counter)


if __name__ == "__main__":
    download_esports_files()
    download_games(2023)
