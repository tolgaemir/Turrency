import requests
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
from datetime import datetime

# API Configuration
API_KEY = "ff408e4543587cb24f32355577d09d3f"  # Your API Key
BASE_URL = "http://api.exchangerate.host/"

# Function to fetch live exchange rates
def fetch_live_exchange_rates(base_currency="GBP", target_currencies="USD,AUD,CAD,PLN,MXN"):
    """
    Fetch the most recent exchange rates from the API.
    """
    url = f"{BASE_URL}live?access_key={API_KEY}&source={base_currency}&currencies={target_currencies}&format=1"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        print("API Response:", data)  # Print the full response to check the structure
        if "quotes" in data:
            return data["quotes"]  # Return the exchange rates under the 'quotes' key
        else:
            print("Error: 'quotes' not found in the response.")
            return None
    else:
        print(f"Failed to fetch data. Status Code: {response.status_code}")
        return None

# Function to fetch historical exchange rates
def fetch_historical_rates(start_year=2018, end_year=2025, base_currency="USD", target_currency="TRY"):
    """
    Fetch historical exchange rates using ExchangeRate.host API.
    """
    historical_data = []
    for year in range(start_year, end_year + 1):
        date = f"{year}-01-01"  # Fetch rates for the start of each year
        url = f"{BASE_URL}historical?access_key={API_KEY}&date={date}&source={base_currency}&currencies={target_currency}&format=1"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print(f"API Response for {year}: {data}")  # Print the response to check for 'quotes'
            rate = data.get("quotes", {}).get(f"{base_currency}{target_currency}")
            if rate:
                historical_data.append({"Year": year, "Exchange Rate": rate})
                print(f"Fetched exchange rate for {year}: {rate}")
            else:
                print(f"Rate for {target_currency} not available on {date}.")
        else:
            print(f"Failed to fetch data for {year}. Status Code: {response.status_code}")
    return pd.DataFrame(historical_data)

# Function to calculate the travel budget
def calculate_budget(destination, days, standard, predicted_rate_2024, start_date):
    """
    Calculate estimated travel budget based on predicted exchange rate for 2024.
    """
    # Extract year from the start date
    start_year = datetime.strptime(start_date, "%Y-%m-%d").year

    # Example cost categories (in Euro)
    costs_per_day = {
        "high": 200,
        "mid": 120,
        "low": 80
    }

    # Get the exchange rate for the start year of the trip (e.g., 2024)
    if start_year in predicted_rate_2024:
        euro_to_tl = predicted_rate_2024[start_year]
    else:
        euro_to_tl = predicted_rate_2024[2024]  # Default to the 2024 rate if no specific year is found

    daily_cost_in_tl = costs_per_day[standard] * euro_to_tl
    total_cost_in_tl = daily_cost_in_tl * days
    return total_cost_in_tl

# Fetch live exchange rates for debugging and demonstration
live_rates = fetch_live_exchange_rates()
if live_rates:
    print("Live Exchange Rates:", live_rates)

# Fetch historical exchange rates
df_exchange = fetch_historical_rates(start_year=2018, end_year=2025)

# Check if the DataFrame is empty and handle it
if df_exchange.empty:
    print("No historical exchange rates were fetched.")
else:
    # Mock inflation data (replace this with real data if available)
    inflation_data = {
        2018: 10.1,
        2019: 11.5,
        2020: 14.6,
        2021: 19.1,
        2022: 24.0,
        2023: 40.0,  # Example inflation data for 2023
        2024: 45.0,  # Example inflation data for 2024
        2025: 50.0   # Example inflation data for 2025 (this is an assumption for future prediction)
    }

    # Add inflation data to the dataframe
    df_exchange["Inflation (%)"] = df_exchange["Year"].map(inflation_data)

    # Train a Linear Regression model
    X = df_exchange["Inflation (%)"].values.reshape(-1, 1)  # Predictor: Inflation rate
    y = df_exchange["Exchange Rate"].values  # Target: Exchange rate
    model = LinearRegression()
    model.fit(X, y)

    # Predict future exchange rates for the years 2024-2025
    future_inflation = np.array([40.0, 45.0, 50.0]).reshape(-1, 1)  # Example future inflation rates for 2023, 2024 & 2025
    predicted_exchange_rates = model.predict(future_inflation)

    # Create a dictionary of predicted exchange rates for 2024 and 2025
    predicted_rate_2024 = {
        2024: predicted_exchange_rates[1],
        2025: predicted_exchange_rates[2]
    }

    # User Input for Travel Budget
    destination = input("Enter your travel destination: ")
    days = int(input("Enter the number of days for your trip: "))
    start_date = input("Enter the start date of your trip (YYYY-MM-DD): ")

    while True:
        standard = input("Enter your travel standard (high, mid, low): ").lower()
        if standard in ["high", "mid", "low"]:
            break
        print("Invalid input! Please enter 'high', 'mid', or 'low'.")

    # Calculate and display budget
    budget = calculate_budget(destination, days, standard, predicted_rate_2024, start_date)
    print(f"\nEstimated travel cost for {days} days in {destination} ({standard} standard): {budget:.2f} TL")

    # Visualization of Exchange Rates and Inflation
    plt.scatter(df_exchange["Inflation (%)"], df_exchange["Exchange Rate"], color="blue", label="Historical Data")
    plt.plot(future_inflation, predicted_exchange_rates, color="red", marker="o", linestyle="--", label="Predicted Rates")
    plt.title("Exchange Rate vs Inflation")
    plt.xlabel("Inflation (%)")
    plt.ylabel("Exchange Rate (USD to TRY)")
    plt.legend()
    plt.grid()
    plt.show()
