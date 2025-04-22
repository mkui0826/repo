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

@st.cache_data
def load_data():
    df = pd.read_csv("air_quality_index.csv")
    df.columns = df.columns.str.strip()
    df.rename(columns={"lat": "Latitude", "lng": "Longitude"}, inplace=True)
    df.dropna(subset=["AQI Value", "Latitude", "Longitude"], inplace=True)
    df["AQI Value"] = pd.to_numeric(df["AQI Value"], errors="coerce")
    df["City"] = df["City"].str.title()
    df["Country"] = df["Country"].str.title()
    return df

def describe_city(city, df):
    city_data = df[df["City"] == city]
    return city_data["AQI Value"].min(), city_data["AQI Value"].max()

def main():
    st.title("World Air Quality Explorer")
    df = load_data()

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

    # Filter: AQI Range
    aqi_min = int(city_df["AQI Value"].min())
    aqi_max = int(city_df["AQI Value"].max())
    aqi_range = st.slider(
        "Select AQI Range", aqi_min, aqi_max, (aqi_min, aqi_max),
        key="aqi_slider"
    )
    filtered_df = city_df[
        (city_df["AQI Value"] >= aqi_range[0]) & 
        (city_df["AQI Value"] <= aqi_range[1])
    ]

    # Charts, Summaries, Labels (same as before)...

if __name__ == "__main__":
    main()
