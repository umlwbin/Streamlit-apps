import streamlit as st
import plotly.express as px
import numpy as np


def plot_comparison(df, var):
    """
    Plot St. Laurent vs ECCC comparison for a selected variable.
    Mirrors the original app's comparison logic.
    """

    # ---------------------------------------------------------
    # 1. Variable mapping (StL vs ECCC)
    # ---------------------------------------------------------
    stl_map = {
        "Air Temperature": "Air Temperature_StL",
        "Air Pressure": "Air Pressure_StL",
        "Relative Humidity": "Relative Humidity_StL",
    }

    eccc_map = {
        "Air Temperature": "Air Temperature",
        "Air Pressure": "Station Pressure",
        "Relative Humidity": "Relative Humidity",
    }

    units = {
        "Air Temperature": "(°C)",
        "Air Pressure": "(mb)",
        "Relative Humidity": "(%)",
    }

    short_names = {
        "Air Temperature": "Temp",
        "Air Pressure": "Pres",
        "Relative Humidity": "RH",
    }

    stl_var = stl_map[var]
    eccc_var = eccc_map[var]
    unit = units[var]
    short = short_names[var]

    # ---------------------------------------------------------
    # 2. Clean up values (same as original app)
    # ---------------------------------------------------------
    df = df.copy()
    df[stl_var] = df[stl_var].round(3)

    # Pressure fix: replace 0 with NaN
    if var == "Air Pressure":
        df[eccc_var] = df[eccc_var].replace(0, np.nan)

    # ---------------------------------------------------------
    # 3. Build Plotly figure
    # ---------------------------------------------------------
    fig = px.scatter(
        df,
        x="Datetime",
        y=[stl_var, eccc_var],
        title=f"Average 1‑hour {var} at St. Laurent vs ECCC Oakpoint",
        color_discrete_sequence=px.colors.qualitative.Plotly,
    )

    fig.update_traces(marker={"size": 3})
    fig.update_layout(
        height=550,
        plot_bgcolor="ghostwhite",
        hovermode="x unified",
        xaxis_title="Datetime",
        yaxis_title=f"{var} {unit}",
        font=dict(size=16),  # global font bump
        xaxis=dict(
            title_font=dict(size=18),
            tickfont=dict(size=14),
            showline=True,
            linewidth=0.7,
            linecolor="LightGrey",
            showgrid=True
        ),
        yaxis=dict(
            title_font=dict(size=18),
            tickfont=dict(size=14),
            showline=True,
            linewidth=0.7,
            linecolor="LightGrey",
            showgrid=True
        ),
        legend=dict(
            font=dict(size=16),   # bigger legend text
            title_font=dict(size=18)
        )
    )


    # ---------------------------------------------------------
    # 4. Rename legend entries
    # ---------------------------------------------------------
    fig.data[0].name = f"St.L_{short}"
    fig.data[1].name = f"ECCC_{short}"

    # ---------------------------------------------------------
    # 5. Render
    # ---------------------------------------------------------
    st.plotly_chart(fig)
