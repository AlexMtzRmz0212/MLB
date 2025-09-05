from prompt_toolkit import HTML
import requests
import pandas as pd
import os
os.system('cls' if os.name == 'nt' else 'clear')

def get_teams_info():
    url = "https://statsapi.mlb.com/api/v1/teams"
    response = requests.get(url)
    
    if response.status_code != 200:
        print("Failed to fetch teams data")
        return None
    
    data = response.json()
    teams = data.get("teams", [])
    
    team_info = []
    for team in teams:
        league_name = team.get("league", {}).get("name", "N/A")

        # Filter only American and National leagues
        if league_name not in ["American League", "National League"]:
            continue

        team_info.append({
            "id": team["id"],
            "name": team["name"],
            "abbreviation": team["abbreviation"],
            "teamName": team["teamName"],
            "shortName": team["shortName"],
            "franchiseName": team["franchiseName"],
            "clubName": team["clubName"],
            "location": team["locationName"],
            "league": league_name,
            "division": team.get("division", {}).get("name", "N/A"),
            "venue": team["venue"]["name"],
            "firstYearOfPlay": team.get("firstYearOfPlay", "N/A"),
            "yearsActive": pd.Timestamp.now().year - pd.to_datetime(team.get("firstYearOfPlay", "ERROR"), errors='coerce').year if team.get("firstYearOfPlay") else "N/A",
        })
    
    return pd.DataFrame(team_info)

def save_teams_info(df, filename, filetype="csv"):
    if filetype == "csv":
        df.to_csv(filename, index=False)
        print(f"Teams information saved to {filename}")
    elif filetype == "excel":
        df.to_excel(filename, index=False)
        print(f"Teams information saved to {filename}")
    else:
        print(f"Unsupported file type: {filetype}")

def save_teams_info_to_html_sortable(df, filename="Teams Info/MLB_Teams_Info.html"):
    # Generate the basic HTML table from the DataFrame
    html_table = df.to_html(index=False, table_id="mlb_teams_table") #

    # Add the necessary HTML, CSS, and JavaScript for DataTables
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>MLB Teams Info</title>
        <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/2.0.8/css/dataTables.dataTables.min.css">
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.7.1/jquery.min.js"></script>
        <script type="text/javascript" src="https://cdn.datatables.net/2.0.8/js/dataTables.min.js"></script>
    </head>
    <body>

    {html_table}

    <script>
    $(document).ready( function () {{
        $('#mlb_teams_table').DataTable(); // Initialize DataTables on your table
    }} );
    </script>

    </body>
    </html>
    """

    # Write the complete HTML content to the file
    with open(filename, "w") as f:
        f.write(html_content)

    print(f"Sortable HTML table saved to {filename}")

if __name__ == "__main__":
    teams_df = get_teams_info()
    if teams_df is not None:
        # Save to CSV and Excel
        save_teams_info(teams_df, "Teams Info/MLB_Teams_Info.csv", "csv")
        save_teams_info(teams_df, "Teams Info/MLB_Teams_Info.xlsx", "excel")
        save_teams_info_to_html_sortable(teams_df)
    else:
        print("No team information available.")