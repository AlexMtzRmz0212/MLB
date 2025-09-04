# https://statsapi.mlb.com/api/v1/schedule?sportId=1
# &teamId=141
# &startDate=2025-03-18
# &endDate=2025-07-22
# &gameType=R
# &hydrate=teams.leagueRecord
# https://statsapi.mlb.com/api/v1/schedule?sportId=1&teamId=141&startDate=2025-03-18&endDate=2025-09-28&gameType=R

import pandas as pd
import requests
import os
os.system('cls' if os.name == 'nt' else 'clear')

def get_season_dates(season):
    url = f"https://statsapi.mlb.com/api/v1/seasons?sportId=1&season={season}"
    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to fetch season data")
        return None, None
    data = response.json()
    regularSeasonStartDate = data['seasons'][0]['regularSeasonStartDate']
    regularSeasonEndDate = data['seasons'][0]['regularSeasonEndDate']
    return regularSeasonStartDate, regularSeasonEndDate

def get_team_id(team_name):
    url = "https://statsapi.mlb.com/api/v1/teams"
    response = requests.get(url)
    data = response.json()
    teams = data.get("teams", [])
    
    for team in teams:
        if team["name"].lower() == team_name.lower():
            return team["id"]
    return None

def get_team_wins_losses(team_id, startDate, today):
    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&teamId={team_id}&startDate={startDate}&endDate={today}&gameType=R"
    response = requests.get(url)
    # retrieve when and if the team won or lost in a list of tuples
    if response.status_code != 200:
        print("Failed to fetch team data")
        return None
    data = response.json()
    games = data.get("dates", [])
    results = []
    for game in games:
        for matchup in game.get("games", []):
            # Determine if the team is home or away in this matchup
            away = matchup["teams"]["away"]["team"]["id"]
            home = matchup["teams"]["home"]["team"]["id"]
            if team_id == home or team_id == away:
                team_side = "home" if team_id == home else "away"
                team_info = matchup["teams"][team_side]
                opponent_side = "away" if team_side == "home" else "home"
                opponent_info = matchup["teams"][opponent_side]
                # Only consider completed games
                if matchup["status"]["detailedState"].lower() == "final":
                    is_win = team_info.get("isWinner", False)
                    results.append((
                        matchup.get("officialDate", matchup.get("gameDate", game.get("date"))),
                        is_win,
                        team_info["score"],
                        opponent_info["score"]
                    ))
    return results

today = pd.Timestamp.now().date()
season = today.year
startDate, endDate = get_season_dates(season)
if startDate and endDate:
    print(f"Season {season} starts on {startDate} and ends on {endDate}. Today's date is {today}.")

team = "Toronto Blue Jays" 
team_id = get_team_id(team)
print(f"Team ID for {team}: {team_id}")

if team_id:
    results = get_team_wins_losses(team_id, startDate, today)
    if results:
        df = pd.DataFrame(results, columns=["Date", "Win", "Team Score", "Opponent Score"])
        df["Win"] = df["Win"].apply(lambda x: "W" if x else "L")
        # print(df)
        df.to_csv(f"./Current Season/{team.replace(' ', '_')}_season_results.csv", index=False)
        print(f"Season results for {team} saved to {team.replace(' ', '_')}_season_results.csv")
    else:
        print("No results found for the team.")