from dash import html, dcc, Dash
from jupyter_dash import JupyterDash
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
import pycountry


df = pd.read_csv('dataset.csv')


def convert_alpha_2_to_3(alpha_2_code):
    try:
        return pycountry.countries.get(alpha_2=alpha_2_code).alpha_3
    except:
        return None

df['RegionCodeAlpha3'] = df['RegionCode'].apply(convert_alpha_2_to_3)
df = df.dropna(subset=['RegionCodeAlpha3'])


app = Dash(__name__, external_stylesheets=[dbc.themes.SLATE])


app.layout = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                html.H3("Group-02-Final-Dashboard", className="text-center text-light mt-4"),
                width=12
            )
        ),
        dbc.Row(
            dbc.Col(
                html.Div(
                    [
                        "Select a country to analyze: ",
                        dcc.Dropdown(
                            id="state_dropdown",
                            options=[{'label': state, 'value': state} for state in df['RegionName'].unique()],
                            value="Austria",  
                            className="dropdown-select mb-4",  
                            style={
                                'background-color': '#2b2b2b',  
                                'color': '#000000',  
                                'width': '100%'  
                            }
                        ),
                    ],
                    className="text-light"
                ),
                width=12
            )
        ),
        dbc.Row(
            dbc.Col(
                html.Div(
                    [
                        "Filter by RegionCode: ",
                        dcc.Dropdown(
                            id="regioncode_dropdown",
                            options=[{'label': code, 'value': code} for code in df['RegionCodeAlpha3'].unique()],
                            value="AUT", 
                            className="dropdown-select mb-4",  
                            style={
                                'background-color': '#2b2b2b',  
                                'color': '#000000',  
                                'width': '100%'  
                            }
                        ),
                    ],
                    className="text-light"
                ),
                width=12
            )
        ),
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id="visual"), width=6),  
                dbc.Col(dcc.Graph(id="world_map"), width=6)  
            ]
        ),
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id="bar_chart"), width=6), 
                dbc.Col(dcc.Graph(id="donut_plot"), width=6)  
            ]
        )
    ],
    fluid=True
)


@app.callback(
    [
        Output("visual", "figure"), 
        Output("world_map", "figure"), 
        Output("bar_chart", "figure"),
        Output("donut_plot", "figure")
    ],
    [
        Input("state_dropdown", "value"), 
        Input("regioncode_dropdown", "value")
    ]
)
def update_output_div(state, region_code):
    if not state or not region_code:
        raise PreventUpdate


    filtered_df = df.query(f"RegionName == '{state}'")

    
    line_fig = px.line(
        filtered_df,
        x="Time",
        y="NumValue",
        title=f"Confirmed Leptospirosis Cases Over Time in {state}",
        template="plotly_dark",  
        labels={"NumValue": "Confirmed Leptospirosis Cases"}
    )

    
    map_fig = px.choropleth(
        df,
        locations="RegionCodeAlpha3",  
        color="NumValue",              
        hover_name="RegionName",        
        title="Global Overview of Confirmed Leptospirosis Cases",
        template="plotly_dark",         
        color_continuous_scale=px.colors.sequential.Plasma,  
        labels={'NumValue': 'Confirmed Cases'},  
        projection="natural earth"  
    )

    
    filtered_region_df = df.query(f"RegionCodeAlpha3 == '{region_code}'")
    bar_fig = px.bar(
        filtered_region_df,
        x="Time",
        y="NumValue",
        title=f"Leptospirosis Cases Over Time in RegionCode {region_code}",
        template="plotly_dark",  
        labels={"NumValue": "Confirmed Leptospirosis Cases"}
    )

    
    top_5_region_df = df.groupby('RegionCodeAlpha3').sum().nlargest(5, 'NumValue').reset_index()
    donut_fig = px.pie(
        top_5_region_df,
        names="RegionCodeAlpha3",
        values="NumValue",
        title="Top 5 RegionCodes by Confirmed Leptospirosis Cases",
        template="plotly_dark",  
        hole=0.4,  
        labels={"NumValue": "Confirmed Cases"}
    )

    
    donut_fig.update_traces(textposition='inside', textinfo='percent+label')

    
    map_fig.update_layout(
        coloraxis_colorbar=dict(
            title="Confirmed Cases",
            ticks="outside"
        )
    )

    return line_fig, map_fig, bar_fig, donut_fig


if __name__ == "__main__":
    app.run_server(debug=True, port=4819)
