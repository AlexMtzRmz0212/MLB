import pandas as pd
import folium
import os
from math import radians, sin, cos, sqrt, atan2
from branca.element import Template, MacroElement

# Clear console
os.system('cls' if os.name == 'nt' else 'clear')

# Define your paths here
DATA_PATH = 'MLB.csv'
OUTPUT_PATH = '../index.html'

# Load data
mlb_df = pd.read_csv(DATA_PATH)

# League colors
league_colors = {
    'American': 'red',
    'National': 'blue'
}

MIN_DISTANCE_KM = 140 # minimum distance in km to avoid overlap
ITERATIONS = 2 # the higher, the more iterations for separation
DIV_FACTOR = 60 # the lower, the more separation

# Define custom separation directions for specific team pairs
# Format: (team1, team2): (angle_in_degrees, relative_strength)
custom_directions = {    
    ("Milwaukee Brewers", "Chicago Cubs"): (150 , 20),
    ("Chicago White Sox", "Chicago Cubs"): (250 , 10),

    # New York teams are diagonal north
    ("New York Yankees", "New York Mets"): (330, 20),
    
    # Los Angeles teams
    ("Los Angeles Dodgers", "Los Angeles Angels"): (90, 20),
    ("Los Angeles Dodgers", "San Diego Padres"): (90, 20),

    # Bay Area teams
    ("San Francisco Giants", "Athletics"): (100, 15),

    ("Baltimore Orioles", "Washington Nationals"): (300, 15)
} 

division_orders = {
    "American Central": [
        "Minnesota Twins",
        "Chicago White Sox",
        "Kansas City Royals",
        "Chicago White Sox",
        "Cleveland Guardians", 
        "Detroit Tigers", 
    ],
    "American East": [
        "Toronto Blue Jays",
        "New York Yankees",
        "Boston Red Sox",
        "New York Yankees",
        "Baltimore Orioles",
        "Tampa Bay Rays"
    ],
    "American West": [
        "Texas Rangers",
        "Houston Astros",
        "Los Angeles Angels",
        "Athletics",
        "Seattle Mariners",
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
        "Miami Marlins",
        "Atlanta Braves",
        "Washington Nationals",
        "New York Mets",
        "Philadelphia Phillies",
    ],
    "National West": [
        "Colorado Rockies",
        "Arizona Diamondbacks",
        "San Diego Padres",
        "Los Angeles Dodgers",
        "San Francisco Giants"
    ]
}


# Create map
map = folium.Map(location=[38, -97], zoom_start=5, tiles='CartoDB positron')

map.fit_bounds([[50 , -100], [30, -100]])
legend_html = """
{% macro html(this, kwargs) %}

<div style="
    position: fixed; 
    bottom: 30px; left: 30px; width: 180px; height: 80px; 
    border:2px solid grey; z-index:9999; font-size:14px;
    background-color: white; opacity: 0.85; padding: 10px;">
<b>Legend</b><br>
<i style="color:red;">&#8212;</i> American League<br>
<i style="color:blue;">&#8212;</i> National League
</div>

{% endmacro %}
"""

legend = MacroElement()
legend._template = Template(legend_html)
map.get_root().add_child(legend)

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
                    # Check if we have a custom direction for this pair
                    custom_key1 = (team1, team2)
                    custom_key2 = (team2, team1)
                    
                    if custom_key1 in custom_directions:
                        angle_degrees, strength_multiplier = custom_directions[custom_key1]
                    elif custom_key2 in custom_directions:
                        angle_degrees, strength_multiplier = custom_directions[custom_key2]
                    else:
                        # Default behavior: push directly away from each other
                        dx = coord2[1] - coord1[1]
                        dy = coord2[0] - coord1[0]
                        
                        # Normalize the direction (avoid division by zero)
                        magnitude = max(sqrt(dx*dx + dy*dy), 0.0001)
                        dx /= magnitude
                        dy /= magnitude
                        
                        # Calculate push force
                        push_force = (min_distance_km - distance) / DIV_FACTOR

                        # Apply push in opposite directions
                        offsets[team1] = (offsets[team1][0] - dy * push_force, 
                                         offsets[team1][1] - dx * push_force)
                        offsets[team2] = (offsets[team2][0] + dy * push_force, 
                                         offsets[team2][1] + dx * push_force)
                        continue
                    
                    # Use custom direction
                    angle_radians = radians(angle_degrees)
                    
                    # Calculate push force with custom strength
                    push_force = (min_distance_km - distance) / 20 * strength_multiplier
                    
                    # Convert to degrees (approx 111 km per degree)
                    lat_offset = push_force * cos(angle_radians) / 111
                    lon_offset = push_force * sin(angle_radians) / (111 * cos(radians(coord1[0])))
                    
                    # Apply custom offset (team1 gets the defined direction, team2 gets opposite)
                    offsets[team1] = (offsets[team1][0] + lat_offset, 
                                     offsets[team1][1] + lon_offset)
                    offsets[team2] = (offsets[team2][0] - lat_offset, 
                                     offsets[team2][1] - lon_offset)
    
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
    
    folium.CircleMarker(
        location=[row['Latitude'], row['Longitude']],
        radius=3,
        color='black',
        fill=True,
        fillColor='black',
        fillOpacity=0.8,
        weight=1,
        tooltip=f"Original location: {row['Team']}"
    ).add_to(map)

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

###################### IDEA: change the opacity of divisions ######################
# legend_items = []
# for division, teams in division_orders.items():
#     league = division.split()[0]
#     color = league_colors.get(league, "black")
#     legend_items.append(f'<i style="color:{color};">&#8212;</i> {division}')

# legend_html = f"""
# {{% macro html(this, kwargs) %}}

# <div style="
#     position: fixed; 
#     bottom: 30px; left: 30px; width: 230px; max-height: 250px; overflow-y:auto;
#     border:2px solid grey; z-index:9999; font-size:13px;
#     background-color: white; opacity: 0.85; padding: 10px;">
# <b>Divisions</b><br>
# {'<br>'.join(legend_items)}
# </div>

# {{% endmacro %}}
# """

# legend = MacroElement()
# legend._template = Template(legend_html)
# map.get_root().add_child(legend)



# Save map
map.save(OUTPUT_PATH)
print(f"Success! Map has been saved to '{OUTPUT_PATH}'")
print("Custom separations applied for:")
for pair, (angle, strength) in custom_directions.items():
    print(f"  {pair[0]} ↔ {pair[1]}: {angle}° direction, {strength}x strength")