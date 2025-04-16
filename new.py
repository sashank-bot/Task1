import streamlit as st
import requests
import datetime
import plotly.graph_objects as go

# App Title
st.set_page_config(page_title="Weather Dashboard", layout="wide")
st.title("Weather Dashboard")

# Session state to track if form is submitted
if 'submitted' not in st.session_state:
    st.session_state.submitted = False

if not st.session_state.submitted:
    with st.form("city_form"):
        city_name = st.text_input("Enter city name")
        submitted = st.form_submit_button("Get Weather")
        if submitted:
            if city_name:
                st.session_state.submitted = True
                st.session_state.city = city_name
            else:
                st.warning("Please enter a city name.")

if st.session_state.submitted:
    api_key = "fcec2dbc68a628cab0ba5f1e05d98b5c"
    city_name = st.session_state.city

    # Fetch current weather
    current_url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}&units=metric"
    current_response = requests.get(current_url)

    if current_response.status_code == 200:
        data = current_response.json()
        main = data["main"]
        weather = data["weather"][0]
        wind = data["wind"]

        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.markdown(f"### {weather['main']} {data['name']}, {data['sys']['country']}")
            st.markdown(f"#### {round(main['temp'])}°C")
            st.markdown(f"**{weather['description'].title()}**")

        with col2:
            st.metric("Feels Like", f"{main['feels_like']}°C")
            st.metric("Humidity", f"{main['humidity']}%")

        with col3:
            st.metric("Pressure", f"{main['pressure']} hPa")
            st.metric("Wind Speed", f"{wind['speed']} m/s")

        # Forecast
        forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?q={city_name}&appid={api_key}&units=metric"
        forecast_response = requests.get(forecast_url)

        if forecast_response.status_code == 200:
            forecast_data = forecast_response.json()
            times = []
            temps = []
            precs = []

            for entry in forecast_data["list"][:8]:  # Next 24 hours (8 intervals of 3 hours)
                times.append(entry["dt_txt"])
                temps.append(entry["main"]["temp"])
                precs.append(entry["pop"] * 100)  # Probability of precipitation

            col4, col5 = st.columns(2)

            with col4:
                fig_temp = go.Figure()
                fig_temp.add_trace(go.Scatter(x=times, y=temps, fill='tozeroy', name='Temperature'))
                fig_temp.update_layout(title='Temperatures Today', xaxis_title='Time', yaxis_title='°C')
                st.plotly_chart(fig_temp, use_container_width=True)

            with col5:
                fig_prec = go.Figure()
                fig_prec.add_trace(go.Scatter(x=times, y=precs, name='Precipitation %'))
                fig_prec.update_layout(title='Precipitation Today', xaxis_title='Time', yaxis_title='%')
                st.plotly_chart(fig_prec, use_container_width=True)

        else:
            st.error("Forecast data not available with your API plan.")
    else:
        st.error("City not found. Please enter a valid city name.")
