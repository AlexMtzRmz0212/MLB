import pandas as pd
import folium
import os
from math import radians, sin, cos, sqrt, atan2

# Clear console
os.system('cls' if os.name == 'nt' else 'clear')

# Define your paths here
DATA_PATH = '../MLB.csv'
OUTPUT_PATH = 'mlb_optimal_map.html'

# Load data
mlb_df = pd.read_csv(DATA_PATH)

# League colors
league_colors = {
    'American': 'red',
    'National': 'blue'
}

# Create map
map = folium.Map(location=[38, -97], zoom_start=5, tiles='CartoDB positron')

# Add team markers
for _, row in mlb_df.iterrows():
    color = league_colors.get(row['League'], 'gray')
    popup_text = f"<b>{row['Team']}</b><br>{row['Division']}"
    
    logo_icon = folium.CustomIcon(
        icon_image=row['LogoURL'],
        icon_size=(30, 30),
        icon_anchor=(15, 15),
        popup_anchor=(0, -15)
    )
    
    folium.Marker(
        location=[row['Latitude'], row['Longitude']],
        popup=popup_text,
        tooltip=row['Team'],
        icon=logo_icon
    ).add_to(map)

# Haversine distance calculation
def haversine_distance(p1, p2):
    lat1, lon1 = radians(p1[0]), radians(p1[1])
    lat2, lon2 = radians(p2[0]), radians(p2[1])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    return 6371 * c  # Earth radius in km

# Create division paths
mlb_df['FullDivision'] = mlb_df['League'] + ' ' + mlb_df['Division']

division_orders = {
    "American Central": [
        "Chicago White Sox", 
        "Cleveland Guardians", 
        "Detroit Tigers", 
        "Kansas City Royals", 
        "Minnesota Twins"
    ],
    "American East": [
        "Baltimore Orioles", 
        "Boston Red Sox", 
        "Toronto Blue Jays", 
        "Tampa Bay Rays", 
        "New York Yankees"
    ],
    "American West": [
        "Houston Astros",
        "Los Angeles Angels",
        "Athletics",
        "Seattle Mariners",
        "Texas Rangers"
    ],
    "National Central": [
        "Milwaukee Brewers",
        "Chicago Cubs",
        "Cincinnati Reds",
        "Pittsburgh Pirates",
        "Cincinnati Reds",
        "St. Louis Cardinals"
    ],
    "National East": [
        "Atlanta Braves",
        "Miami Marlins",
        "New York Mets",
        "Philadelphia Phillies",
        "Washington Nationals"
    ],
    "National West": [
        "Arizona Diamondbacks",
        "Colorado Rockies",
        "Los Angeles Dodgers",
        "San Diego Padres",
        "San Francisco Giants"
    ]
}

for division in mlb_df['FullDivision'].unique():
    division_teams = mlb_df[mlb_df['FullDivision'] == division]
    
    if len(division_teams) < 2:
        continue
        
    # Get league color
    league = division_teams['League'].iloc[0]
    line_color = league_colors.get(league, 'black')
    
    # Check if custom order is defined
    custom_order = division_orders.get(division, [])
    path = []
    
    if custom_order:
        # If a custom order is defined, use it but verify teams exist
        for team in custom_order:
            team_data = division_teams[division_teams['Team'] == team]
            if not team_data.empty:
                team_coords = team_data[['Latitude', 'Longitude']].iloc[0]
                path.append((team_coords['Latitude'], team_coords['Longitude']))
            else:
                print(f"Warning: Team '{team}' not found in division '{division}'")
    else:
        # Default case: use the original order from the CSV
        path = list(zip(division_teams['Latitude'], division_teams['Longitude']))

    # Add path to map only if we have at least 2 points
    if len(path) >= 2:
        folium.PolyLine(locations=path, color=line_color, weight=2.5, opacity=0.8).add_to(map)
    else:
        print(f"Warning: Not enough valid points for division '{division}' to draw a line")

# Save map
map.save(OUTPUT_PATH)
print(f"Success! Map has been saved to '{OUTPUT_PATH}'")