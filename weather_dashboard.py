import requests
import streamlit as st
import pandas as pd
from datetime import datetime

def get_coordinates(city_name):
    try:
        response = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1&language=en&format=json")
        response.raise_for_status()
        results = response.json().get("results")
        if results:
            location = results[0]
            return float(location['latitude']), float(location['longitude'])
        else:
            st.warning("City not found. Try adding the country name (e.g., 'Lucknow, India').")
            return None, None
    except Exception as e:
        st.error("Error fetching coordinates. Please check your input or try again later.")
        st.exception(e)
        return None, None


def get_weather_data(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        st.error("Failed to retrieve weather data.")
        return None

st.title("Real-Time Weather Dashboard 🌤️")
st.write("Get live weather updates and forecasts.")

city_name = st.text_input("Enter City Name", value="San Francisco")
forecast_duration = st.slider("Select forecast duration (hours)", min_value=12, max_value=48, value=24, step=12)
parameter_options = st.multiselect(
    "Choose weather parameters to display:",
    options=["Temperature (°C)", "Humidity (%)", "Wind Speed (m/s)"],
    default=["Temperature (°C)", "Humidity (%)"]
)

if st.button("Get Weather Data"):
    with st.spinner("Fetching weather data..."):
        lat, lon = get_coordinates(city_name)
        if lat and lon:
            data = get_weather_data(lat, lon)
            if data:
                # Extract current weather data
                current_data = data.get("current_weather", {})
                hourly_data = data.get("hourly", {})

                if current_data:
                    st.subheader("Current Weather Summary")
                    col1, col2, col3 = st.columns(3)
                    col1.metric("🌡️ Temperature", f"{current_data['temperature']}°C")
                    
                    # Fetch the first available humidity from hourly data
                    first_humidity = hourly_data.get("relative_humidity_2m", [None])[0]
                    col2.metric("💧 Humidity", f"{first_humidity}%" if first_humidity is not None else "Data not available")

                    col3.metric("🌬️ Wind Speed", f"{current_data['windspeed']} m/s")

                # Filter hourly data for the requested duration
                df = pd.DataFrame({"Time": hourly_data['time'][:forecast_duration]})
                df['Time'] = pd.to_datetime(df['Time'])

                if "Temperature (°C)" in parameter_options:
                    df["Temperature (°C)"] = hourly_data['temperature_2m'][:forecast_duration]
                    st.subheader("Temperature Forecast")
                    st.line_chart(df.set_index("Time")["Temperature (°C)"])

                if "Humidity (%)" in parameter_options:
                    if 'relative_humidity_2m' in hourly_data:
                        df["Humidity (%)"] = hourly_data['relative_humidity_2m'][:forecast_duration]
                        st.subheader("Humidity Forecast")
                        st.line_chart(df.set_index("Time")["Humidity (%)"])
                    else:
                        st.warning("Humidity data not available for this location.")

                if "Wind Speed (m/s)" in parameter_options:
                    df["Wind Speed (m/s)"] = hourly_data['wind_speed_10m'][:forecast_duration]
                    st.subheader("Wind Speed Forecast")
                    st.line_chart(df.set_index("Time")["Wind Speed (m/s)"])

                st.success("Weather data retrieved successfully.")