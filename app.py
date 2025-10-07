import pandas as pd
import dash
from dash import html, dcc, Input, Output
import plotly.express as px

# Load dataset
spacex_df = pd.read_csv("spacex_launch_dash.csv")
spacex_df.columns
spacex_df.head()
# Find min and max payload values
max_payload = spacex_df["Payload Mass (kg)"].max()
min_payload = spacex_df["Payload Mass (kg)"].min()

# Create a Dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),

    # Dropdown for Launch Site Selection
    dcc.Dropdown(id='site-dropdown',
                 options=[{'label': 'All Sites', 'value': 'ALL'}] +
                         [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()],
                 value='ALL',
                 placeholder="Select a Launch Site",
                 searchable=True
                 ),
    html.Br(),

    # Pie Chart
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    # Payload Range Slider
    html.P("Payload range (Kg):"),
    dcc.RangeSlider(id='payload-slider',
                    min=min_payload, max=max_payload, step=1000,
                    marks={0: '0', 2500: '2500', 5000: '5000', 7500: '7500', 10000: '10000'},
                    value=[min_payload, max_payload]
                    ),

    # Scatter Chart
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# Callback for Pie Chart
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Count successful launches per site
        success_counts = spacex_df.groupby('Launch Site')['class'].sum().reset_index()
        fig = px.pie(success_counts, values='class', names='Launch Site', 
                     title='Total Successful Launches by Site')
    else:
        # Filter dataframe for selected site
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]

        # Count the number of successful (1) and failed (0) launches
        outcome_counts = filtered_df['class'].value_counts().reset_index()
        outcome_counts.columns = ['class', 'Count']
        outcome_counts['class'] = outcome_counts['class'].map({0: 'Failure', 1: 'Success'})

        fig = px.pie(outcome_counts, values='Count', names='class', 
                     title=f'Success vs Failure for {entered_site}')
    return fig

# Callback for Scatter Chart
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter_chart(entered_site, payload_range):
    # Filter the dataframe for the selected payload range
    filtered_df = spacex_df[(spacex_df["Payload Mass (kg)"] >= payload_range[0]) & 
                            (spacex_df["Payload Mass (kg)"] <= payload_range[1])]
    
    if entered_site != 'ALL':
        # Further filter by selected site
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]

    fig = px.scatter(filtered_df, 
                     x="Payload Mass (kg)", 
                     y='class', 
                     color='Booster Version Category',
                     title=f'Correlation between Payload and Launch Success for {entered_site}',
                     labels={'class': 'Launch Outcome (0=Failure, 1=Success)'},
                     hover_data=['Launch Site'])

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)