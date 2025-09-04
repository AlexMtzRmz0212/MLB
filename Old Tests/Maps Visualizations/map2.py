import pandas as pd
import folium
from folium import Map, FitBounds
from folium.plugins import MarkerCluster
import requests

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
    "West": "pink"
}

# Create base map
map = folium.Map(location=[39.8283, -98.5795], zoom_start=4, tiles="CartoDB positron", max_bounds=True)
# map = folium.Map(tiles="CartoDB positron")

# Add marker cluster to handle overlaps
clusters = MarkerCluster().add_to(map)

# Add team markers with visual cues
for _, row in mlb_df.iterrows():
    league_color = league_colors.get(row["League"], "gray")
    division = row["Division"]
    division_color = division_colors.get(division.split()[-1], "gray")

    label = f"<b>{row['Team Name']}</b><br>{row['League']} League - {row['Division']} Division<br>Stadium: {row['Home Stadium']}<br>Established: {row['Founded']}<br>Location: {row['City']}, {row['State']}"

    # Main circle marker (outer color = league, inner fill = division)
    folium.CircleMarker(
        location=[row["Latitude"], row["Longitude"]],
        radius=8,
        color=league_color,
        weight=3,
        fill=True,
        fill_color=division_color,
        fill_opacity=0.9,
        popup=folium.Popup(label, max_width=300),
        tooltip=row["Team Name"]
    ).add_to(clusters)

    # # Add permanent text label next to marker
    # folium.map.Marker(
    #     [row["Latitude"] + 0.25, row["Longitude"]],  # Slight offset so text doesn't overlap
    #     icon=folium.DivIcon(html=f"""<div style="font-size:10px;font-weight:bold;">{row['Team Name']}</div>""")
    # ).add_to(clusters)

bounds = [[row["Latitude"], row["Longitude"]] for _, row in mlb_df.iterrows()]
map.fit_bounds(bounds)

# Add US state borders using GeoJSON
us_states_url = "https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/us-states.json"
us_states = requests.get(us_states_url).json()

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

# Custom legend (manual HTML overlay)
legend_html = f"""
<div style="position: fixed; bottom: 30px; left: 30px; width: 100px; height: 200px;
    background-color: white; border:2px solid grey; z-index:9999; font-size:14px;
    padding: 10px;">
<b>Legend</b><br>
<u>League:</u><br> 
<span style="color:{league_colors['American']};">●</span> American<br>
<span style="color:{league_colors['National']};">●</span> National<br><br>
<u>Division:</u><br>
<span style="color:{division_colors['East']};">●</span> East<br>
<span style="color:{division_colors['Central']};">●</span> Central<br>
<span style="color:{division_colors['West']};">●</span> West<br>
</div>
"""

map.get_root().html.add_child(folium.Element(legend_html))

# Save the map
map.save("mlb_teams_map.html")
