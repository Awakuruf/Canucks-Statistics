import requests
import json
import csv

BASE_URL = "https://api.nhle.com/stats/rest/en"
TEAM_NAME = "Vancouver Canucks"

# Function to get all teams and retrieve Canucks' team ID
def get_team_id():
    response = requests.get(f"{BASE_URL}/team")
    if response.status_code == 200:
        teams = response.json().get("data", [])
        for team in teams:
            if team["fullName"] == TEAM_NAME:
                return team["id"]
    print("Error fetching team data.")
    return None

# Funtions to conver the team ID into teamName
def converIdtoFullTeamName(file):
    response = requests.get(f"{BASE_URL}/team")
    
    if response.status_code == 200:
        teams = response.json().get("data", [])
        
        # Create a mapping of teamId -> fullName
        team_id_map = {team["id"]: team["fullName"] for team in teams}
        
        # Replace Opponent Team ID with Full Team Name
        for game in file:
            team_id = game["Opponent Team"]
            game["Opponent Team"] = team_id_map.get(team_id, f"Unknown Team ({team_id})")
        
        return file
    
    print("Error fetching team data.")
    return None

# Function to get current season
def get_latest_season():
    response = requests.get(f"{BASE_URL}/season")
    if response.status_code == 200:
        seasons = response.json().get("data", [])
        return max(seasons, key=lambda x: x["formattedSeasonId"])["formattedSeasonId"]  # Latest season
    print("Error fetching season data.")
    return None

def get_season_from_dates(start_date, end_date):
    """
    Determines the NHL season from the given start and end dates.

    :param start_date: Start date in "YYYY-MM-DD" format
    :param end_date: End date in "YYYY-MM-DD" format
    :return: Season ID in "YYYYYYYY" format (e.g., "20232024")
    """
    start_year = start_date[:4]  # Extract the first 4 characters (YYYY)
    end_year = end_date[:4]      # Extract the first 4 characters (YYYY)
    
    return f"{start_year}-{end_year}"  # Format as "YYYYYYYY"

import urllib.parse

BASE_URL = "https://api.nhle.com/stats/rest/en"

def get_game_history(team_id, start_date, end_date):
    """
    Fetches game history for a given team between start_date and end_date.
    
    :param team_id: ID of the team (e.g., 23 for Vancouver Canucks)
    :param start_date: Start date in YYYY-MM-DD format
    :param end_date: End date in YYYY-MM-DD format
    :return: List of games
    """
    query = f"(homeTeamId={team_id} or visitingTeamId={team_id}) and gameDate>='{start_date}' and gameDate<='{end_date}'"
    encoded_query = urllib.parse.quote(query)
    url = f"{BASE_URL}/game?cayenneExp={encoded_query}"

    response = requests.get(url)
    # print(f"Request URL: {url}")  # Debugging
    # print(f"Response Status Code: {response.status_code}")
    
    if response.status_code == 200:
        return response.json().get("data", [])
    
    print(f"Error fetching game history: {response.text}")
    return []

# Example usage
team_id = 23  # Vancouver Canucks
start_date = "2023-10-01"  # Example start date
end_date = "2024-04-15"  # Example end date
games = get_game_history(team_id, start_date, end_date)
print("This is the games:", games)

# -----------------------------------------

# import urllib.parse

# BASE_URL = "https://api.nhle.com/stats/rest/en"

# def get_game_history(team_id, season):
#     query = f"formattedSeasonId={season} and (homeTeamId={team_id} or awayTeamId={team_id})"
#     encoded_query = urllib.parse.quote(query)  # Encode query parameters
#     url = f"{BASE_URL}/game?cayenneExp={encoded_query}"
    
#     response = requests.get(url)
#     print(f"Request URL: {url}")  # Debugging
#     print(f"Response Status Code: {response.status_code}")
    
#     if response.status_code == 200:
#         return response.json().get("data", [])
    
#     print(f"Error fetching game history: {response.text}")
#     return []

# # Example usage
# team_id = 23  # Vancouver Canucks (Check the actual team ID from the API)
# season = 20232024  # Example season
# games = get_game_history(team_id, season)
# print("Here are the games:", games)

#-----------------

# # Function to get game history for a specific team and season
# def get_game_history(team_id, season):
#     query = f"cayenneExp=seasonId={season} and (homeTeamId={team_id} or awayTeamId={team_id})"
#     response = requests.get(f"{BASE_URL}/game?{query}")
#     print(response)
#     if response.status_code == 200:
#         return response.json().get("data", [])
#     print("Error fetching game history.")
#     return []

def save_to_csv(game_data, season):
    if not game_data:
        print("No data to save.")
        return

    filename = f"canucks_game_history_{season}.csv"  
    fieldnames = game_data[0].keys()

    with open(filename, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(game_data)

    print(f"Game history saved to {filename}")

# Main function
def main():
    team_id = get_team_id()
    start_date = "2023-10-01"  # Example start date
    end_date = "2024-04-15"  # Example end date
    season = get_season_from_dates(start_date, end_date)
    if not team_id or not season:
        return
    
    games = get_game_history(team_id, start_date, end_date)
    game_data = []
    
    for game in games:
        game_entry = {
            "Season": season,
            "Game Location": "Home" if game["homeTeamId"] == team_id else "Away",
            "Opponent Team": game["visitingTeamId"] if game["homeTeamId"] == team_id else game["homeTeamId"],
            "Goals Scored": game["homeScore"] if game["homeTeamId"] == team_id else game["visitingScore"],
            "Goals Conceded": game["visitingScore"] if game["homeTeamId"] == team_id else game["homeScore"],
            "Result": "Win" if game["homeScore"] > game["visitingScore"] else "Loss",
        }
        game_data.append(game_entry)

    converIdtoFullTeamName(game_data)
    
    with open("canucks_game_history.json", "w") as f:
        json.dump(game_data, f, indent=4)
    
    print("Game history saved to canucks_game_history.json")

    if game_data:
        save_to_csv(game_data, season)

if __name__ == "__main__":
    main()
