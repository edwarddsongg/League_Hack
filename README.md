# region_rank

API Specifications

The API is deployed with the url: https://ded9b05jx7.execute-api.us-east-2.amazonaws.com/test/
	
You can access the endpoints by adding the desired path, e.g
https://ded9b05jx7.execute-api.us-east-2.amazonaws.com/test/global_rankings

For team rankings, you query with the string parameter: “team_id: {team_id}” for example:
https://ded9b05jx7.execute-api.us-east-2.amazonaws.com/test/team_rankings/?team_ids=99566404581868574&team_ids=98767991853197861&team_ids=100205573495116443&team_ids=99566404579461230 

For global_rankings, you query with the string parameter: “number_of_teams:{integer}” for example:
https://ded9b05jx7.execute-api.us-east-2.amazonaws.com/test/global_rankings?number_of_teams=50 

For tournament rankings, you query with the string parameter: “tournament_id: {tournament_id}” and “stage: {stage_name}” for example: https://ded9b05jx7.execute-api.us-east-2.amazonaws.com/test/tournament_rankings/?tournament_id=110733838935136200&stage=knockouts 

