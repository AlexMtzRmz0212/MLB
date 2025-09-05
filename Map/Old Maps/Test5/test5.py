import pandas as pd
import folium
import os
import math # We need this for the distance calculation

os.system('cls' if os.name == 'nt' else 'clear')

mlb_df = pd.read_csv(filepath_or_buffer='MLB.csv')

league_colors = {
    'American': 'red',
    'National': 'blue'
}

map = folium.Map(location=[39.8283, -98.5795], zoom_start=4, tiles='CartoDB positron')

for index, row in mlb_df.iterrows():
    color = league_colors.get(row['League'], 'gray')
    popup_text = f"<b>{row['Team']}</b><br>{row['Division']}"
    folium.Marker(
        location=[row['Latitude'], row['Longitude']],
        popup=popup_text,
        tooltip=row['Team'],
        icon=folium.Icon(color=color, icon='info-sign')
    ).add_to(map)

## --- CHANGE #3: This section is now updated to find the optimal path ---
# A simple function to calculate the distance between two points
def calculate_distance(p1, p2):
    """Calculates the straight-line distance between two lat/lon points."""
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

# Create the combined division names for grouping
mlb_df['FullDivision'] = mlb_df['League'] + ' ' + mlb_df['Division']
divisions = mlb_df['FullDivision'].unique()

# Loop through each division to draw the connecting lines
for division in divisions:
    division_teams = mlb_df[mlb_df['FullDivision'] == division]
    
    # Get a list of team coordinates to visit
    unvisited_points = list(zip(division_teams['Latitude'], division_teams['Longitude']))
    
    # Don't try to draw a line if there's only one team
    if len(unvisited_points) < 2:
        continue

    # --- Start of the Nearest Neighbor Algorithm ---
    path = []
    current_point = unvisited_points.pop(0) # Start at the first team
    path.append(current_point)

    while unvisited_points:
        # Find the nearest point among the remaining unvisited ones
        next_point = min(unvisited_points, key=lambda point: calculate_distance(current_point, point))
        
        # Add the nearest point to our path
        path.append(next_point)
        # Remove it from the list of points to visit
        unvisited_points.remove(next_point)
        # Move our "current location" to this new point
        current_point = next_point
    # --- End of Algorithm ---
    
    # Get the league color for the line
    league = division_teams['League'].iloc[0]
    line_color = league_colors.get(league, 'black')
    
    # Add the final, ordered line to the map
    folium.PolyLine(locations=path, color=line_color, weight=2.5, opacity=0.8).add_to(map)

# Save the map
output_file = 'mlb_optimal_map.html'
map.save(output_file)

print(f"Success! Optimal map has been saved to '{output_file}'")