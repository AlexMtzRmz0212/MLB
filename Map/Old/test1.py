import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import requests
from io import BytesIO
from PIL import Image
import sqlite3
from datetime import datetime

# Set up the figure with high DPI for portfolio quality
plt.style.use('seaborn-v0_8-whitegrid')
fig, ax = plt.subplots(1, 1, figsize=(16, 10), dpi=300)

# MLB Team Data with coordinates and connections
mlb_teams_data = {
    'team_name': [
        'Seattle Mariners', 'San Francisco Giants', 'Los Angeles Dodgers', 'San Diego Padres',
        'Arizona Diamondbacks', 'Texas Rangers', 'Miami Marlins', 'Atlanta Braves',
        'Washington Nationals', 'Philadelphia Phillies', 'New York Yankees', 'Boston Red Sox',
        'Minnesota Twins', 'Chicago Cubs', 'Detroit Tigers', 'Cleveland Guardians',
        'Pittsburgh Pirates', 'St. Louis Cardinals', 'Cincinnati Reds', 'Kansas City Royals',
        'Houston Astros', 'Colorado Rockies'
    ],
    'team_abbr': [
        'SEA', 'SF', 'LAD', 'SD', 'ARI', 'TEX', 'MIA', 'ATL', 'WSH', 'PHI', 'NYY', 'BOS',
        'MIN', 'CHC', 'DET', 'CLE', 'PIT', 'STL', 'CIN', 'KC', 'HOU', 'COL'
    ],
    'latitude': [
        47.5912, 37.7786, 34.0739, 32.7073, 33.4457, 32.7511, 25.7781, 33.7352,
        38.8730, 39.9061, 40.8296, 42.3467, 44.9815, 41.9484, 42.3393, 41.4962,
        40.4469, 38.6226, 39.0975, 39.0516, 29.7566, 39.7559
    ],
    'longitude': [
        -122.3321, -122.3893, -118.2400, -117.1566, -112.0667, -97.0829, -80.2197, -84.3900,
        -77.0074, -75.1665, -73.9262, -71.0972, -93.2777, -87.6553, -83.0485, -81.6851,
        -80.0063, -90.1928, -84.5068, -94.4807, -95.3551, -104.9942
    ],
    'division': [
        'AL West', 'NL West', 'NL West', 'NL West', 'NL West', 'AL West', 'NL East', 'NL East',
        'NL East', 'NL East', 'AL East', 'AL East', 'AL Central', 'NL Central', 'AL Central',
        'AL Central', 'NL Central', 'NL Central', 'NL Central', 'AL Central', 'AL West', 'NL West'
    ],
    'league': [
        'AL', 'NL', 'NL', 'NL', 'NL', 'AL', 'NL', 'NL', 'NL', 'NL', 'AL', 'AL',
        'AL', 'NL', 'AL', 'AL', 'NL', 'NL', 'NL', 'AL', 'AL', 'NL'
    ]
}

# Create DataFrame
df_teams = pd.DataFrame(mlb_teams_data)

# Define the network connections based on your description
red_network = [
    ('SEA', 'SF'), ('SF', 'LAD'), ('LAD', 'SD'), ('SD', 'ARI'), ('ARI', 'TEX'),
    ('TEX', 'MIA'), ('MIA', 'ATL'), ('ATL', 'WSH'), ('WSH', 'PHI'), ('PHI', 'NYY'), ('NYY', 'BOS'),
    # Red branches
    ('MIN', 'CHC'),
    ('DET', 'CLE'), ('CLE', 'PIT')
]

blue_network = [
    ('STL', 'CIN'), ('STL', 'KC'), ('STL', 'HOU'),
    ('COL', 'ARI')  # Note: ARI appears in both networks
]

# Create a simple US map using state boundaries (simplified approach)
# For a full implementation, you'd want to use actual shapefiles
def create_us_outline():
    """Create a simplified US map outline"""
    # Simplified US boundary coordinates (you'd typically load this from a shapefile)
    us_bounds = {
        'west': -125, 'east': -66.9, 'south': 20.9, 'north': 49.4
    }
    
    # Create a simple rectangle for the US (in a real implementation, use actual state boundaries)
    from matplotlib.patches import Rectangle
    us_rect = Rectangle((us_bounds['west'], us_bounds['south']), 
                       us_bounds['east'] - us_bounds['west'],
                       us_bounds['north'] - us_bounds['south'],
                       facecolor='#E8F4F8', edgecolor='#B0C4DE', linewidth=0.5)
    ax.add_patch(us_rect)
    
    return us_bounds

# Set up the map
us_bounds = create_us_outline()
ax.set_xlim(us_bounds['west'], us_bounds['east'])
ax.set_ylim(us_bounds['south'], us_bounds['north'])

# Function to draw network connections
def draw_connections(connections, color, label, linewidth=2.5, alpha=0.8):
    """Draw network connections between teams"""
    for i, (team1, team2) in enumerate(connections):
        # Get coordinates for both teams
        team1_data = df_teams[df_teams['team_abbr'] == team1].iloc[0]
        team2_data = df_teams[df_teams['team_abbr'] == team2].iloc[0]
        
        # Draw line
        ax.plot([team1_data['longitude'], team2_data['longitude']],
                [team1_data['latitude'], team2_data['latitude']],
                color=color, linewidth=linewidth, alpha=alpha, 
                zorder=2, label=label if i == 0 else "")

# Draw the networks
draw_connections(red_network, '#DC143C', 'Red Network', linewidth=3)
draw_connections(blue_network, '#4169E1', 'Blue Network', linewidth=3)

# Function to create team markers (simplified - in full implementation you'd use actual logos)
def add_team_markers():
    """Add team markers to the map"""
    colors_by_league = {'AL': '#FF6B6B', 'NL': '#4ECDC4'}
    
    for _, team in df_teams.iterrows():
        # Create a circle marker for each team
        circle = plt.Circle((team['longitude'], team['latitude']), 
                          radius=0.8, 
                          color=colors_by_league[team['league']], 
                          ec='white', linewidth=2, zorder=3)
        ax.add_patch(circle)
        
        # Add team abbreviation
        ax.text(team['longitude'], team['latitude'], team['team_abbr'],
                ha='center', va='center', fontsize=8, fontweight='bold',
                color='white', zorder=4)

# Add team markers
add_team_markers()

# Customize the plot
ax.set_title('MLB Team Network Analysis\nInterconnected Relationships Across Baseball Geography', 
             fontsize=20, fontweight='bold', pad=20)
ax.set_xlabel('Longitude', fontsize=12)
ax.set_ylabel('Latitude', fontsize=12)

# Remove grid for cleaner look
ax.grid(False)
ax.set_facecolor('white')

# Add legend
legend_elements = [
    plt.Line2D([0], [0], color='#DC143C', lw=3, label='Red Network (Main Path)'),
    plt.Line2D([0], [0], color='#4169E1', lw=3, label='Blue Network (Central Hub)'),
    plt.Circle((0, 0), radius=0.1, color='#FF6B6B', label='American League'),
    plt.Circle((0, 0), radius=0.1, color='#4ECDC4', label='National League')
]
ax.legend(handles=legend_elements, loc='lower left', fontsize=10)

# Add analysis insights as text box
analysis_text = """
Key Network Insights:
• Red Network: 14 connections spanning coast-to-coast
• Blue Network: 4 connections forming central hub
• Arizona Diamondbacks: Only team in both networks
• Geographic Coverage: All major US regions represented
"""
ax.text(0.02, 0.98, analysis_text, transform=ax.transAxes, fontsize=10,
        verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

plt.tight_layout()
plt.show()

# SQL Database Component for Portfolio
def create_mlb_database():
    """Create SQLite database with MLB team data for SQL demonstration"""
    
    conn = sqlite3.connect('mlb_network_analysis.db')
    cursor = conn.cursor()
    
    # Create teams table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS teams (
        team_id INTEGER PRIMARY KEY AUTOINCREMENT,
        team_name TEXT NOT NULL,
        team_abbr TEXT UNIQUE NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        division TEXT NOT NULL,
        league TEXT NOT NULL,
        created_date TEXT DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create connections table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS connections (
        connection_id INTEGER PRIMARY KEY AUTOINCREMENT,
        team1_abbr TEXT NOT NULL,
        team2_abbr TEXT NOT NULL,
        network_type TEXT NOT NULL,
        connection_strength INTEGER DEFAULT 1,
        created_date TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (team1_abbr) REFERENCES teams (team_abbr),
        FOREIGN KEY (team2_abbr) REFERENCES teams (team_abbr)
    )
    ''')
    
    # Insert team data
    cursor.executemany('''
    INSERT OR REPLACE INTO teams (team_name, team_abbr, latitude, longitude, division, league)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', [(row['team_name'], row['team_abbr'], row['latitude'], row['longitude'], 
           row['division'], row['league']) for _, row in df_teams.iterrows()])
    
    # Insert connection data
    red_connections = [(t1, t2, 'Red') for t1, t2 in red_network]
    blue_connections = [(t1, t2, 'Blue') for t1, t2 in blue_network]
    all_connections = red_connections + blue_connections
    
    cursor.executemany('''
    INSERT OR REPLACE INTO connections (team1_abbr, team2_abbr, network_type)
    VALUES (?, ?, ?)
    ''', all_connections)
    
    conn.commit()
    
    print("✅ Database created successfully!")
    print(f"📊 Inserted {len(df_teams)} teams and {len(all_connections)} connections")
    
    # Example SQL queries for portfolio demonstration
    print("\n" + "="*50)
    print("SQL ANALYSIS EXAMPLES")
    print("="*50)
    
    # Query 1: Teams by league
    print("\n1. Teams by League:")
    result = cursor.execute('''
    SELECT league, COUNT(*) as team_count
    FROM teams
    GROUP BY league
    ORDER BY team_count DESC
    ''').fetchall()
    for row in result:
        print(f"   {row[0]}: {row[1]} teams")
    
    # Query 2: Network connectivity analysis
    print("\n2. Network Connectivity Analysis:")
    result = cursor.execute('''
    SELECT 
        network_type,
        COUNT(*) as connection_count,
        COUNT(DISTINCT team1_abbr) + COUNT(DISTINCT team2_abbr) as unique_teams
    FROM connections
    GROUP BY network_type
    ''').fetchall()
    for row in result:
        print(f"   {row[0]} Network: {row[1]} connections, ~{row[2]} unique teams")
    
    # Query 3: Most connected teams
    print("\n3. Most Connected Teams:")
    result = cursor.execute('''
    WITH team_connections AS (
        SELECT team1_abbr as team, COUNT(*) as connections FROM connections GROUP BY team1_abbr
        UNION ALL
        SELECT team2_abbr as team, COUNT(*) as connections FROM connections GROUP BY team2_abbr
    )
    SELECT 
        tc.team,
        t.team_name,
        SUM(tc.connections) as total_connections
    FROM team_connections tc
    JOIN teams t ON tc.team = t.team_abbr
    GROUP BY tc.team, t.team_name
    ORDER BY total_connections DESC
    LIMIT 5
    ''').fetchall()
    for i, row in enumerate(result, 1):
        print(f"   {i}. {row[1]} ({row[0]}): {row[2]} connections")
    
    # Query 4: Geographic analysis
    print("\n4. Geographic Spread Analysis:")
    result = cursor.execute('''
    SELECT 
        CASE 
            WHEN longitude < -100 THEN 'West'
            WHEN longitude > -80 THEN 'East'
            ELSE 'Central'
        END as region,
        COUNT(*) as team_count,
        ROUND(AVG(latitude), 2) as avg_latitude,
        ROUND(AVG(longitude), 2) as avg_longitude
    FROM teams
    GROUP BY region
    ORDER BY avg_longitude
    ''').fetchall()
    for row in result:
        print(f"   {row[0]}: {row[1]} teams (Center: {row[2]}°N, {row[3]}°W)")
    
    conn.close()
    return "mlb_network_analysis.db"

# Create the database
db_file = create_mlb_database()

print(f"\n🎯 Project Complete!")
print(f"📈 Visualization: Interactive MLB network map created")
print(f"🗄️  Database: {db_file}")
print(f"💼 Portfolio Ready: Demonstrates data viz, SQL, and network analysis skills")