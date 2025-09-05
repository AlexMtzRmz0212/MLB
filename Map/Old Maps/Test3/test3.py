# create_map.py
import pandas as pd
import folium


df = pd.read_csv(filepath_or_buffer='stadiums.csv')

# We only want the MLB teams for this map
mlb_df = df[df['Sport'] == 'MLB'].copy()

# Create a dictionary to assign a color to each MLB division
division_colors = {
    'AL East': 'red',
    'AL Central': 'blue',
    'AL West': 'darkblue',
    'NL East': 'green',
    'NL Central': 'purple',
    'NL West': 'orange'
}

# Create the base map, centered on the United States
m = folium.Map(location=[39.8283, -98.5795], zoom_start=4, tiles='CartoDB positron')

# Loop through each MLB team in our data
for index, row in mlb_df.iterrows():
    # Look up the correct color for the team's division
    color = division_colors.get(row['Division'], 'gray') # Use gray as a default
    
    # Create the text that will appear in the popup window
    popup_text = f"<b>{row['Team']}</b><br>{row['Division']}"

    # Add a marker to the map for the current team
    folium.Marker(
        location=[row['Latitude'], row['Longitude']],
        popup=popup_text,
        tooltip=row['Team'], # Shows the team name when you hover over the marker
        icon=folium.Icon(color=color, icon='info-sign') # A simple, generic icon
    ).add_to(m)

# Save the completed map to an HTML file
output_file = 'mlb_divisions_map.html'
m.save(output_file)

print(f"Success! Map has been saved to '{output_file}'")