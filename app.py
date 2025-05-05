import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from datetime import date, timedelta
from api_utils import fetch_weather
from assistant import generate_ski_report, generate_multi_resort_report
from resorts import resorts
import numpy as np
import plotly.express as px
import pandas as pd
import dash_leaflet as dl

# Initialize Dash app
app = dash.Dash(__name__)
server = app.server

# --- CLASSIFICATION LOGIC --- #
def classify_ski_day(snowfall_sum, temperature, wind, sunny):
    if snowfall_sum > 30 and temperature < 0:
        if sunny and wind < 10:
            return ("Pow Cuscus", "#add8e6", "🥇")
        elif not sunny and wind < 20:
            return ("Amazing!", "green", "🥈")
    elif snowfall_sum < 10 and temperature < 5 and wind < 20:
        return ("Don't break your skis", "yellow", "🪨")
    elif snowfall_sum == 0 and temperature < 10 and wind < 20:
        return ("Weather for beginners", "red", "🎓")
    else:
        return ("Not Worth it", "gray", "👎")

# --- LAYOUT --- #
app.layout = html.Div(
    style={"backgroundColor": "#e6f2ff", "fontFamily": "Arial, sans-serif", "padding": "40px", "minHeight": "100vh"},
    children=[
        html.H1("❄️ My Freeriding Assistant", style={"textAlign": "center", "color": "#004080"}),

        html.Div([
            html.Label("Initial Exploration of the Weather conditions:", style={"color": "#003366", "fontWeight": "bold"}),
            dl.Map(
                id='ski-map',
                center=[42.5, 1.5],
                zoom=7,
                style={"width": "100%", "height": "500px", "marginBottom": "20px"},
                children=[
                    dl.TileLayer(),
                    dl.LayerGroup(id="resort-markers")
                ]
            ),
            html.Div([
                html.H4(" Legend", style={"marginBottom": "10px", "color": "#004080"}),
                html.Ul([
                    html.Li("🎖️ Grading label (e.g., Pow Cuscus, Amazing!)"),
                    html.Li("❄️ Snowfall over the past 72h"),
                    html.Li("🌡 Average daily temperature"),
                    html.Li("🌬 Average wind speed"),
                ], style={"paddingLeft": "20px", "lineHeight": "1.8", "fontSize": "16px"})
            ], style={
                "backgroundColor": "#ffffff",
                "padding": "15px",
                "borderRadius": "10px",
                "maxWidth": "500px",
                "margin": "0 auto 30px auto",
                "boxShadow": "0 2px 6px rgba(0,0,0,0.1)"
            })
        ]),

        html.Hr(),

        html.Div([
            html.Label("Deep analysis - choose ski resorts:", style={"color": "#003366", "fontWeight": "bold"}),
            dcc.Dropdown(
                id='resort-dropdown',
                options=[{"label": name, "value": name} for name in resorts.keys()],
                value=["Baqueira Beret (Spain)", "Grandvalira (Andorra)"],
                multi=True,
                style={"marginBottom": "20px"}
            ),

            html.Label("Select date range:", style={"color": "#003366", "fontWeight": "bold"}),
            dcc.DatePickerRange(
                id='date-range-picker',
                min_date_allowed=date.today() - timedelta(days=4),
                max_date_allowed=date.today() + timedelta(days=4),
                start_date=date.today() - timedelta(days=2),
                end_date=date.today() + timedelta(days=2),
                style={"marginBottom": "20px"}
            ),

            html.Button("Check Snow Conditions", id='submit-btn', n_clicks=0,
                        style={"backgroundColor": "#0099cc", "color": "white", "border": "none",
                               "padding": "10px 20px", "cursor": "pointer", "fontWeight": "bold",
                               "borderRadius": "5px"})
        ], style={"maxWidth": "700px", "margin": "0 auto"}),

        html.Div(id='report-output', style={"marginTop": "40px"})
    ]
)

# --- CALLBACK: INITIALIZE MAP WITH RESORT MARKERS --- #
@app.callback(
    Output("resort-markers", "children"),
    Input("ski-map", "id")
)
def init_map(_):
    markers = []
    today = date.today()
    start_date = (today - timedelta(days=3)).isoformat()
    end_date = today.isoformat()

    for name, coords in resorts.items():
        forecast = fetch_weather(coords["lat"], coords["lon"], start_date, end_date)

        try:
            snowfall = forecast["hourly"]["snowfall"]
            temperature = forecast["hourly"]["temperature_2m"]
            wind = forecast["hourly"]["windspeed_10m"]
            weathercode = forecast["hourly"].get("weathercode", [0]*len(temperature))

            snowfall_sum = round(np.sum(snowfall), 1)
            avg_temp = round(np.mean(temperature), 1)
            avg_wind = round(np.mean(wind), 1)
            sunny = weathercode[-1] in [0, 1]
            label, color, badge = classify_ski_day(snowfall_sum, avg_temp, avg_wind, sunny)

            popup_html = html.Div([
                html.H4(f"{badge} {name}", style={"marginBottom": "5px"}),
                html.Div(f"{label}", style={"marginBottom": "10px"}),
                html.Div(f"❄️ Snowfall: {snowfall_sum} cm"),
                html.Div(f"🌡 Temperature: {avg_temp} °C"),
                html.Div(f"🌬 Wind: {avg_wind} km/h")
            ], style={"fontSize": "14px", "lineHeight": "1.6"})

            marker = dl.Marker(
                position=[coords["lat"], coords["lon"]],
                children=dl.Popup(popup_html, maxWidth=250)
            )
            markers.append(marker)
        except:
            continue

    return markers

# --- CALLBACK: LLM REPORT + COMPARISON CHART --- #
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
    resort_data = []

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

            resort_data.append({
                "name": resort_name,
                "snowfall": snowfall_sum,
                "temp": avg_temp,
                "wind": avg_wind
            })

            data.append({"Resort": resort_name, "Feature": "Snowfall (cm)", "Value": snowfall_sum})
            data.append({"Resort": resort_name, "Feature": "Avg Temp (°C)", "Value": avg_temp})
            data.append({"Resort": resort_name, "Feature": "Avg Wind (km/h)", "Value": avg_wind})

        except Exception as e:
            reports.append(f"❌ {resort_name}: Error retrieving data: {e}")

    if len(resort_data) == 1:
        r = resort_data[0]
        report_text = generate_ski_report(r["name"], f"{start_date} to {end_date}", r["snowfall"], r["temp"], r["wind"])
    else:
        report_text = generate_multi_resort_report(resort_data, f"{start_date} to {end_date}")

    reports.append(report_text)

    df = pd.DataFrame(data)
    fig = px.bar(df, x="Resort", y="Value", color="Feature", barmode="group",
                 title=" Resort Conditions Comparison")

    return html.Div([
        html.Div("\n\n".join(reports), style={"marginTop": "40px", "whiteSpace": "pre-line"}),
        dcc.Graph(figure=fig)
    ])

if __name__ == '__main__':
    app.run(debug=True)