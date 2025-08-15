# app.py
import os
import streamlit as st
from utils import (
    geocode_location, get_ip_location,
    fetch_current_weather, fetch_5day_forecast,
)
from datetime import datetime

st.set_page_config(page_title="Weather App - Nisar", layout="centered")

st.markdown("<h1 style='text-align:center'>Weather App</h1>", unsafe_allow_html=True)
st.write("Enter a location (lahore, 54000/zip code, coordinates or landmark).")

col1, col2 = st.columns([3,1])
with col1:
    input_mode = st.selectbox(
        "Choose how to enter location",
        ("City / Town / Landmark", "Zip/Postal Code", "Latitude,Longitude", "Use my approximate location (IP)"),
    )

    if input_mode == "City / Town / Landmark":
        location_input = st.text_input(
            "Enter city, town, or landmark",
            value="Johar Town, Lahore",
            placeholder="Examples: Lahore, Johar Town, Eiffel Tower"
        )
    elif input_mode == "Zip/Postal Code":
        location_input = st.text_input(
            "Enter zip/postal code (optionally '12345,US')",
            value="54000, PK",
            placeholder="Example: 54000, PK"
        )
    elif input_mode == "Latitude,Longitude":
        location_input = st.text_input(
            "Enter coordinates like: 31.5204,74.3587",
            value="31.4678,74.2875",
            placeholder="Example: 31.4678,74.2875 (Johar Town)"
        )
    else:
        location_input = None

DEFAULT_API_KEY = "b5dac7771ab3543126331347f19879d9"  # <-- apni key yahan likho

with col2:
    api_key = st.text_input(
        "OpenWeather API Key",
        value=DEFAULT_API_KEY,
        type="password"
    )
    st.caption("API key is pre-filled for convenience.")

if st.button("Get Weather"):
    if input_mode == "Use my approximate location (IP)":
        lat, lon, display_name = get_ip_location()
        if lat is None:
            st.error("Could not get your IP-based location.")
            st.stop()
    else:
        if not location_input:
            st.error("Please enter a location.")
            st.stop()


        # Geocode the input (city/zip/landmark/coordinates)
        geocode = geocode_location(location_input)
        if geocode is None:
            st.error("Couldn't find that location. Try a different query.")
            st.stop()
        lat, lon, display_name = geocode

    if not api_key:
        st.error("OpenWeather API key required. Get one at https://openweathermap.org/ and set OPENWEATHER_API_KEY.")
        st.stop()

    with st.spinner("Fetching weather..."):
        current = fetch_current_weather(lat, lon, api_key)
        forecast = fetch_5day_forecast(lat, lon, api_key)

    if current is None:
        st.error("Error fetching current weather.")
        st.stop()

    # Show summary
    st.markdown(f"### Weather for **{display_name}**")
    c = current
    icon_url = f"http://openweathermap.org/img/wn/{c['weather'][0]['icon']}@2x.png"
    temp_c = c['main']['temp'] - 273.15
    feels = c['main'].get('feels_like', None)
    feels_c = feels - 273.15 if feels is not None else None
    cols = st.columns([1,3])
    with cols[0]:
        st.image(icon_url, width=96)
    with cols[1]:
        st.markdown(f"**{c['weather'][0]['main']} — {c['weather'][0]['description'].title()}**")
        st.write(f"Temperature: **{temp_c:.1f}°C**")
        if feels_c:
            st.write(f"Feels like: **{feels_c:.1f}°C**")
        st.write(f"Humidity: {c['main']['humidity']}%")
        st.write(f"Wind: {c['wind'].get('speed', '?')} m/s")

    # 5-day forecast (grouped by day)
    if forecast:
        st.markdown("### 5-day forecast")
        # forecast is list of 3-hour entries; we'll summarize each day (min/max)
        days = {}
        for entry in forecast.get("list", []):
            dt = datetime.fromtimestamp(entry["dt"])
            day = dt.strftime("%a %d %b")
            temp = entry["main"]["temp"] - 273.15
            desc = entry["weather"][0]["description"]
            icon = entry["weather"][0]["icon"]
            if day not in days:
                days[day] = {"temps": [], "icons": [], "descs": []}
            days[day]["temps"].append(temp)
            days[day]["icons"].append(icon)
            days[day]["descs"].append(desc)

        cols = st.columns(len(days))
        for i, (day, info) in enumerate(days.items()):
            with cols[i]:
                avg_temp = sum(info["temps"]) / len(info["temps"])
                icon = info["icons"][len(info["icons"])//2]
                st.markdown(f"**{day}**")
                st.image(f"http://openweathermap.org/img/wn/{icon}@2x.png", width=64)
                st.write(f"{avg_temp:.1f}°C")
                # show most common desc
                from collections import Counter
                common = Counter(info["descs"]).most_common(1)[0][0]
                st.caption(common.title())

    st.success("Weather loaded ✅")

st.markdown("---")
st.markdown("App built by **Nisar** — for assessment. Info: Product Manager Accelerator (PM Accelerator).")
