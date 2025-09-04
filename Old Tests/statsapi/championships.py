import requests
from collections import Counter

#clear the console
import os
os.system('cls' if os.name == 'nt' else 'clear')

def get_world_series_champions(start_year=1903, end_year=2025):
    champions = []

    for year in range(start_year, end_year + 1):
        url = f"https://statsapi.mlb.com/api/v1/schedule/postseason/series?season={year}"
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to retrieve data for {year}")
            continue
        data = response.json()
        series = data.get('series', [])
        for s in series:
            if s.get('seriesName') == 'World Series':
                if s.get('isOver'):
                    winner = s.get('teams', {}).get('winner', {}).get('team', {}).get('name')
                    if winner:
                        champions.append(winner)
                break  # Exit after finding the World Series
    return champions

# Retrieve champions and count the number of championships per team
champions_list = get_world_series_champions()
championship_counts = Counter(champions_list)

# Display the results
print("World Series Championships by Team:")
print(len(champions_list), "championships found.")
for team, count in championship_counts.most_common():
    print(f"{team}: {count} championships")
