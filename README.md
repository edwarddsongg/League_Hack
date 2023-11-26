Global Power Rankings Hackathon

# API Specifications

The API is deployed with the url: ** https://ded9b05jx7.execute-api.us-east-2.amazonaws.com/test/**
	
You can view the global rankings for all teams with their respective ids by 
```
curl https://ded9b05jx7.execute-api.us-east-2.amazonaws.com/test/global_
rankings
```

For team rankings, you query with the string parameter: ```“team_id: {team_id}”``` for example:
```
curl https://ded9b05jx7.execute-api.us-east-2.amazonaws.com/test/team_rankings/?team_ids=99566404581868574&team_ids=98767991853197861&team_ids=100205573495116443&team_ids=99566404579461230 
```

For global_rankings, you query with the string parameter: ```“number_of_teams:{integer}”``` for example:
```curl https://ded9b05jx7.execute-api.us-east-2.amazonaws.com/test/global_rankings?number_of_teams=50```

For tournament rankings, you query with the string parameter: ```“tournament_id: {tournament_id}”``` and ```“stage: {stage_name}”``` 

for example: ``` curl https://ded9b05jx7.execute-api.us-east-2.amazonaws.com/test/tournament_rankings/?tournament_id=110733838935136200&stage=knockouts ```

