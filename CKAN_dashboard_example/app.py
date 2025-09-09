import streamlit as st
import pandas as pd
import datetime
import pydeck as pdk
import numpy as np
import plotly.express as px
from streamlit_autorefresh import st_autorefresh
import os
import time

# Page config
st.set_page_config(page_title="James Bay CTD Dashboard", layout="wide")

# Refresh every 600 seconds (12 minutes)
#st_autorefresh(interval=720 * 1000, limit=100, key="datarefresh")


t1, t2, t3, t4 =st.tabs(["Introduction","Station Map", "Depth Profiles", " Depth Profile Over Time"])

if st.button("Refresh Data"):
    st.experimental_rerun()


# PULLING UPDATED DATA FILES FROM GITHUB=============================================================================================

@st.cache_data(ttl=720)  # Cache expires every 10 minutes
def load_data():
    return pd.read_csv("2022_ctd.csv")
df_from_github = load_data()



# PULLING CKAN DATA=============================================================================================
@st.cache_data
def load_ctd_data():
    url = "https://canwin-datahub.ad.umanitoba.ca/data/dataset/james-bay-ctd-2022/resource/bb9d964c-4a58-448b-9a9f-51d10c527c79/download/jamesbay_ctd_2022.csv"
    df = pd.read_csv(url)
    return df
df = load_ctd_data()

# Rename columns
df.rename(columns={
    "Depth [salt water, m], using lat = 54.1684": "Depth",
    "Temperature [ITS-90, deg C]": "Temperature",
    "Salinity, Practical [PSU]": "Salinity",
    "Conductivity [mS/cm]": "Conductivity",
    "Latitude In [Degrees North]": "Latitude",
    "Longitude In [Degrees East]": "Longitude",
    "Station": "Station",
    "Timestamp (UTC)": "Timestamp"
}, inplace=True)

# Clean data
df.dropna(subset=["Depth", "Temperature", "Salinity", "Conductivity", "Latitude", "Longitude", "Station", "Timestamp"], inplace=True)
#df["Timestamp"] = pd.to_datetime(df["Timestamp"])

# Sidebar filters
st.sidebar.header("🔍 Filter Data")

stations = df["Station"].unique()
selected_station = st.sidebar.selectbox("Select Station", stations)

min_depth, max_depth = int(df["Depth"].min()), int(df["Depth"].max())

depth_range = st.sidebar.slider("Select Depth Range (m)", min_depth, max_depth, (min_depth, max_depth))

# Ensure Timestamp column is in pandas datetime format
df["Timestamp"] = pd.to_datetime(df["Timestamp"], utc=True)
df["TimestampStr"] = df["Timestamp"].dt.strftime("%Y-%m-%d %H:%M")

# Get min and max directly as pandas Timestamps
min_time = df["Timestamp"].min()
max_time = df["Timestamp"].max()

# Use pandas Timestamps in the slider
selected_time = st.sidebar.slider(
    "Select Time Range",
    min_value=min_time,
    max_value=max_time,
    value=(min_time.to_pydatetime(), max_time.to_pydatetime()),
    format="YYYY-MM-DD HH:mm"
)

selected_time_utc = (
    selected_time[0].replace(tzinfo=datetime.timezone.utc),
    selected_time[1].replace(tzinfo=datetime.timezone.utc)
)

# Filtered data
filtered_df = df[
    (df["Station"] == selected_station) &
    (df["Depth"] >= depth_range[0]) &
    (df["Depth"] <= depth_range[1]) &
    (df["Timestamp"] >= selected_time_utc[0]) &
    (df["Timestamp"] <= selected_time_utc[1])
]


with t1:


    # Title and intro
    st.title("🌊 James Bay CTD 2022 Dashboard")
    st.markdown("""
    This dashboard visualizes oceanographic measurements collected using a CTD (Conductivity, Temperature, Depth) instrument in James Bay, 2022.

    A CTD is a key tool in oceanography that measures how water properties change with depth. Temperature and salinity influence water density, which drives ocean circulation and affects marine ecosystems.
    """)

    # # Interpretation
    # st.subheader("🔬 More about CTDs")
    # st.markdown("""
    # The CTD instrument provides a vertical profile of the water column:

    # - **Temperature** typically decreases with depth, indicating thermal stratification.
    # - **Salinity** can vary due to freshwater input from rivers or ice melt, especially near the surface.
    # - **Conductivity** reflects salinity and temperature, helping infer water mass characteristics.

    # In James Bay, surface waters may be fresher due to river discharge, while deeper layers are colder and more saline. This stratification influences nutrient mixing, biological productivity, and carbon cycling.

    # By comparing stations over time, we can detect seasonal changes, freshwater plumes, or mixing zones—critical for understanding climate impacts in sub-Arctic marine environments.
    # """)

    # Footer
    st.markdown("📁 [Dataset Source - CanWIN](https://canwin-datahub.ad.umanitoba.ca/data/dataset/james-bay-ctd-2022)")
    st.markdown("---")


    st.subheader("📊 Latest Data From Github")
    st.markdown('Data is being updated every 12 minutes')

    csv_path = "2022_ctd.csv"
    # Get last modified time
    last_modified = datetime.datetime.fromtimestamp(os.path.getmtime(csv_path))

    # Calculate next update (10 minutes later)
    next_update = last_modified + datetime.timedelta(minutes=12)

    st.markdown("### ⏱️ Update Info")
    st.write(f"**Last updated:** {last_modified.strftime('%Y-%m-%d %H:%M:%S')}")
    st.write(f"**Next update expected:** {next_update.strftime('%Y-%m-%d %H:%M:%S')}")

    st. dataframe(df_from_github)



with t2:
    st.subheader("📍 CTD Station Map")

    # Spinner while loading
    with st.spinner("Loading interactive map..."):
        # Prepare data
        map_df = df[["Latitude", "Longitude", "Station", "Timestamp"]].dropna().copy()

        # Convert Timestamp to string for tooltip
        map_df["Timestamp"] = pd.to_datetime(map_df["Timestamp"])
        map_df["TimestampStr"] = map_df["Timestamp"].dt.strftime("%Y-%m-%d %H:%M")

        # Assign unique color per station
        stations = map_df["Station"].unique()
        color_map = {station: list(np.random.randint(50, 255, size=3)) for station in stations}
        map_df["Color"] = map_df["Station"].map(color_map)

        # Ensure all columns are basic types
        map_df["Latitude"] = map_df["Latitude"].astype(float)
        map_df["Longitude"] = map_df["Longitude"].astype(float)
        map_df["Station"] = map_df["Station"].astype(str)
        map_df["TimestampStr"] = map_df["TimestampStr"].astype(str)
        map_df["Color"] = map_df["Color"].apply(lambda x: list(map(int, x)))



        # Create PyDeck layer
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=map_df,
            get_position=["Longitude", "Latitude"],
            get_radius=5000,
            get_color="Color",
            pickable=True,
            auto_highlight=True
        )

        # Define tooltip
        tooltip = {
            "html": "<b>Station:</b> {Station}<br><b>Lat:</b> {Latitude}<br><b>Lon:</b> {Longitude}<br><b>Time:</b> {TimestampStr}",
            "style": {"backgroundColor": "steelblue", "color": "white"}
        }

        # Set view
        view_state = pdk.ViewState(
            latitude=map_df["Latitude"].mean(),
            longitude=map_df["Longitude"].mean(),
            zoom=5,
            pitch=0
        )

        # Render map
        st.pydeck_chart(pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip=tooltip
        ))



with t3:
    # Depth profiles
    st.subheader("📊 Interactive Depth Profiles")
    st.caption(f"Available data from {df['Timestamp'].min().strftime('%Y-%m-%d')} to {df['Timestamp'].max().strftime('%Y-%m-%d')}")

    # Use filtered_df from your sidebar filters
    if filtered_df.empty:
        st.warning("⚠️ No data available for the selected time and depth range.")
    else:
        # Temperature vs Depth
        fig_temp = px.scatter(
            filtered_df,
            x="Temperature",
            y="Depth",
            color="Station",
            hover_data=["Timestamp", "Salinity", "Conductivity"],
            title="Temperature vs Depth",
            labels={"Depth": "Depth (m)", "Temperature": "Temperature (°C)"}
        )
        fig_temp.update_yaxes(autorange="reversed")
        st.plotly_chart(fig_temp, use_container_width=True)

        # Salinity vs Depth
        fig_sal = px.scatter(
            filtered_df,
            x="Salinity",
            y="Depth",
            color="Station",
            hover_data=["Timestamp", "Temperature", "Conductivity"],
            title="Salinity vs Depth",
            labels={"Depth": "Depth (m)", "Salinity": "Salinity (PSU)"}
        )
        fig_sal.update_yaxes(autorange="reversed")
        st.plotly_chart(fig_sal, use_container_width=True)

        # Conductivity vs Depth
        fig_cond = px.scatter(
            filtered_df,
            x="Conductivity",
            y="Depth",
            color="Station",
            hover_data=["Timestamp", "Temperature", "Salinity"],
            title="Conductivity vs Depth",
            labels={"Depth": "Depth (m)", "Conductivity": "Conductivity (mS/cm)"}
        )
        fig_cond.update_yaxes(autorange="reversed")
        st.plotly_chart(fig_cond, use_container_width=True)


with t4:
    import plotly.express as px
    st.subheader("🎞️ Animated Depth Profile Over Time")

    # Choose parameter
    animated_param = st.selectbox("Select parameter for animation", ["Temperature", "Salinity", "Conductivity"])

    # Filter for animation (optional: limit to one station)
    animation_df = df[df["Station"] == selected_station]

    fig = px.scatter(
        animation_df,
        x=animated_param,
        y="Depth",
        animation_frame="Timestamp",
        range_y=[animation_df["Depth"].max(), animation_df["Depth"].min()],
        color="Station",
        title=f"{animated_param} vs Depth Over Time",
        labels={"Depth": "Depth (m)", animated_param: animated_param}
    )
    st.plotly_chart(fig)

