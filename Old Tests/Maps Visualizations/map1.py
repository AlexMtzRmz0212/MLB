import pandas as pd
import folium

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
mlb_map = folium.Map(location=[39.8283, -98.5795], zoom_start=4, tiles="CartoDB positron")

# Add circle markers with custom styling
for _, row in mlb_df.iterrows():
    league_color = league_colors.get(row["League"], "gray")
    division = row["Division"]
    division_color = division_colors.get(division, "gray")

    label = f"<b>{row['Team Name']}</b><br>{row['League']} League - {row['Division']} Division<br>Stadium: {row['Home Stadium']}<br>Established: {row['Founded']}<br>Location: {row['City']}, {row['State']}"

    folium.CircleMarker(
        location=[row["Latitude"], row["Longitude"]],
        radius=5,
        color=league_color,  # Outer ring
        weight=2,            # Thickness of the outer stroke
        fill=True,
        fill_color=division_color,  # Inner fill
        fill_opacity=0.5,
        popup=folium.Popup(label, max_width=300),
        tooltip=row["Team Name"]
    ).add_to(mlb_map)

# Save the map
mlb_map.save("mlb_teams_map.html")
