import requests
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

# Mock Data for Hotels and Activities
HOTELS = [
    {"name": "ABC Hotel", "stars": 4, "cost_per_night": 100},
    {"name": "Budget Inn", "stars": 2, "cost_per_night": 50},
    {"name": "Luxury Palace", "stars": 5, "cost_per_night": 300},
]

ACTIVITIES = {
    "sports match": {"name": "Real Madrid Match", "date": "12th December", "location": "Section 10, Seats 10-11", "cost": 50},
    "concert": {"name": "Coldplay Concert", "date": "15th December", "location": "Main Stage, Seats 20-21", "cost": 70},
    "cooking class": {"name": "Italian Cooking Masterclass", "date": "10th December", "location": "Downtown Studio", "cost": 30},
    "museum trip": {"name": "Louvre Museum Tour", "date": "14th December", "location": "Louvre Hall 3", "cost": 25},
}

# API configuration
ACCESS_KEY = "29e3b19056a8944a8d18424add3772be"  # Your API key
BASE_URL = "http://api.currencylayer.com/"

def fetch_historical_rates(start_year=2018, end_year=2022, base_currency="USD", target_currency="TRY"):
    """
    Fetch historical exchange rates using CurrencyLayer API.
    """
    historical_data = []
    for year in range(start_year, end_year + 1):
        date = f"{year}-01-01"
        endpoint = f"{BASE_URL}historical"
        params = {"access_key": ACCESS_KEY, "date": date, "source": base_currency, "currencies": target_currency}
        response = requests.get(endpoint, params=params)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                rate = data["quotes"].get(f"{base_currency}{target_currency}")
                historical_data.append({"Year": year, "Exchange Rate": rate})
            else:
                print(f"API Error: {data.get('error', {}).get('info', 'Unknown Error')}")
        else:
            print(f"Failed to fetch data for {date}. Status Code: {response.status_code}")
    if not historical_data:
        raise ValueError("No data fetched from the API.")
    return pd.DataFrame(historical_data)

# Fetch exchange rates
df_exchange = fetch_historical_rates()

# Inflation mock data
inflation_data = {2018: 10.1, 2019: 11.5, 2020: 14.6, 2021: 19.1, 2022: 24.0}
df_exchange["Inflation (%)"] = df_exchange["Year"].map(inflation_data)

# Train Linear Regression Model
X = df_exchange["Inflation (%)"].values.reshape(-1, 1)
y = df_exchange["Exchange Rate"].values
model = LinearRegression()
model.fit(X, y)

# Predict next year's exchange rate
future_inflation = np.array([26.0]).reshape(-1, 1)
predicted_rate = model.predict(future_inflation)[0]

def suggest_hotel(standard, days):
    """
    Suggest a hotel based on the user's standard and calculate the total cost.
    """
    if standard == "low":
        hotel = HOTELS[1]
    elif standard == "mid":
        hotel = HOTELS[0]
    else:
        hotel = HOTELS[2]
    total_cost = hotel["cost_per_night"] * days
    return hotel, total_cost

def suggest_activity():
    """
    Allow the user to choose an activity and return its details.
    """
    print("Choose an activity: Sports Match, Concert, Cooking Class, Museum Trip")
    choice = input("Enter your activity preference: ").lower()
    return ACTIVITIES.get(choice, None)

# User Inputs
destination = input("Enter your travel destination: ")
days = int(input("Enter the number of nights for your stay: "))
standard = input("Enter your travel standard (low, mid, high): ").lower()

# Calculate costs
hotel, hotel_cost = suggest_hotel(standard, days)
activity = suggest_activity()

# Display Results
print("\nTravel Cost Breakdown:")
print(f"I booked '{hotel['name']}' ({hotel['stars']}-star) for {days} nights, costing ${hotel_cost}.")
if activity:
    print(f"Based on your preferences, I got you tickets for '{activity['name']}' on {activity['date']} at {activity['location']}.")
    print(f"Activity cost: ${activity['cost']}.")
else:
    print("No activity selected.")

total_cost = hotel_cost + (activity['cost'] if activity else 0)
total_cost_in_try = total_cost * predicted_rate

print(f"\nTotal estimated cost in USD: ${total_cost:.2f}")
print(f"Total estimated cost in TRY: {total_cost_in_try:.2f} TL")