import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table, Input, Output, State, ctx
import requests
import pandas as pd
import plotly.express as px

API_URL = "http://localhost:8000/devices"

# Use a dark theme (Cyborg or Darkly, you can try others too)
external_stylesheets = [dbc.themes.CYBORG]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
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

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("IoT Device Health Dashboard", className="mb-2"), width=12)
    ]),
    dbc.Row([
        dbc.Col(html.Div(id="error-alert"), width=12)
    ]),
    dbc.Row([
        dbc.Col(
            dbc.Button(
                "Download Device Table as CSV",
                id="btn_csv",
                color="primary",
                size="lg",
                className="mb-2",
                style={"fontWeight": "bold", "fontSize": "18px", "boxShadow": "0 2px 8px rgba(0,0,0,0.15)"}
            ),
            width="auto"
        ),
        dcc.Download(id="download-dataframe-csv"),
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id='status-filter',
                options=[
                    {'label': s, 'value': s}
                    for s in ['online', 'offline', 'error']
                ],
                multi=True,
                placeholder='Filter by Status'
            ),
        ], width=4),
        dbc.Col([
            dcc.Dropdown(
                id='device-filter',
                options=[],  # To be filled by callback
                multi=True,
                placeholder='Filter by Device'
            ),
        ], width=4),
        dbc.Col([
            dcc.Interval(id='interval', interval=10*1000, n_intervals=0),
        ], width=4)
    ], className="mb-4"),
    dbc.Row([
        dbc.Col(dash_table.DataTable(
            id='live-update-table',
            style_table={'overflowX': 'auto'},
            style_cell={'backgroundColor': '#272B30', 'color': 'white'},
            style_header={'backgroundColor': '#1B1E23', 'color': 'white', 'fontWeight': 'bold'},
            filter_action='native',
            sort_action='native',
            page_size=10
        ), width=12),
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='status-pie'), width=4),
        dbc.Col(dcc.Graph(id='battery-bar'), width=4),
        dbc.Col(dcc.Graph(id='error-bar'), width=4),
    ], className="mb-4"),
], fluid=True)

# Callback for CSV download
@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("btn_csv", "n_clicks"),
    Input('interval', 'n_intervals'),
    State('status-filter', 'value'),
    State('device-filter', 'value'),
    prevent_initial_call=True
)
def download_csv(n_clicks, n, selected_statuses, selected_devices):
    if ctx.triggered_id != "btn_csv":
        return dash.no_update
    df = fetch_data()
    if selected_statuses:
        df = df[df['status'].isin(selected_statuses)]
    if selected_devices:
        df = df[df['device_id'].isin(selected_devices)]
    return dcc.send_data_frame(df.to_csv, "devices.csv")

@app.callback(
    [
        Output('error-alert', 'children'),
        Output('live-update-table', 'data'),
        Output('live-update-table', 'columns'),
        Output('device-filter', 'options'),
        Output('status-pie', 'figure'),
        Output('battery-bar', 'figure'),
        Output('error-bar', 'figure')
    ],
    [
        Input('interval', 'n_intervals'),
        Input('status-filter', 'value'),
        Input('device-filter', 'value')
    ]
)
def update_dashboard(n, selected_statuses, selected_devices):
    df = fetch_data()
    if df.empty:
        return None, [], [], [], {}, {}, {}

    # Filters
    if selected_statuses:
        df = df[df['status'].isin(selected_statuses)]
    if selected_devices:
        df = df[df['device_id'].isin(selected_devices)]

    # Table
    columns = [{"name": i, "id": i} for i in df.columns]
    data = df.to_dict('records')

    # Device filter dropdown options
    device_options = [{'label': device, 'value': device} for device in df['device_id'].unique()]

    # Status Pie Chart
    status_pie = px.pie(df, names='status', title='Device Status Distribution', hole=0.5)
    status_pie.update_layout(paper_bgcolor='#222', plot_bgcolor='#222', font_color='white')

    # Battery Bar
    battery_bar = px.bar(df, x='device_id', y='battery', color='status', title='Battery Level')
    battery_bar.update_layout(paper_bgcolor='#222', plot_bgcolor='#222', font_color='white')

    # Error Rate Bar
    error_bar = px.bar(df, x='device_id', y='error_rate', color='status', title='Error Rate')
    error_bar.update_layout(paper_bgcolor='#222', plot_bgcolor='#222', font_color='white')

    # Detect error devices for alert
    if not df.empty and (df['status'] == 'error').any():
        error_devices = df[df['status'] == 'error']['device_id'].tolist()
        alert = dbc.Alert(
            f"⚠️ Attention: Devices in ERROR state: {', '.join(error_devices)}",
            color="danger",
            dismissable=True,
            className="mb-4",
            style={'fontWeight': 'bold', 'fontSize': '18px'}
        )
    else:
        alert = None

    return alert, data, columns, device_options, status_pie, battery_bar, error_bar

if __name__ == "__main__":
    app.run(debug=True)
