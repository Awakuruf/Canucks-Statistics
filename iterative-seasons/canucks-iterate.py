import requests
import json
import csv
import time
import urllib.parse
from geopy.distance import geodesic
from datetime import datetime
import pytz

BASE_URL = "https://api.nhle.com/stats/rest/en"
TEAM_NAME = "Vancouver Canucks"

# Function to get team ID
def get_team_id():
    response = requests.get(f"{BASE_URL}/team")
    if response.status_code == 200:
        teams = response.json().get("data", [])
        for team in teams:
            if team["fullName"] == TEAM_NAME:
                return team["id"]
    print("Error fetching team data.")
    return None

# Function to convert team IDs to full team names
def convert_id_to_team_name(file):
    response = requests.get(f"{BASE_URL}/team")
    if response.status_code == 200:
        teams = response.json().get("data", [])
        team_id_map = {team["id"]: team["fullName"] for team in teams}
        
        for game in file:
            team_id = game["Opponent Team"]
            game["Opponent Team"] = team_id_map.get(team_id, f"Unknown Team ({team_id})")
        
        return file

    print("Error fetching team data.")
    return None

# Function to determine the NHL season ID
def get_season_id(start_year):
    end_year = start_year + 1
    return f"{start_year}-{end_year}"

# Function to get game history for a given team in a season
def get_game_history(team_id, start_date, end_date):
    query = f"(homeTeamId={team_id} or visitingTeamId={team_id}) and gameDate>='{start_date}' and gameDate<='{end_date}'"
    encoded_query = urllib.parse.quote(query)
    url = f"{BASE_URL}/game?cayenneExp={encoded_query}"

    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get("data", [])
    
    print(f"Error fetching game history for {start_date} - {end_date}")
    return []

nhl_team_mapping = {
    "Anaheim Ducks": {
        "city": "Anaheim",
        "coordinates": (33.8353, -117.9145),
        "time_zone": "America/Los_Angeles"
    },
    "Arizona Coyotes": {
        "city": "Tempe",
        "coordinates": (33.4255, -111.9400),
        "time_zone": "America/Phoenix"
    },
    "Boston Bruins": {
        "city": "Boston",
        "coordinates": (42.3662, -71.0209),
        "time_zone": "America/New_York"
    },
    "Buffalo Sabres": {
        "city": "Buffalo",
        "coordinates": (42.8750, -78.8767),
        "time_zone": "America/New_York"
    },
    "Calgary Flames": {
        "city": "Calgary",
        "coordinates": (51.0374, -114.0620),
        "time_zone": "America/Edmonton"
    },
    "Carolina Hurricanes": {
        "city": "Raleigh",
        "coordinates": (35.8034, -78.7222),
        "time_zone": "America/New_York"
    },
    "Chicago Blackhawks": {
        "city": "Chicago",
        "coordinates": (41.8806, -87.6742),
        "time_zone": "America/Chicago"
    },
    "Colorado Avalanche": {
        "city": "Denver",
        "coordinates": (39.7487, -105.0076),
        "time_zone": "America/Denver"
    },
    "Columbus Blue Jackets": {
        "city": "Columbus",
        "coordinates": (39.9690, -83.0064),
        "time_zone": "America/New_York"
    },
    "Dallas Stars": {
        "city": "Dallas",
        "coordinates": (32.7905, -96.8103),
        "time_zone": "America/Chicago"
    },
    "Detroit Red Wings": {
        "city": "Detroit",
        "coordinates": (42.3252, -83.0514),
        "time_zone": "America/Detroit"
    },
    "Edmonton Oilers": {
        "city": "Edmonton",
        "coordinates": (53.5461, -113.4938),
        "time_zone": "America/Edmonton"
    },
    "Florida Panthers": {
        "city": "Sunrise",
        "coordinates": (26.1585, -80.3256),
        "time_zone": "America/New_York"
    },
    "Los Angeles Kings": {
        "city": "Los Angeles",
        "coordinates": (34.0430, -118.2673),
        "time_zone": "America/Los_Angeles"
    },
    "Minnesota Wild": {
        "city": "Saint Paul",
        "coordinates": (44.9447, -93.1011),
        "time_zone": "America/Chicago"
    },
    "Montreal Canadiens": {
        "city": "Montreal",
        "coordinates": (45.4960, -73.5693),
        "time_zone": "America/Montreal"
    },
    "Nashville Predators": {
        "city": "Nashville",
        "coordinates": (36.1590, -86.7787),
        "time_zone": "America/Chicago"
    },
    "New Jersey Devils": {
        "city": "Newark",
        "coordinates": (40.7336, -74.1711),
        "time_zone": "America/New_York"
    },
    "New York Islanders": {
        "city": "Elmont",
        "coordinates": (40.7007, -73.7080),
        "time_zone": "America/New_York"
    },
    "New York Rangers": {
        "city": "New York",
        "coordinates": (40.7505, -73.9934),
        "time_zone": "America/New_York"
    },
    "Ottawa Senators": {
        "city": "Ottawa",
        "coordinates": (45.2969, -75.9273),
        "time_zone": "America/Toronto"
    },
    "Philadelphia Flyers": {
        "city": "Philadelphia",
        "coordinates": (39.9012, -75.1720),
        "time_zone": "America/New_York"
    },
    "Pittsburgh Penguins": {
        "city": "Pittsburgh",
        "coordinates": (40.4394, -79.9893),
        "time_zone": "America/New_York"
    },
    "San Jose Sharks": {
        "city": "San Jose",
        "coordinates": (37.3329, -121.9012),
        "time_zone": "America/Los_Angeles"
    },
    "Seattle Kraken": {
        "city": "Seattle",
        "coordinates": (47.6221, -122.3541),
        "time_zone": "America/Los_Angeles"
    },
    "St. Louis Blues": {
        "city": "St. Louis",
        "coordinates": (38.6266, -90.2026),
        "time_zone": "America/Chicago"
    },
    "Tampa Bay Lightning": {
        "city": "Tampa",
        "coordinates": (27.9428, -82.4519),
        "time_zone": "America/New_York"
    },
    "Toronto Maple Leafs": {
        "city": "Toronto",
        "coordinates": (43.6435, -79.3791),
        "time_zone": "America/Toronto"
    },
    "Vancouver Canucks": {
        "city": "Vancouver",
        "coordinates": (49.2778, -123.1088),
        "time_zone": "America/Vancouver"
    },
    "Vegas Golden Knights": {
        "city": "Las Vegas",
        "coordinates": (36.1029, -115.1784),
        "time_zone": "America/Los_Angeles"
    },
    "Washington Capitals": {
        "city": "Washington",
        "coordinates": (38.8981, -77.0209),
        "time_zone": "America/New_York"
    },
    "Winnipeg Jets": {
        "city": "Winnipeg",
        "coordinates": (49.8951, -97.1384),
        "time_zone": "America/Winnipeg"
    }
}

# Function to calculate distance traveled
def calculate_distance(home_team, opponent_team):
    # Get coordinates for home and opponent cities
    home_city_info = nhl_team_mapping.get(home_team, {})
    opponent_city_info = nhl_team_mapping.get(opponent_team, {})

    home_coords = home_city_info.get("coordinates", (0, 0))
    opponent_coords = opponent_city_info.get("coordinates", (0, 0))

    # Calculate distance using geodesic
    return geodesic(home_coords, opponent_coords).miles

# Function to calculate time zone change
def calculate_time_zone_change(home_team, opponent_team):
    # Get time zones for home and opponent cities
    home_city_info = nhl_team_mapping.get(home_team, {})
    opponent_city_info = nhl_team_mapping.get(opponent_team, {})

    home_tz_name = home_city_info.get("time_zone", "UTC")
    opponent_tz_name = opponent_city_info.get("time_zone", "UTC")

    # Calculate time zone difference
    home_tz = pytz.timezone(home_tz_name)
    opponent_tz = pytz.timezone(opponent_tz_name)
    return (opponent_tz.utcoffset(datetime.now()) - home_tz.utcoffset(datetime.now())).total_seconds() / 3600  # Convert to hours

# Function to calculate rest days
def calculate_rest_days(previous_game_date, current_game_date):
    if previous_game_date:
        return (current_game_date - previous_game_date).days
    return 0 

def sort_by_date(game_data):
    """
    Sort the game data by the 'Game Date' field in ascending order.
    """
    return sorted(game_data, key=lambda x: datetime.strptime(x["Game Date"], "%Y-%m-%d"))

# Function to save game data to CSV
def save_to_csv(game_data, season):
    if not game_data:
        print(f"No data to save for season {season}.")
        return

    filename = f"canucks_game_history_{season}.csv"
    fieldnames = [
        "Season", "Game Location", "Opponent Team", "Distance Traveled (miles)",
        "Time Zone Change", "Rest Days", "Goals Scored", "Goals Conceded", "Result", "Game Date"
    ]

    with open(filename, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(game_data)

# Function to process game data for a given season
def process_season(team_id, start_year):
    season = get_season_id(start_year)
    start_date = f"{start_year}-10-01"
    end_date = f"{start_year + 1}-04-15"

    games = get_game_history(team_id, start_date, end_date)
    game_data = []

    for game in games:
        goals_scored = game["homeScore"] if game["homeTeamId"] == team_id else game["visitingScore"]
        goals_conceded = game["visitingScore"] if game["homeTeamId"] == team_id else game["homeScore"]
        game_date = game['gameDate']

        game_entry = {
            "Season": season,
            "Game Location": "Home" if game["homeTeamId"] == team_id else "Away",
            "Opponent Team": game["visitingTeamId"] if game["homeTeamId"] == team_id else game["homeTeamId"],
            "Goals Scored": goals_scored,
            "Goals Conceded": goals_conceded,
            "Result": "Win" if goals_scored > goals_conceded else "Loss",
            "Game Date": game_date
        }
        game_data.append(game_entry)

    convert_id_to_team_name(game_data)
    game_data = sort_by_date(game_data)
    process_travel(game_data)

    with open(f"canucks_game_history_{season}.json", "w") as f:
        json.dump(game_data, f, indent=4)

    print(f"Game history saved to canucks_game_history_{season}.json")

    save_to_csv(game_data, season)

# Function to process travel data for the seaso ns
def process_travel(game_data):
    home_team = "Vancouver Canucks"
    previous_game_date = None

    for game in game_data:
        game_date = datetime.strptime(game["Game Date"], "%Y-%m-%d")

        if game["Game Location"] == "Away":
            opponent_team = game["Opponent Team"]
            game["Distance Traveled (miles)"] = calculate_distance(home_team, opponent_team)
            game["Time Zone Change"] = calculate_time_zone_change(home_team, opponent_team)
        else:
            game["Distance Traveled (miles)"] = 0
            game["Time Zone Change"] = 0

        game["Rest Days"] = calculate_rest_days(previous_game_date, game_date)
        previous_game_date = game_date

# Main function to fetch data for multiple seasons
def main():
    team_id = get_team_id()
    if not team_id:
        return

    for start_year in range(2010, 2024): 
        print(f"Fetching season {start_year}-{start_year + 1}...")
        process_season(team_id, start_year)
        time.sleep(1)  

if __name__ == "__main__":
    main()
