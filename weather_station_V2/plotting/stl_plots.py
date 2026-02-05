import streamlit as st
import plotly.express as px
import pandas as pd
from dateutil.relativedelta import relativedelta
from streamlit_card import card


def plot_single_variable(stl_avgs, var):
    """
    Plot a single St. Laurent variable with summary cards and a scatter plot.
    Mirrors the original app's visualization logic.
    """

    # ---------------------------------------------------------
    # 1. Extract max/min/most recent values
    # ---------------------------------------------------------
    max_row = stl_avgs.loc[stl_avgs[var].idxmax()]
    min_row = stl_avgs.loc[stl_avgs[var].idxmin()]
    recent_row = stl_avgs.loc[stl_avgs['Datetime'].idxmax()]

    max_val = max_row[var]
    max_date = max_row['Datetime'].strftime('%B %d, %Y')

    min_val = min_row[var]
    min_date = min_row['Datetime'].strftime('%B %d, %Y')

    recent_date = recent_row['Datetime']
    recent_val = recent_row[var]

    # One year ago
    year_ago_date = recent_date - relativedelta(years=1)
    year_ago_val = None
    if year_ago_date in stl_avgs['Datetime'].tolist():
        year_ago_val = stl_avgs.loc[stl_avgs['Datetime'] == year_ago_date, var].iloc[0]

    # ---------------------------------------------------------
    # 2. Determine variable metadata (units, icons, colors)
    # ---------------------------------------------------------
    if "temp" in var.lower():
        varname = var.replace("_StL", "")
        unit = "°C"
        color = "red"
        icon_max, icon_min, icon_today = "🔥", "🥶", "🌡️"

    elif "Precipitation" in var:
        varname = var.replace("_StL", "")
        unit = "mm"
        color = "green"
        icon_max, icon_min, icon_today = "⛈️", "🌤️", "🌧️"

    elif "Pressure" in var:
        varname = var.replace("_StL", "")
        unit = "mb"
        color = "mediumvioletred"
        icon_max, icon_min, icon_today = "👆🏼", "👇🏼", "🌎"

    elif "Humidity" in var:
        varname = var.replace("_StL", "")
        unit = "%"
        color = "orange"
        icon_max, icon_min, icon_today = "😰", "🥵", "💧"

    elif "Wind Speed" in var:
        varname = var.replace("_StL", "")
        unit = " km/hr"
        color = "royalblue"
        icon_max, icon_min, icon_today = "🍃🍃", "🍃", "💨"

    else:
        varname = var
        unit = ""
        color = "blue"
        icon_max = icon_min = icon_today = "📈"

    # ---------------------------------------------------------
    # 3. Summary cards
    # ---------------------------------------------------------
    left, right = st.columns(2)

    with left:
        card(
            title=f"{icon_max} Max {varname}",
            text=f"The highest {varname} was {round(max_val)} {unit} on {max_date}.",
            styles=_card_style()
        )

    with right:
        card(
            title=f"{icon_min} Min {varname}",
            text=f"The lowest {varname} was {round(min_val)} {unit} on {min_date}.",
            styles=_card_style()
        )

    # Today's value + last year
    left, right = st.columns(2)

    with left:
        card(
            title=f"{icon_today} Today's {varname}",
            text=f"The {varname} for today, {recent_date.strftime('%B %d, %Y')} "
                 f"is {round(recent_val)} {unit}.",
            styles=_card_style()
        )

    with right:
        if year_ago_val is not None:
            card(
                title=f"{icon_today} {varname} this time last year",
                text=f"On {year_ago_date.strftime('%B %d, %Y')}, "
                     f"the {varname} was {round(year_ago_val)} {unit}.",
                styles=_card_style()
            )
        else:
            st.info("No data available for this time last year.")

    # ---------------------------------------------------------
    # 4. Plotly scatter plot
    # ---------------------------------------------------------
    fig = px.scatter(
        stl_avgs,
        x="Datetime",
        y=var,
        title=f"Average 1‑hour {varname} at St. Laurent",
    )

    fig.update_traces(marker={"size": 3, "color": color})
    fig.update_layout(
        height=500,
        plot_bgcolor="ghostwhite",
        xaxis_title="Datetime",
        yaxis_title=varname,
        font=dict(size=16),  # overall font size bump
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
    )


    st.plotly_chart(fig)


# ---------------------------------------------------------
# Helper: card styling
# ---------------------------------------------------------
def _card_style():
    return {
        "card": {
            "width": "100%",
            "height": "150px",
            "box-shadow": "0 0 10px rgba(0,0,0,0.5)",
            "margin": "20px 0px 0px 0px",
            "border-radius": "20px",
        },
        "text": {
            "font-family": "inherit",
            "font-weight": "normal",
            "color": "black",
        },
        "title": {
            "font-weight": "normal",
            "color": "black",
            "font-size": 20,
        },
        "filter": {
            "background-color": "rgba(0, 0, 0, 0)"
        }
    }
