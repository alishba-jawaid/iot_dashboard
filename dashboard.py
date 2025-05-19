import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import requests
import pandas as pd
import plotly.express as px

API_URL = "http://localhost:8000/devices"  # Update if needed

app = dash.Dash(__name__)
app.title = "IoT Device Health Dashboard"

def fetch_data():
    try:
        r = requests.get(API_URL)
        r.raise_for_status()
        data = r.json()
        return pd.DataFrame(data)
    except Exception as e:
        print("Error fetching data:", e)
        return pd.DataFrame()

app.layout = html.Div([
    html.H1("IoT Device Health Dashboard"),
    dcc.Interval(id='interval', interval=10*1000, n_intervals=0),  # 10 seconds
    html.Div(id='live-update-table'),
    dcc.Graph(id='battery-graph'),
    dcc.Graph(id='error-rate-graph')
])

@app.callback(
    [Output('live-update-table', 'children'),
     Output('battery-graph', 'figure'),
     Output('error-rate-graph', 'figure')],
    [Input('interval', 'n_intervals')]
)
def update_dashboard(n):
    df = fetch_data()
    if df.empty:
        return html.Div("No data"), {}, {}

    # DataTable
    table = dash_table.DataTable(
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict('records'),
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left', 'padding': '5px'},
        style_header={'fontWeight': 'bold'}
    )

    # Battery Level Graph
    fig_battery = px.bar(
        df, x="device_id", y="battery",
        color="status", title="Battery Level per Device"
    )

    # Error Rate Graph
    fig_error = px.bar(
        df, x="device_id", y="error_rate",
        color="status", title="Error Rate per Device"
    )

    return table, fig_battery, fig_error

if __name__ == "__main__":
    app.run(debug=True)
