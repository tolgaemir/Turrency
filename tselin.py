import requests
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

# Mock Data for Hotels
HOTELS = [
    {"name": "ABC Hotel", "stars": 4, "cost_per_night": 100},
    {"name": "Budget Inn", "stars": 2, "cost_per_night": 50},
    {"name": "Luxury Palace", "stars": 5, "cost_per_night": 300},
]

# API Configuration
AMADEUS_API_KEY = "jBjwRbGNmsWfZWSQDw1utF6VEkZwwATF"
AMADEUS_API_SECRET = "JDI256aCkqF8UYQG"
TOKEN_URL = "https://test.api.amadeus.com/v1/security/oauth2/token"
ACTIVITIES_URL = "https://test.api.amadeus.com/v1/shopping/activities"
BASE_URL_CURRENCY = "http://api.currencylayer.com/"
ACCESS_KEY_CURRENCY = "29e3b19056a8944a8d18424add3772be"

def get_amadeus_access_token():
    """
    Fetch an access token from the Amadeus API.
    """
    payload = {
        "grant_type": "client_credentials",
        "client_id": AMADEUS_API_KEY,
        "client_secret": AMADEUS_API_SECRET
    }
    response = requests.post(TOKEN_URL, data=payload)
    response.raise_for_status()
    return response.json().get("access_token")

def fetch_activities(location, token):
    """
    Fetch touristic activities from Amadeus API for a specific location.
    """
    params = {"latitude": location["latitude"], "longitude": location["longitude"]}
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(ACTIVITIES_URL, headers=headers, params=params)
    response.raise_for_status()
    return response.json().get("data", [])

def fetch_historical_rates(start_year=2018, end_year=2022, base_currency="USD", target_currency="TRY"):
    """
    Fetch historical exchange rates using CurrencyLayer API.
    """
    historical_data = []
    for year in range(start_year, end_year + 1):
        date = f"{year}-01-01"
        endpoint = f"{BASE_URL_CURRENCY}historical"
        params = {
            "access_key": ACCESS_KEY_CURRENCY,
            "date": date,
            "source": base_currency,
            "currencies": target_currency
        }
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

def suggest_activity(activities):
    """
    Allow the user to choose an activity and return its details.
    """
    print("Choose an activity:")
    for i, activity in enumerate(activities):
        price = activity.get('price', {})
        amount = price.get('amount', 'N/A')
        currency = price.get('currency', 'N/A')
        print(f"{i + 1}. {activity['name']} - {amount} {currency}")
    choice = int(input("Enter your choice: ")) - 1
    return activities[choice] if 0 <= choice < len(activities) else None

# User Inputs
destination = input("Enter your travel destination: ")
days = int(input("Enter the number of nights for your stay: "))
standard = input("Enter your travel standard (low, mid, high): ").lower()

# Example location (latitude, longitude) for the destination
location = {"latitude": 40.4168, "longitude": -3.7038}  # Madrid, Spain

# Fetch activities
token = get_amadeus_access_token()
activities = fetch_activities(location, token)

# Calculate costs
hotel, hotel_cost = suggest_hotel(standard, days)
activity = suggest_activity(activities)

# Display Results
print("\nTravel Cost Breakdown:")
print(f"I booked '{hotel['name']}' ({hotel['stars']}-star) for {days} nights, costing ${hotel_cost}.")
if activity:
    activity_price = activity.get('price', {})
    amount = activity_price.get('amount', 'N/A')
    currency = activity_price.get('currency', 'N/A')
    print(f"Based on your preferences, I got you tickets for '{activity['name']}' at {activity['geoCode']}.")
    print(f"Activity cost: {amount} {currency}.")
else:
    print("No activity selected.")

total_cost = hotel_cost + (float(activity_price.get('amount', 0)) if activity else 0)
total_cost_in_try = total_cost * predicted_rate

print(f"\nTotal estimated cost in USD: ${total_cost:.2f}")
print(f"Total estimated cost in TRY: {total_cost_in_try:.2f} TL")
