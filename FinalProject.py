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
import pydeck as pdk  # for interactive map

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

def main():
    df = load_data()
    st.title("World Air Quality Explorer")

    # Country filter
    country = st.selectbox(
        "Select a Country",
        sorted(df["Country"].dropna().astype(str).unique()),
        key="country_select"
    )
    country_df = df[df["Country"] == country].copy()

    # City filter
    city = st.selectbox(
        "Select a City",
        sorted(country_df["City"].dropna().astype(str).unique()),
        key="city_select"
    )
    city_df = country_df[country_df["City"] == city].copy()

    # Chart 1: AQI Category counts
    st.subheader(f"AQI Category Breakdown - {country}")
    category_counts = country_df["AQI Category"].value_counts()
    fig1, ax1 = plt.subplots()
    ax1.bar(category_counts.index, category_counts.values, color="skyblue")
    ax1.set_xlabel("AQI Category")
    ax1.set_ylabel("AQI Readings")
    ax1.set_title(f"AQI Categories in {country}")
    st.pyplot(fig1)

    # Chart 2: Average AQI by city
    st.subheader(f"Average AQI by City in {country}")
    avg_aqi_by_city = country_df.groupby("City")["AQI Value"].mean().sort_values()
    fig2, ax2 = plt.subplots(figsize=(10, 4))
    ax2.bar(avg_aqi_by_city.index, avg_aqi_by_city.values, color="coral")
    ax2.set_xticks(range(len(avg_aqi_by_city)))
    ax2.set_xticklabels(avg_aqi_by_city.index, rotation=45, ha='right')
    ax2.set_ylabel("Average AQI")
    st.pyplot(fig2)

    # AQI Summary
    st.subheader(f"AQI Summary for {country}")
    min_aqi = country_df["AQI Value"].min()
    max_aqi = country_df["AQI Value"].max()
    avg_aqi = country_df["AQI Value"].mean()
    st.markdown(f"- Minimum AQI: **{min_aqi}**")
    st.markdown(f"- Maximum AQI: **{max_aqi}**")
    st.markdown(f"- Average AQI: **{round(avg_aqi, 2)}**")

    # Top AQI Records
    st.subheader("Top 5 AQI Readings in City")
    st.dataframe(city_df.sort_values("AQI Value", ascending=False).head(5))

    # AQI Rating labels
    city_df["AQI Rating"] = np.where(
        city_df["AQI Value"] < 50, "Good",
        np.where(city_df["AQI Value"] < 100, "Moderate",
                 np.where(city_df["AQI Value"] < 150, "Unhealthy", "Very Unhealthy"))
    )

    st.subheader("Sample Classified Records")
    for _, row in city_df.head(3).iterrows():
        st.write(f"{row['City']} - AQI {row['AQI Value']} ({row['AQI Rating']})")

    # --- AQI Map using pydeck ---
    st.subheader(f"Air Quality Map for {country}")
    country_df = country_df.rename(columns={"AQI Value": "AQI_Value"})

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=country_df,
        get_position='[Longitude, Latitude]',
        get_color='[255, 140 - AQI_Value, 0, 160]',
        get_radius=20000,
        pickable=True
    )

    view_state = pdk.ViewState(
        latitude=country_df["Latitude"].mean(),
        longitude=country_df["Longitude"].mean(),
        zoom=4,
        pitch=0
    )

    st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state))

if __name__ == "__main__":
    main()
    
