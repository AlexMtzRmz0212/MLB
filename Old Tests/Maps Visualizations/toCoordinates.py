import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

# Load your data
df = pd.read_csv("MLB_Teams_Table.csv")  

# Set up geolocator with rate limiter (1 call per second)
geolocator = Nominatim(user_agent="mlb_mapper")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

# Geocode the locations
df['Coordinates'] = df['Location'].apply(geocode)
df['Latitude'] = df['Coordinates'].apply(lambda loc: loc.latitude if loc else None)
df['Longitude'] = df['Coordinates'].apply(lambda loc: loc.longitude if loc else None)


# Save updated data
df.to_csv("mlb_teams_with_coords.csv", index=False)

print("✅ CSV updated with coordinates saved as 'mlb_teams_with_coords.csv'")
