import json
import os

def process_game_file(file_name, team_to_ratio_arr):
    # local_file_name = file_name.replace(":", "_")
    
    with open(f"games/{file_name}", 'r') as json_file:
    # with open(f"{local_file_name}_extracted.json", 'r') as json_file:
        data = json.load(json_file)

    team100_ratio = data.get("team100GoldToDamageRatio", 0)
    team200_ratio = data.get("team200GoldToDamageRatio", 0)
    team100_ID = data.get("team100ID", 0)
    team200_ID = data.get("team200ID", 0)

    if team100_ID in team_to_ratio_arr:
        team_to_ratio_arr[team100_ID].append(team100_ratio)
    else:
        team_to_ratio_arr[team100_ID] = [team100_ratio]

    if team200_ID in team_to_ratio_arr:
        team_to_ratio_arr[team200_ID].append(team200_ratio)
    else:
        team_to_ratio_arr[team200_ID] = [team200_ratio]


def calculate_average_ratio(df, team):
    team_df = df[df["team"] == team]
    return team_df["ratio"].mean() if not team_df.empty else 0

def main():
    directory = "games"
    team_to_ratio_arr = {}
    team_to_avg_ratio = {}

    for file_name in os.listdir(directory):
        if file_name.endswith("_extracted.json"):
            process_game_file(file_name, team_to_ratio_arr)

    # Calculate average ratios for each team
    for teamID in team_to_ratio_arr:
        ratios = team_to_ratio_arr[teamID]
        avg_ratio = sum(ratios) / len(ratios)
        team_to_avg_ratio[teamID] = avg_ratio

    # Sort the dictionary by values in ascending order
    sorted_by_ratio = dict(sorted(team_to_avg_ratio.items(), key=lambda item: item[1]))

    with open("result.json", 'w') as json_file:
        json.dump(sorted_by_ratio, json_file, indent=2)

    # sorted_teams = sorted(average_ratios.items(), key=lambda x: x[1])

    # print("Sorted Teams and Average Ratios:")
    # for team, ratio in sorted_teams:
    #     print(f"{team}: {ratio}")

if __name__ == "__main__":
    main()
