import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from datetime import date, timedelta
from api_utils import fetch_weather
from assistant import generate_ski_report
from resorts import resorts
import numpy as np
import plotly.express as px
import pandas as pd

# Initialize Dash app
app = dash.Dash(__name__)
server = app.server  # For deployment if needed

# Layout
app.layout = html.Div(
    style={
        "backgroundColor": "#e6f2ff",
        "fontFamily": "Arial, sans-serif",
        "padding": "40px",
        "minHeight": "100vh"
    },
    children=[
        html.H1("❄️ Snow Forecast Assistant", style={"textAlign": "center", "color": "#004080"}),

        html.Div([
            html.Label("Choose a ski resort:", style={"color": "#003366", "fontWeight": "bold"}),
            dcc.Dropdown(
                id='resort-dropdown',
                options=[{"label": name, "value": name} for name in resorts.keys()],
                value=["Baqueira Beret (Spain)", "Grandvalira (Andorra)"],
                multi=True,
                style={"marginBottom": "20px"}
            ),

            html.Label("Select a date:", style={"color": "#003366", "fontWeight": "bold"}),
            dcc.DatePickerRange(
                id='date-range-picker',
                min_date_allowed=date.today() - timedelta(days=4),
                max_date_allowed=date.today() + timedelta(days=4),
                start_date=date.today() - timedelta(days=2),
                end_date=date.today() + timedelta(days=2),
                style={"marginBottom": "20px"}
            ),

            html.Button("Check Snow Conditions", id='submit-btn', n_clicks=0,
                        style={
                            "backgroundColor": "#0099cc",
                            "color": "white",
                            "border": "none",
                            "padding": "10px 20px",
                            "cursor": "pointer",
                            "fontWeight": "bold",
                            "borderRadius": "5px"
                        })
        ], style={"maxWidth": "600px", "margin": "0 auto"}),

        html.Div(id='report-output', style={
            "marginTop": "40px",
            "backgroundColor": "white",
            "padding": "20px",
            "borderRadius": "10px",
            "boxShadow": "0 0 10px rgba(0,0,0,0.1)",
            "color": "#003366",
            "whiteSpace": "pre-line",
            "maxWidth": "700px",
            "marginLeft": "auto",
            "marginRight": "auto"
        })
    ]
)

# Callback
@app.callback(
    Output('report-output', 'children'),
    Input('submit-btn', 'n_clicks'),
    Input('resort-dropdown', 'value'),
    Input('date-range-picker', 'start_date'),
    Input('date-range-picker', 'end_date')
)
def update_output(n_clicks, resort_list, start_date, end_date):
    if n_clicks == 0 or not resort_list:
        return ""

    data = []
    reports = []

    for resort_name in resort_list:
        coords = resorts[resort_name]
        forecast = fetch_weather(coords["lat"], coords["lon"], start_date, end_date)

        try:
            snowfall = forecast["hourly"]["snowfall"]
            temperature = forecast["hourly"]["temperature_2m"]
            wind = forecast["hourly"]["windspeed_10m"]

            snowfall_sum = round(np.sum(snowfall), 1)
            avg_temp = round(np.mean(temperature), 1)
            avg_wind = round(np.mean(wind), 1)

            report = generate_ski_report(resort_name, f"{start_date} to {end_date}",
                                         snowfall_sum, avg_temp, avg_wind)
            reports.append(f"🏔️ {resort_name}:\n{report}\n")

            # Add to data list for chart
            data.append({"Resort": resort_name, "Feature": "Snowfall (cm)", "Value": snowfall_sum})
            data.append({"Resort": resort_name, "Feature": "Avg Temp (°C)", "Value": avg_temp})
            data.append({"Resort": resort_name, "Feature": "Avg Wind (km/h)", "Value": avg_wind})

        except Exception as e:
            reports.append(f"❌ {resort_name}: Error retrieving data: {e}")

    # Create comparison chart
    df = pd.DataFrame(data)
    fig = px.bar(df, x="Resort", y="Value", color="Feature", barmode="group",
                 title="🏔️ Resort Conditions Comparison")

    return html.Div([
        html.Div("\n\n".join(reports), style={"marginBottom": "40px"}),
        dcc.Graph(figure=fig)
    ])
# Run the app
if __name__ == '__main__':
    app.run(debug=True)