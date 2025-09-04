import pandas as pd
import folium
import os

os.system('cls' if os.name == 'nt' else 'clear')

mlb_df = pd.read_csv(filepath_or_buffer='MLB.csv')

## --- CHANGE #1: Color dictionary is now for Leagues ---
league_colors = {
    'American': 'red',
    'National': 'blue'  
}

# Create the base map
map = folium.Map(location=[39.8283, -98.5795], zoom_start=4, tiles='CartoDB positron')

# --- This loop adds the colored MARKERS for each team ---
for index, row in mlb_df.iterrows():
    # Look up the correct color based on the team's LEAGUE
    color = league_colors.get(row['League'], 'gray') # Default to gray

    popup_text = f"<b>{row['Team']}</b><br>{row['Division']}"

    folium.Marker(
        location=[row['Latitude'], row['Longitude']],
        popup=popup_text,
        tooltip=row['Team'],
        icon=folium.Icon(color=color, icon='info-sign')
    ).add_to(map)

## --- CHANGE #2: New section to draw LINES for Divisions ---
# First, get a list of all unique divisions (e.g., 'American Central', 'National East', etc.)
divisions = mlb_df['League'] + ' ' + mlb_df['Division']
divisions = divisions.unique()
mlb_df['FullDivision'] = mlb_df['League'] + ' ' + mlb_df['Division']

# Now, loop through each division to draw the connecting lines
for division in divisions:
    # Get the data for just the teams in the current division
    division_teams = mlb_df[mlb_df['FullDivision'] == division]

    # Get the coordinates for each of those teams
    points = list(zip(division_teams['Latitude'], division_teams['Longitude']))

    # We need at least two points to draw a line
    if len(points) > 1:
        # Get the league for this division to color the line correctly
        league = division_teams['League'].iloc[0]
        line_color = league_colors.get(league, 'black')
        
        # Add the line to the map
        folium.PolyLine(locations=points, color=line_color, weight=2.5, opacity=0.8).add_to(map)

# Save the completed map to an HTML file
output_file = 'mlb_leagues_and_divisions_map.html'
map.save(output_file)

print(f"Success! Map has been saved to '{output_file}'")