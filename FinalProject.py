"""
Name:    Michael Kui
CS230:   Section 6
Data:    World Air Quality Index by City and Coordinates
URL:

Description:
This program allows users to explore global air quality data using interactive
charts, filters, and maps. Users can filter by country, city, and AQI range
to visualize pollution trends and compare air quality across different locations.
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.title("Air Quality Dashboard")

# Load data
df = pd.read_csv("air_quality_index.csv")

# Country filter (line 51)
country = st.selectbox(
    "Select a Country",
    sorted(df["Country"].dropna().astype(str).unique())
)

# Filter by country
country_df = df[df["Country"] == country]

# Function to load and clean data
@st.cache_data
def load_data():
    df = pd.read_csv("air_quality_index.csv")
    df.columns = df.columns.str.strip()

    # Rename lat/lng columns
    df.rename(columns={"lat": "Latitude", "lng": "Longitude"}, inplace=True)

    # Drop rows with missing key data
    df.dropna(subset=["AQI Value", "Latitude", "Longitude"], inplace=True)

    # Standardize types
    df["AQI Value"] = pd.to_numeric(df["AQI Value"], errors="coerce")
    df["City"] = df["City"].str.title()
    df["Country"] = df["Country"].str.title()

    return df

# --- Main Streamlit App ---
def main():
    df = load_data()

    st.title("World Air Quality Explorer")

    # Filter: Country
    country = st.selectbox(
        "Select a Country", 
        sorted(df["Country"].dropna().astype(str).unique()),
        key="country_select"
    )
    country_df = df[df["Country"] == country]

    # Filter: City
    city = st.selectbox(
        "Select a City", 
        sorted(country_df["City"].dropna().astype(str).unique()),
        key="city_select"
    )
    city_df = country_df[country_df["City"] == city]

    # Filter: AQI range
    aqi_min = int(city_df["AQI Value"].min())
    aqi_max = int(city_df["AQI Value"].max())
    aqi_range = st.slider("Select AQI Range", aqi_min, aqi_max, (aqi_min, aqi_max), key="aqi_slider")
    filtered_df = city_df[
        (city_df["AQI Value"] >= aqi_range[0]) &
        (city_df["AQI Value"] <= aqi_range[1])
    ]

    # Chart 1: AQI Category counts in selected city
    st.subheader(f"AQI Category Breakdown - {city}")
    category_counts = filtered_df["AQI Category"].value_counts()
    fig1, ax1 = plt.subplots()
    ax1.bar(category_counts.index, category_counts.values, color="skyblue")
    ax1.set_xlabel("AQI Category")
    ax1.set_ylabel("Count")
    ax1.set_title(f"AQI Categories in {city}")
    st.pyplot(fig1)

    # Chart 2: Average AQI by city in selected country
    st.subheader(f"Average AQI by City in {country}")
    avg_aqi_by_city = country_df.groupby("City")["AQI Value"].mean().sort_values()
    fig2, ax2 = plt.subplots(figsize=(10, 4))
    ax2.bar(avg_aqi_by_city.index, avg_aqi_by_city.values, color="coral")
    ax2.set_xticklabels(avg_aqi_by_city.index, rotation=45, ha='right')
    ax2.set_ylabel("Average AQI")
    st.pyplot(fig2)

    # AQI Summary
    st.subheader(f"AQI Summary for {city}")
    min_aqi, max_aqi = describe_city(city, country_df)
    st.markdown(f"- Minimum AQI: **{min_aqi}**")
    st.markdown(f"- Maximum AQI: **{max_aqi}**")
    st.markdown(f"- Average AQI: **{round(city_df['AQI Value'].mean(), 2)}**")

    # Top 5 highest AQI values
    st.subheader("Top 5 AQI Readings in City")
    st.dataframe(city_df.sort_values("AQI Value", ascending=False).head(5))

    # Add AQI rating labels
    filtered_df["AQI Rating"] = np.where(
        filtered_df["AQI Value"] < 50, "Good",
        np.where(filtered_df["AQI Value"] < 100, "Moderate",
                    np.where(filtered_df["AQI Value"] < 150, "Unhealthy", "Very Unhealthy"))
    )

    # Sample rows with labels
    st.subheader("Sample Classified Records")
    for _, row in filtered_df.head(3).iterrows():
        st.write(f"{row['City']} - AQI {row['AQI Value']} ({row['AQI Rating']})")

if __name__ == "__main__":
    main()
     
