import requests
import json

BASE_URL = "https://api.nhle.com/stats/rest/en"
TEAM_NAME = "Vancouver Canucks"

# Function to get all teams and retrieve Canucks' team ID
def get_team_id():
    response = requests.get(f"{BASE_URL}/team")
    if response.status_code == 200:
        teams = response.json().get("data", [])
        for team in teams:
            if team["teamFullName"] == TEAM_NAME:
                return team["id"]
    print("Error fetching team data.")
    return None

# Function to get current season
def get_current_season():
    response = requests.get(f"{BASE_URL}/season")
    if response.status_code == 200:
        seasons = response.json().get("data", [])
        return max(seasons, key=lambda x: x["seasonId"])["seasonId"]  # Latest season
    print("Error fetching season data.")
    return None

# Function to get game history for a specific team and season
def get_game_history(team_id, season):
    query = f"cayenneExp=seasonId={season} and (homeTeamId={team_id} or awayTeamId={team_id})"
    response = requests.get(f"{BASE_URL}/game?{query}")
    if response.status_code == 200:
        return response.json().get("data", [])
    print("Error fetching game history.")
    return []

# Main function
def main():
    team_id = get_team_id()
    season = get_current_season()
    if not team_id or not season:
        return
    
    games = get_game_history(team_id, season)
    game_data = []
    
    for game in games:
        game_entry = {
            "Season": season,
            "Game Location": "Home" if game["homeTeamId"] == team_id else "Away",
            "Opponent Team": game["awayTeamFullName"] if game["homeTeamId"] == team_id else game["homeTeamFullName"],
            "Goals Scored": game["goalsFor"] if game["homeTeamId"] == team_id else game["goalsAgainst"],
            "Goals Conceded": game["goalsAgainst"] if game["homeTeamId"] == team_id else game["goalsFor"],
            "Result": "Win" if game["gameOutcome"] == "W" else "Loss",
        }
        game_data.append(game_entry)
    
    # Save results to a JSON file
    with open("canucks_game_history.json", "w") as f:
        json.dump(game_data, f, indent=4)
    
    print("Game history saved to canucks_game_history.json")

if __name__ == "__main__":
    main()
