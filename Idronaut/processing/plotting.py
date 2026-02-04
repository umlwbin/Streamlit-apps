import pandas as pd
import plotly.express as px

# ============================================================
# 3. PLOTTING FUNCTIONS
# ============================================================
def plot_pressure_vs_row(df):
    """
    Create a scatter plot of Pressure vs. Row Index.

    Why this plot?
      - It helps the curator visually identify the downcast portion
      - Pressure increases during the downcast, then decreases on the upcast
      - The row index is simply the row number in the file

    Returns:
      A Plotly figure that Streamlit can display.
    """
    fig = px.scatter(df, x=df.index, y="Pres")
    fig.update_layout(
        yaxis_title="Pressure (dbar)",
        xaxis_title="Row Index",
        height=450,
        yaxis=dict(autorange="reversed")  # Pressure increases downward
    )
    return fig


def plot_temp_vs_pressure(df):
    """
    Create a scatter plot of Temperature vs. Pressure.

    Why this plot?
      - It gives the curator a quick preview of the downcast shape
      - Helps confirm that the selected rows look reasonable

    Returns:
      A Plotly figure.
    """
    fig = px.scatter(df, x="Temp", y="Pres")
    fig.update_layout(
        yaxis_title="Pressure (dbar)",
        xaxis_title="Temperature (°C)",
        height=450,
        yaxis=dict(autorange="reversed")
    )
    return fig