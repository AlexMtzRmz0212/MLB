import pandas as pd
import folium
import os
# import math
import itertools
from math import radians, sin, cos, sqrt, atan2

os.system('cls' if os.name == 'nt' else 'clear')

mlb_df = pd.read_csv(filepath_or_buffer='MLB.csv')

league_colors = {
    'American': 'red',
    'National': 'blue'
}

map = folium.Map(location=[38, -97], zoom_start=5, tiles='CartoDB positron')

for index, row in mlb_df.iterrows():
    color = league_colors.get(row['League'], 'gray')
    popup_text = f"<b>{row['Team']}</b><br>{row['Division']}"
    
    # Create custom icon with team logo
    logo_icon = folium.CustomIcon(
        icon_image=row['LogoURL'],  # Assuming your CSV has a column with logo URLs
        icon_size=(30, 30),  # Adjust size as needed
        icon_anchor=(15, 15),  # Anchor point for the icon
        popup_anchor=(0, -15)  # Where popup appears relative to icon
    )
    
    folium.Marker(
        location=[row['Latitude'], row['Longitude']],
        popup=popup_text,
        tooltip=row['Team'],
        icon=logo_icon  # Use the custom icon instead of standard icon
    ).add_to(map)

def haversine_distance(p1, p2):
    """Calculate the great-circle distance between two points using Haversine formula."""
    lat1, lon1 = radians(p1[0]), radians(p1[1])
    lat2, lon2 = radians(p2[0]), radians(p2[1])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    return 6371 * c  # Earth radius in km

def total_path_distance(path):
    """Calculates total distance of a path."""
    return sum(haversine_distance(path[i], path[i+1]) for i in range(len(path)-1))

def brute_force_tsp(points):
    """Finds the optimal path using brute force (only for small sets)."""
    if len(points) <= 1:
        return points
    
    if len(points) > 8:  # Too computationally expensive
        return nearest_neighbor_tsp(points)
    
    shortest_path = None
    shortest_distance = float('inf')
    
    for permutation in itertools.permutations(points[1:]):
        current_path = [points[0]] + list(permutation)
        total_distance = total_path_distance(current_path)
        
        if total_distance < shortest_distance:
            shortest_distance = total_distance
            shortest_path = current_path
    
    return shortest_path

def nearest_neighbor_tsp(points):
    """Nearest neighbor algorithm for larger sets."""
    if len(points) <= 1:
        return points
    
    unvisited = points.copy()
    path = [unvisited.pop(0)]
    
    while unvisited:
        current = path[-1]
        next_point = min(unvisited, key=lambda point: haversine_distance(current, point))
        path.append(next_point)
        unvisited.remove(next_point)
    
    return path

def two_opt_improvement(path):
    """Improves a path using the 2-opt algorithm."""
    improved = True
    best_path = path.copy()
    best_distance = total_path_distance(path)
    
    while improved:
        improved = False
        for i in range(1, len(path) - 2):
            for j in range(i + 1, len(path)):
                if j - i == 1:
                    continue
                
                new_path = best_path[:i] + best_path[i:j][::-1] + best_path[j:]
                new_distance = total_path_distance(new_path)
                
                if new_distance < best_distance:
                    best_path = new_path
                    best_distance = new_distance
                    improved = True
                    break
            if improved:
                break
    
    return best_path

# Create the combined division names for grouping
mlb_df['FullDivision'] = mlb_df['League'] + ' ' + mlb_df['Division']
divisions = mlb_df['FullDivision'].unique()

for division in divisions:
    division_teams = mlb_df[mlb_df['FullDivision'] == division]
    unvisited_points = list(zip(division_teams['Latitude'], division_teams['Longitude']))
    
    if len(unvisited_points) < 2:
        continue

    # Get optimal path
    if len(unvisited_points) <= 8:
        path = brute_force_tsp(unvisited_points)
    else:
        initial_path = nearest_neighbor_tsp(unvisited_points)
        path = two_opt_improvement(initial_path)
    
    league = division_teams['League'].iloc[0]
    line_color = league_colors.get(league, 'black')
    
    folium.PolyLine(locations=path, color=line_color, weight=2.5, opacity=0.8).add_to(map)

# Save the map
output_file = 'mlb_optimal_map.html'
map.save(output_file)

print(f"Success! Optimal map has been saved to '{output_file}'")