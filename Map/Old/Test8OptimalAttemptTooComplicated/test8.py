import pandas as pd
import folium
import os
import math
import itertools
from math import radians, sin, cos, sqrt, atan2

os.system('cls' if os.name == 'nt' else 'clear')

mlb_df = pd.read_csv(filepath_or_buffer='../MLB.csv')

league_colors = {
    'American': 'red',
    'National': 'blue'
}

# Create the map
m = folium.Map(location=[38, -97], zoom_start=5, tiles='CartoDB positron')

# Store original positions for later use
original_positions = {}
for index, row in mlb_df.iterrows():
    original_positions[row['Team']] = (row['Latitude'], row['Longitude'])

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

# Function to check if markers are overlapping
def are_markers_overlapping(pos1, pos2, threshold=0.1):
    """Check if two positions are too close (overlapping)"""
    return haversine_distance(pos1, pos2) < threshold

# Function to calculate a scattered position
def calculate_scattered_position(base_pos, index, total, radius=0.2):
    """Calculate a position in a circle around the base position"""
    angle = 2 * math.pi * index / total
    dx = radius * math.cos(angle) / 69  # approx degrees latitude per mile
    dy = radius * math.sin(angle) / (69 * math.cos(math.radians(base_pos[0])))  # longitude adjustment
    return (base_pos[0] + dx, base_pos[1] + dy)

# Group teams by their location to find clusters
position_groups = {}
for index, row in mlb_df.iterrows():
    pos = (row['Latitude'], row['Longitude'])
    found_group = False
    
    # Check if this position is close to any existing group
    for group_center in position_groups:
        if are_markers_overlapping(pos, group_center):
            position_groups[group_center].append((index, row))
            found_group = True
            break
    
    # If not close to any existing group, create a new one
    if not found_group:
        position_groups[pos] = [(index, row)]

# Create markers, scattering those in clusters
for group_center, items in position_groups.items():
    if len(items) == 1:
        # Single marker, use original position
        index, row = items[0]
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
        ).add_to(m)
    else:
        # Multiple markers at similar locations, scatter them
        for i, (index, row) in enumerate(items):
            color = league_colors.get(row['League'], 'gray')
            popup_text = f"<b>{row['Team']}</b><br>{row['Division']}"
            
            # Store original position in popup for JavaScript access
            orig_lat, orig_lng = original_positions[row['Team']]
            popup_text += f"<div class='original-position' data-lat='{orig_lat}' data-lng='{orig_lng}' style='display:none;'></div>"
            
            logo_icon = folium.CustomIcon(
                icon_image=row['LogoURL'],
                icon_size=(30, 30),
                icon_anchor=(15, 15),
                popup_anchor=(0, -15)
            )
            
            # Calculate scattered position
            scattered_pos = calculate_scattered_position(group_center, i, len(items))
            
            folium.Marker(
                location=scattered_pos,
                popup=popup_text,
                tooltip=row['Team'],
                icon=logo_icon
            ).add_to(m)

# Add JavaScript to handle zoom behavior
js_code = """
<script>
// Function to check if we're zoomed in enough to show original positions
function shouldUseOriginalPositions() {
    return map.getZoom() >= 10; // Adjust this threshold as needed
}

// Function to update marker positions based on zoom level
function updateMarkerPositions() {
    if (shouldUseOriginalPositions()) {
        // Use original positions
        document.querySelectorAll('.original-position').forEach(function(el) {
            var marker = el.closest('.leaflet-popup');
            if (marker) {
                var lat = parseFloat(el.getAttribute('data-lat'));
                var lng = parseFloat(el.getAttribute('data-lng'));
                var markerInstance = window.markers[marker.id];
                if (markerInstance) {
                    markerInstance.setLatLng([lat, lng]);
                }
            }
        });
    } else {
        // Use scattered positions (already set when markers were created)
        // No action needed as markers are already in scattered positions
    }
}

// Initialize when map is ready
map.whenReady(function() {
    // Store reference to all markers
    window.markers = {};
    document.querySelectorAll('.leaflet-marker-icon').forEach(function(icon) {
        var popup = icon.nextElementSibling;
        if (popup && popup.classList.contains('leaflet-popup')) {
            window.markers[popup.id] = L.popup({autoPan: false}).setContent(popup.querySelector('.leaflet-popup-content-wrapper'));
        }
    });
    
    // Update positions on zoom
    map.on('zoomend', updateMarkerPositions);
    
    // Initial update
    updateMarkerPositions();
});
</script>
"""

# Add the JavaScript to the map
m.get_root().html.add_child(folium.Element(js_code))


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
    
    folium.PolyLine(locations=path, color=line_color, weight=2.5, opacity=0.8).add_to(m)

# Save the map
output_file = 'mlb_optimal_map.html'
m.save(output_file)

print(f"Success! Optimal map has been saved to '{output_file}'")