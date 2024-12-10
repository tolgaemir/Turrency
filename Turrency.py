import requests
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

# API configuration
ACCESS_KEY = "29e3b19056a8944a8d18424add3772be"  # Your API key
BASE_URL = "http://api.currencylayer.com/"

def fetch_historical_rates(start_year=2018, end_year=2022, base_currency="USD", target_currency="TRY"):
    """
    Fetch historical exchange rates using CurrencyLayer API.
    """
    historical_data = []
    for year in range(start_year, end_year + 1):
        date = f"{year}-01-01"  # Fetch rates for the start of each year
        endpoint = f"{BASE_URL}historical"
        params = {
            "access_key": ACCESS_KEY,
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
        raise ValueError("No data fetched from the API. Check your access key or endpoint permissions.")
    return pd.DataFrame(historical_data)

# Fetch historical exchange rates
df_exchange = fetch_historical_rates()

# Mock inflation data (replace this with real data if available)
inflation_data = {
    2018: 10.1,
    2019: 11.5,
    2020: 14.6,
    2021: 19.1,
    2022: 24.0
}
df_exchange["Inflation (%)"] = df_exchange["Year"].map(inflation_data)

# Train a Linear Regression model
X = df_exchange["Inflation (%)"].values.reshape(-1, 1)  # Predictor: Inflation rate
y = df_exchange["Exchange Rate"].values  # Target: Exchange rate
model = LinearRegression()
model.fit(X, y)

# Predict future exchange rates
future_inflation = np.array([25.0, 30.0]).reshape(-1, 1)  # Example future inflation rates
predicted_exchange_rates = model.predict(future_inflation)

def calculate_budget(destination, days, standard):
    """
    Calculate estimated travel budget based on predicted exchange rate.
    """
    # Example cost categories
    costs_per_day = {
        "high": 200,  # in Euro
        "mid": 120,
        "low": 80
    }
    euro_to_tl = predicted_exchange_rates[0]  # Use the first prediction
    daily_cost_in_tl = costs_per_day[standard] * euro_to_tl
    total_cost_in_tl = daily_cost_in_tl * days
    return total_cost_in_tl

# User Input
destination = input("Enter your travel destination: ")
days = int(input("Enter the number of days for your trip: "))
standard = input("Enter your travel standard (high, mid, low): ").lower()

# Calculate and display budget
budget = calculate_budget(destination, days, standard)
print(f"\nEstimated travel cost for {days} days in {destination} ({standard} standard): {budget:.2f} TL")

# Visualization
plt.scatter(df_exchange["Inflation (%)"], df_exchange["Exchange Rate"], color="blue", label="Historical Data")
plt.plot(future_inflation, predicted_exchange_rates, color="red", marker="o", label="Predicted Rates")
plt.title("Exchange Rate vs Inflation")
plt.xlabel("Inflation (%)")
plt.ylabel("Exchange Rate (USD to TRY)")
plt.legend()
plt.grid()
plt.show()