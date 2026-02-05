import streamlit as st
from weather_station_workflow import load_all_weather_data
from plotting.stl_plots import plot_single_variable
from plotting.compare_plots import plot_comparison
from utils import big_caption


st.set_page_config(page_title="Weather Station Viewer", layout="wide")

with st.sidebar:
    st.title("Weather Station Viewer ⛈️")
    big_caption("View past and current St. Laurent weather station data and compare to Environment and Climate Change Canada stations close by. ")
    st.markdown('')

    with st.expander("About the Weather Keeper Program"):

        st.subheader('The Manitoba Métis Federation (MMF) Weather Keeper Program')
        st.image("img/st-laurent_17060_oct2022.jpeg", width=200)
        st.markdown('''
            The Weather Keeper Program is a collaboration between the Manitoba Métis Federation (MMF) and the Centre for Earth Observation Science (CEOS) at the University of Manitoba, to support the collection of atmospheric data in the Manitoba Great Lakes region. 
            This program is a co-developed, and jointly managed, monitoring network that will provide information on how the Manitoba Great Lakes respond to land-use changes and variability in weather.
            This program also gives insight into the local and regional effects of climate change. 
            The St. Laurent weather station, shown above, is one of the citizen-managed stations that provides current weather conditions in the area.
            
            [Download project data from CanWIN](https://canwin-datahub.ad.umanitoba.ca/data/project/mmf-weather-keeper)

                    ''')

    st.markdown("---")
    st.image("img/mmf.png",width=180)
    st.image("img/UM-EarthObservationScience-cmyk-left.png",width=250)
    
    
# Cache the data load
@st.cache_data
def load_data_cached():
    return load_all_weather_data()

# ---------------------------------------------------------
# Side‑by‑side buttons
# ---------------------------------------------------------
col1, col2 = st.columns(2)

# First-time load
with col1:
    if st.button("Grab all weather station data", type="primary"):
        with st.spinner("Fetching and cleaning weather station data…"):
            data = load_data_cached()

        if data is None:
            st.error("Unable to fetch weather station data. The server may be temporarily unavailable.")
        else:
            st.session_state.data = data

# Reload button (forces a fresh fetch)
with col2:
    if "data" in st.session_state:
        if st.button("Reload data", type="primary"):
            with st.spinner("Refreshing weather station data…"):
                load_data_cached.clear()
                data = load_data_cached()

            if data is None:
                st.error("Unable to refresh data. The server may be temporarily unavailable.")
            else:
                st.session_state.data = data
                st.success("Data reloaded successfully.")


if "data" in st.session_state and st.session_state.data is not None:
    stl, eccc, combined = st.session_state.data

    st.markdown('')
    st.markdown('#### What would you like to do? ✍🏼')
    choice = st.radio(
        "Select one",
        ["-- Select an option --", "Visualize St. Laurent data", "Compare St. Laurent and ECCC"],
        index=0
    )

    if choice == "Visualize St. Laurent data":

        # Filter out non‑plottable columns
        cols = [
            c for c in stl.columns
            if ("date" not in c.lower())
            and ("direction" not in c.lower())
            and ("gust" not in c.lower())
        ]


        st.markdown('')
        st.markdown('#### Choose the variable you would like to plot 📊')
        var = st.selectbox("Select one", cols)

        plot_single_variable(stl, var)


    if choice == "Compare St. Laurent and ECCC":
        st.markdown('')
        st.markdown('#### Choose the variable you would like to compare between the two stations 📊')
        var = st.selectbox("Choose a variable", ["Air Temperature", "Relative Humidity", "Air Pressure"])
        plot_comparison(combined, var)
