import pandas as pd
import folium
import os
from math import radians, sin, cos, sqrt, atan2, pi
import numpy as np

# Clear console
os.system('cls' if os.name == 'nt' else 'clear')

# Paths 
DATA_PATH = '../MLB.csv'
OUTPUT_PATH = 'mlb_optimal_map.html'

# Load data
mlb_df = pd.read_csv(DATA_PATH)

# League colors
league_colors = {
    'American': 'red',
    'National': 'blue'
}

MIN_DISTANCE_KM = 20 # the higher, the more spaced out the markers
ITERATIONS = 2 # the higher, the more iterations for separation
DIV_FACTOR = 50 # the lower, the more separation

# Create map
map = folium.Map(location=[38, -97], zoom_start=5, tiles='CartoDB positron')

# Haversine distance calculation
def haversine_distance(p1, p2):
    lat1, lon1 = radians(p1[0]), radians(p1[1])
    lat2, lon2 = radians(p2[0]), radians(p2[1])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    return 6371 * c  # Earth radius in km

# Improved function to calculate offset positions for nearby markers
def calculate_offsets(teams_df, min_distance_km=MIN_DISTANCE_KM):
    """
    Calculate offsets for markers that are too close to each other.
    Returns a dictionary with team names as keys and offset coordinates as values.
    """
    offsets = {}
    team_coords = {}
    
    # Get all team coordinates and initialize offsets
    for _, row in teams_df.iterrows():
        team_coords[row['Team']] = (row['Latitude'], row['Longitude'])
        offsets[row['Team']] = (0, 0)  # Initialize with no offset
    
    # Create list of teams for iteration
    team_names = list(team_coords.keys())
    
    # Multiple iterations for better separation
    for iteration in range(ITERATIONS):  # Run multiple passes for better results
        for i in range(len(team_names)):
            team1 = team_names[i]
            coord1 = team_coords[team1]
            
            for j in range(i+1, len(team_names)):
                team2 = team_names[j]
                coord2 = team_coords[team2]
                    
                distance = haversine_distance(coord1, coord2)
                
                if distance < min_distance_km:
                    # Calculate the direction vector between teams
                    dx = coord2[1] - coord1[1]
                    dy = coord2[0] - coord1[0]
                    
                    # Normalize the direction (avoid division by zero)
                    magnitude = max(sqrt(dx*dx + dy*dy), 0.0001)
                    dx /= magnitude
                    dy /= magnitude
                    
                    # Calculate push force based on how close they are
                    push_force = (min_distance_km - distance) / DIV_FACTOR  # Stronger scaling

                    # Apply push in opposite directions
                    offsets[team1] = (offsets[team1][0] - dy * push_force, 
                                     offsets[team1][1] - dx * push_force)
                    offsets[team2] = (offsets[team2][0] + dy * push_force, 
                                     offsets[team2][1] + dx * push_force)
    
    return offsets

# Calculate offsets for all teams
marker_offsets = calculate_offsets(mlb_df)

# Add team markers with offsets
for _, row in mlb_df.iterrows():
    color = league_colors.get(row['League'], 'gray')
    popup_text = f"<b>{row['Team']}</b><br>{row['Division']}"
    
    # Apply offset if needed
    offset = marker_offsets.get(row['Team'], (0, 0))
    lat = row['Latitude'] + offset[0]
    lon = row['Longitude'] + offset[1]
    
    logo_icon = folium.CustomIcon(
        icon_image=row['LogoURL'],
        icon_size=(30, 30),
        icon_anchor=(15, 15),
        popup_anchor=(0, -15)
    )
    
    folium.Marker(
        location=[lat, lon],
        popup=popup_text,
        tooltip=row['Team'],
        icon=logo_icon
    ).add_to(map)

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

# Create a dictionary for team coordinates with offsets
team_offset_coords = {}
for _, row in mlb_df.iterrows():
    offset = marker_offsets.get(row['Team'], (0, 0))
    team_offset_coords[row['Team']] = (
        row['Latitude'] + offset[0], 
        row['Longitude'] + offset[1]
    )

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
            if team in team_offset_coords:
                path.append(team_offset_coords[team])
            else:
                print(f"Warning: Team '{team}' not found in division '{division}'")
    else:
        # Default case: use the original order from the CSV with offsets
        for _, team in division_teams.iterrows():
            if team['Team'] in team_offset_coords:
                path.append(team_offset_coords[team['Team']])

    # Add path to map only if we have at least 2 points
    if len(path) >= 2:
        folium.PolyLine(locations=path, color=line_color, weight=2.5, opacity=0.8).add_to(map)
    else:
        print(f"Warning: Not enough valid points for division '{division}' to draw a line")

# Save map
map.save(OUTPUT_PATH)
print(f"Success! Map has been saved to '{OUTPUT_PATH}'")