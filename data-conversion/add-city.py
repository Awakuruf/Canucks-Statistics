import pandas as pd
import unicodedata

# Load the dataset
df = pd.read_csv('../CleanedCanucksData(1).csv')

# Normalize function to remove accents
def normalize_city_name(name):
    return unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('utf-8')

# Mapping from normalized city names to state/province
city_to_state = {
    "Anaheim": "California",
    "Atlanta": "Georgia",
    "Arizona": "Arizona",
    "Phoenix": "Arizona",
    "Boston": "Massachusetts",
    "Buffalo": "New York",
    "Calgary": "Alberta",
    "Carolina": "North Carolina",
    "Chicago": "Illinois",
    "Colorado": "Colorado",
    "Columbus": "Ohio",
    "Dallas": "Texas",
    "Detroit": "Michigan",
    "Edmonton": "Alberta",
    "Florida": "Florida",
    "Los Angeles": "California",
    "Minnesota": "Minnesota",
    "Montreal": "Quebec",
    "Montréal": "Quebec",  # in case not normalized
    "Nashville": "Tennessee",
    "New Jersey": "New Jersey",
    "NY Islanders": "New York",
    "New York": "New York",  # For NY Rangers
    "Ottawa": "Ontario",
    "Philadelphia": "Pennsylvania",
    "Pittsburgh": "Pennsylvania",
    "San Jose": "California",
    "Seattle": "Washington",
    "St. Louis": "Missouri",
    "Tampa Bay": "Florida",
    "Toronto": "Ontario",
    "Vancouver": "British Columbia",
    "Vegas": "Nevada",
    "Washington": "District of Columbia",
    "Winnipeg": "Manitoba"
}

# Extract city from Opponent Team
def extract_city(team_name):
    words = team_name.split()
    
    # Handle special cases like "St. Louis Blues"
    if team_name.startswith("St. Louis"):
        return "St. Louis"
    
    # Otherwise, return the first word or first two depending on known patterns
    two_words = " ".join(words[:2])
    if two_words in city_to_state:
        return two_words
    return words[0]

# Apply to create City column
df['City'] = df.apply(
    lambda row: "Vancouver" if row["Game Location"] == "Home" else extract_city(row["Opponent Team"]),
    axis=1
)

# Normalize city names before lookup
df['Normalized_City'] = df['City'].apply(normalize_city_name)

# Map to state/province
df['State/Province'] = df['Normalized_City'].map(city_to_state)

# Coordinates
df["City_Latitude"] = df.apply(
    lambda row: row["From (Latitude)"] if row["Game Location"] == "Home" else row["To (Latitude)"], axis=1
)

df["City_Longitude"] = df.apply(
    lambda row: row["From (Longitude)"] if row["Game Location"] == "Home" else row["To (Longitude)"], axis=1
)

# Save cleaned dataset
df.drop(columns=["Normalized_City"], inplace=True)
df.to_csv("../Updated_CanucksData.csv", index=False)

# Preview
print(df[["Opponent Team", "Game Location", "City", "State/Province"]].head(10))
