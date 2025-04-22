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

# Function to load and clean data
@st.cache_data
def load_data():
     df = pd.read_csv("air_quality_index.csv")
    df.columns = df.columns.str.strip()

    df.rename(columns={"Lat": "Latitude", "Lng": "Longitude", "date": "Date"}, inplace=True)

    df.dropna(subset=["AQI Value"], inplace=True)
    df["AQI Value"] = pd.to_numeric(df["AQI Value"], errors="coerce")
    df["City"] = df["City"].str.title()
    df["Country"] = df["Country"].str.title()
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    return df

# Function to describe city AQI
def describe_city(city, df):
    city_data = df[df["City"] == city]
    return city_data["AQI Value"].min(), city_data["AQI Value"].max()

def main():
    df = load_data()

    st.title("🌎 Global Air Quality Explorer")

    # Country selection
    selected_country = st.selectbox("Select a country", sorted(df["Country"].unique()))
    country_df = df[df["Country"] == selected_country]

    # City selection
    selected_city = st.selectbox("Select a city", sorted(country_df["City"].unique()))
    city_df = country_df[country_df["City"] == selected_city]

    # AQI range selection
    aqi_min = int(city_df["AQI Value"].min())
    aqi_max = int(city_df["AQI Value"].max())
    aqi_range = st.slider("Select AQI range", aqi_min, aqi_max, (aqi_min, aqi_max))

    filtered_df = city_df[
        (city_df["AQI Value"] >= aqi_range[0]) &
        (city_df["AQI Value"] <= aqi_range[1])
    ]

    # Line chart: AQI over time
    st.subheader("📈 AQI Over Time")
    fig1, ax1 = plt.subplots()
    ax1.plot(filtered_df["Date"], filtered_df["AQI Value"], marker='o', linestyle='-')
    ax1.set_title(f"AQI in {selected_city}")
    ax1.set_xlabel("Date")
    ax1.set_ylabel("AQI Value")
    ax1.grid(True)
    st.pyplot(fig1)

    # Bar chart: Average AQI by city
    st.subheader("📊 Average AQI by City")
    avg_aqi = country_df.groupby("City")["AQI Value"].mean().sort_values()
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    ax2.bar(avg_aqi.index, avg_aqi.values, color="skyblue")
    ax2.set_xticklabels(avg_aqi.index, rotation=45, ha="right")
    ax2.set_ylabel("Average AQI")
    ax2.set_title(f"Average AQI in {selected_country}")
    st.pyplot(fig2)

    # Display AQI range for selected city
    min_aqi, max_aqi = describe_city(selected_city, df=country_df)
    st.write(f"**{selected_city} AQI Range**: Min = {min_aqi}, Max = {max_aqi}")

    # Display filtered data
    try:
        st.write(filtered_df.head())
    except Exception as e:
        st.error(f"Data error: {e}")

    # AQI dictionary
    aqi_dict = {city: round(val, 2) for city, val in avg_aqi.items()}
    st.write("City AQI dictionary:", aqi_dict)

    # Top 5 AQI readings
    sorted_df = filtered_df.sort_values("AQI Value", ascending=False)
    st.subheader("🔥 Top 5 AQI Readings")
    st.dataframe(sorted_df[["Date", "City", "AQI Value"]].head(5))

    # Add AQI category
    filtered_df["AQI Category"] = np.where(
        filtered_df["AQI Value"] < 50, "Good",
        np.where(filtered_df["AQI Value"] < 100, "Moderate",
                 np.where(filtered_df["AQI Value"] < 150, "Unhealthy", "Very Unhealthy"))
    )

    # Sample records
    st.subheader("📋 Sample Records")
    for _, row in filtered_df.head(3).iterrows():
        st.write(f"{row['City']} on {row['Date'].date()} → AQI {row['AQI Value']} ({row['AQI Category']})")

    # Custom style
    st.markdown("""
    <style>
    body {
        background-color: #f5f9ff;
    }
    h1, h2, h3 {
        color: #2c3e50;
    }
    </style>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
