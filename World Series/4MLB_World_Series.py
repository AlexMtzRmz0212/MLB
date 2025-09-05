# with stats.api create this table: 
# Team, Wins, Losses, Appearances, Win Percentage, 
# Years Since Last Championship, championships/yearsActive, Seasons(bolding winning)

import os
import pandas as pd

os.system('cls' if os.name == 'nt' else 'clear')

franchise_map = {
    "Anaheim Angels": "California / Anaheim / Los Angeles Angels",
    "Arizona Diamondbacks": "Arizona Diamondbacks",
    "Atlanta Braves": "Boston / Milwaukee / Atlanta Braves",
    "Baltimore Orioles": "Milwaukee Brewers / St. Louis Browns / Baltimore Orioles",
    "Boston Americans": "Boston Americans / Red Sox",
    "Boston Braves": "Boston / Milwaukee / Atlanta Braves",
    "Boston Red Sox": "Boston Americans / Red Sox",
    "Brooklyn Dodgers": "Brooklyn / Los Angeles Dodgers",
    "Chicago Cubs": "Chicago Cubs",
    "Chicago White Sox": "Chicago White Sox",
    "Cincinnati Reds": "Cincinnati Reds",
    "Cleveland Indians": "Cleveland Indians / Guardians",
    "Detroit Tigers": "Detroit Tigers",
    "Florida Marlins": "Florida / Miami Marlins",
    "Houston Astros": "Houston Colt .45s / Astros",
    "Kansas City Royals": "Kansas City Royals",
    "Los Angeles Dodgers": "Brooklyn / Los Angeles Dodgers",
    "Milwaukee Braves": "Boston / Milwaukee / Atlanta Braves",
    "Minnesota Twins": "Washington Senators / Minnesota Twins",
    "New York Giants": "New York / San Francisco Giants",
    "New York Mets": "New York Mets",
    "New York Yankees": "New York Yankees",
    "Oakland Athletics": "Philadelphia / Kansas City / Oakland / Athletics",
    "Philadelphia Athletics": "Philadelphia / Kansas City / Oakland / Athletics",
    "Philadelphia Phillies": "Philadelphia Phillies",
    "Pittsburgh Pirates": "Pittsburgh Pirates",
    "San Francisco Giants": "New York / San Francisco Giants",
    "St. Louis Cardinals": "St. Louis Cardinals",
    "Texas Rangers": "Washington Senators / Texas Rangers",
    "Toronto Blue Jays": "Toronto Blue Jays",
    "Washington Nationals": "Montreal Expos / Washington Nationals",
    "Washington Senators": "Washington Senators / Minnesota Twins", 
}

df = pd.read_csv('Champs/MLB_Champs.csv')

df = df[~df['Team'].isin(['No Champion', 'No Champion yet'])]

df['Team'] = df['Team'].replace(franchise_map)


team_champ_count = df.groupby('Team')['Year'].agg(['count', lambda x: sorted(x.tolist())])
team_champ_count.columns = ['Championships', 'Years']

team_champ_count.reset_index(inplace=True)
team_champ_count.index = team_champ_count.index + 1

print("Championships Count by Team:")
print(team_champ_count)

