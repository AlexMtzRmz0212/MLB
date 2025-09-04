import pandas as pd
import folium
from folium.plugins import MarkerCluster

# clear terminal
import os
os.system('cls' if os.name == 'nt' else 'clear')

# Load MLB data
mlb_df = pd.read_csv("mlb_teams_with_coords.csv")

# Define color maps
league_colors = {
    "American": "red",
    "National": "blue"
}

division_colors = {
    "East": "green",
    "Central": "orange",
    "West": "purple"
}

# Create base map
map = folium.Map(location=[39.8283, -98.5795], zoom_start=4, tiles="CartoDB positron")

clusters = MarkerCluster().add_to(map)

import requests

# Get GeoJSON of US states
us_states_url = "https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/us-states.json"
us_states = requests.get(us_states_url).json()

# Add borders to map
folium.GeoJson(
    us_states,
    name="State Borders",
    style_function=lambda x: {
        "fillColor": "transparent",
        "color": "black",
        "weight": 0.2,
        "dashArray": "5, 5"
    }
).add_to(map)


# Add circle markers with custom styling
for _, row in mlb_df.iterrows():
    league_color = league_colors.get(row["League"], "gray")
    division = row["Division"]
    division_color = division_colors.get(division, "gray")

    label = f"<b>{row['Team Name']}</b><br>{row['League']} League - {row['Division']} Division<br>Stadium: {row['Home Stadium']}<br>Established: {row['Founded']}<br>Location: {row['City']}, {row['State']}"

    # folium.map.Marker(
    #     [row["Latitude"] + 0.5, row["Longitude"]],
    #     icon=folium.DivIcon(html=f"""
    #         <div style="font-size:10px; font-weight:bold;">
    #             {row['Team Name']}
    #         </div>
    #     """)
    # ).add_to(map)

    folium.CircleMarker(
        location=[row["Latitude"], row["Longitude"]],
        radius=5,
        color=league_color,  # Outer ring
        weight=2,            # Thickness of the outer stroke
        fill=True,
        fill_color=division_color,  # Inner fill
        fill_opacity=0.5,
        popup=folium.Popup(label, max_width=300),
        tooltip=label
    ).add_to(map)


# Save the map
map.save("mlb_teams_map.html")
print("Map saved")
