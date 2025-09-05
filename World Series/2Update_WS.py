import requests
from datetime import date
import os
os.system('cls' if os.name == 'nt' else 'clear')

def get_world_series_winners(start_year=1903, end_year=date.today().year):
    winners = {}
    for year in range(start_year, end_year + 1):
        url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&season={year}&gameTypes=W"
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to fetch data for {year}")
            winners[year] = "Data not available"
            continue
        data = response.json()
        dates = data.get("dates", [])
        if not dates:
            if year == end_year:
                winners[year] = "No World Series yet"
            else:
                winners[year] = "No World Series"
            continue
        # Get the last game of the World Series
        last_game = dates[-1]["games"][-1]
        winner = last_game.get(
            "teams", {}).get(
                "away", {}).get(
                    "team", {}).get(
                        "name") if last_game.get(
                            "teams", {}).get(
                                "away", {}).get(
                                    "isWinner") else last_game.get(
                                        "teams", {}).get(
                                            "home", {}).get(
                                                "team", {}).get(
                                                    "name")
        winners[year] = winner
    return winners

def get_world_series_losers():
    winners = get_world_series_winners()
    losers = {}
    for year, winner in winners.items():
        if winner == "No World Series yet" or winner == "No World Series":
            losers[year] = winner
        else:
            url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&season={year}&gameTypes=W"
            response = requests.get(url)
            data = response.json()
            dates = data.get("dates", [])
            if not dates:
                losers[year] = "Data not available"
                continue
            last_game = dates[-1]["games"][-1]
            loser = last_game.get(
                "teams", {}).get(
                    "away", {}).get(
                        "team", {}).get(
                            "name") if last_game.get(
                                "teams", {}).get(
                                    "away", {}).get(
                                        "isWinner") else last_game.get(
                                            "teams", {}).get(
                                                "home", {}).get(
                                                    "team", {}).get(
                                                        "name")
            losers[year] = loser
    return losers


world_series_winners = get_world_series_winners()
world_series_losers = get_world_series_losers()

# save the results to a csv file
def save_to_csv(data, filename):
    with open(filename, "w") as file:
        file.write("Year,Team\n")
        for year, team in data.items():
            file.write(f"{year},{team}\n")

save_to_csv(world_series_winners, "2WS/MLB_Champs.csv")
save_to_csv(world_series_losers, "2WS/MLB_Losers.csv")
print("Done")
