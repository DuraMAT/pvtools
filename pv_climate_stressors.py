# -*- coding: utf-8 -*-
"""

Example page template for the pvtools site

toddkarin

"""

from dash import dash, html, dcc
import dash_bootstrap_components as dbc
# import dash_table
import plotly.colors
import plotly.graph_objs as go
# import plotly.plotly as py
# from flask_caching import Cache
from dash.dependencies import Input, Output, State

import numpy as np
import pvlib
import nsrdbtools
import pandas as pd
# import uuid
# import os
import flask
# import json
# import time
import datetime
import io
import pvtoolslib
import urllib

import pvcz

from app import app

# app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# session_id = str(uuid.uuid4())

layout = dbc.Container([
    html.Hr(),
    html.Div([
        html.H1("Photovoltaic Climate Stressors and Zones"),
    ], style={
        # 'background-color': 'lightblue',
        'width': '100%',
        'padding-left': '10px',
        'padding-right': '10px',
        'textAlign': 'center'}),
    html.Hr(),
    html.H2('Overview'),
    dcc.Markdown("""Environmental stress determines the degradation rates and 
    modes for a solar photovoltaic (PV) system. This page shows environmental 
    stressors for PV. By choosing thresholds on temperature and humidity, 
    we define photovoltaic climate zones (PVCZ), showing which locations are 
    expected to show higher degradation rates for PV. 

    **We would highly appreciate any feedback** (praise, bug reports, 
    suggestions, etc.). Please contact us at pvtools.lbl@gmail.com. 

    """.replace('    ', '')
                 ),

    dbc.Row([
        dbc.Col([
            dbc.Button("Show me more details",
                       id="pvcz-details-button",
                       color='light',
                       n_clicks=0,
                       className="mb-3"),
        ], width=3)

    ], justify='start'),

    dbc.Collapse(
        dbc.Card(dbc.CardBody([
            dcc.Markdown("""

            ### Summary
            The variable definitions and methods are described in 
            a [conference manuscript](https://www.researchgate.net/publication/334401420_Photovoltaic_Degradation_Climate_Zones).
            
            This data is also available as an [open-source python library](https://github.com/toddkarin/pvcz).

            ### Who we are

            We are a collection of national lab researchers funded under the 
            [Durable module materials consortium (DuraMAT)](https://www.duramat.org/). 

            """.format(pvtoolslib.contact_email).replace('    ', '')
                         ),

            dbc.Row([
                dbc.Col(
                    html.Img(
                        src=app.get_asset_url('duramat_logo.png'),
                        style={'height': 50})
                ),
                dbc.Col(
                    html.Img(
                        src=app.get_asset_url('pvlib_logo_horiz.png'),
                        style={'height': 50})
                ),
                dbc.Col(
                    html.Img(
                        src=app.get_asset_url(
                            'LBL_Masterbrand_logo_with_Tagline-01.jpg'),
                        style={'height': 50})
                )
            ], justify='center'
            )
        ])), id="pvcz-details-collapse"
    ),
    dbc.Card([
            dbc.CardHeader('Choose Location to lookup stressors'),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        dbc.Label('Latitude'),
                        dbc.Input(id='pvcz-lat', value='37.88', type='text'),
                        dbc.Label('Longitude'),
                        dbc.Input(id='pvcz-lon', value='-122.25', type='text'),
                        # dbc.FormText(id='closest-message',
                        #          children='Closest point shown on map'),
                        # html.P(''),
                        # html.Div([
                        # dbc.Button(id='get-weather', n_clicks=0,
                        #                        children='Show nearest location on map'),
                        #     ]),
                        # html.Div(id='weather_data_download'),

                    ],md=4),
                    dbc.Col([
                        html.Div(id='pvcz-stressors'),
                    ],md=8)
                ]),
            ]),
        ]),
    # html.H2('Simulation Input'),
    html.P(''),
    dbc.Card([
        dbc.CardHeader('PV Climate Stress Maps'),
        dbc.CardBody([
            html.P('Select stressor to plot'),
            dcc.Dropdown(
                id='pvcz-map-select',
                options=pvtoolslib.pvcz_stressor_dropdown_list,
                value='T_equiv_rack_1p1eV',
                style={'max-width': 500}
            ),
            html.P(''),
            dcc.Loading(id="loading-1", children=[html.Div(id="loading-output-1")], type="default"),
            # dcc.Graph(id='pvcz-map')

            ])
        ]),
    html.Div('',style={'min-height': 200}),

    ])

# app.layout = layout


@app.callback(
    Output("loading-output-1", "children"),
    [Input("pvcz-map-select", "value")]
)
def update_pvcz_map(param):
    # return

    #
    # # Tickmode can be auto, linear or array
    # tickmode =


    z = pvtoolslib.pvcz_df[param]

    z = z.astype('float')
    zones = pvcz.get_pvcz_zones()

    print(param)


    if param in ['pvcz','KG_numeric_zone']:
        extra_text = []
        print(zones['zone_spec'])
        zone_spec_df = pd.DataFrame(data={
            'Label': range(len(zones['zone_spec'][param])),
            'Zone': zones['zone_spec'][param]
        })

        extra_text = dbc.Table.from_dataframe(zone_spec_df,
                                 striped=False,
                                 bordered=True,
                                 hover=True,
                                 index=False,
                                 size='sm',
                                 # style={'font-size':'0.8rem'}
                                 ),

        # for s in zones['zone_spec'][param]:
        #     extra_text.append(html.P(s))
        # print(zones['zone_spec']['pvcz'])

    else:
        extra_text = []

    figure = {
        'data': [
            go.Scattermapbox(
                lat=pvtoolslib.pvcz_df['lat'],
                lon=pvtoolslib.pvcz_df['lon'],
                mode='markers',
                marker=dict(
                    color=z,
                    colorscale=[
                        [0, "rgb(150,0,90)"],
                        [0.125, "rgb(0, 0, 200)"],
                        [0.25, "rgb(0, 25, 255)"],
                        [0.375, "rgb(0, 152, 255)"],
                        [0.5, "rgb(44, 255, 150)"],
                        [0.625, "rgb(151, 255, 0)"],
                        [0.75, "rgb(255, 234, 0)"],
                        [0.875, "rgb(255, 111, 0)"],
                        [1, "rgb(255, 0, 0)"]
                    ],
                    size=6,
                    colorbar=dict(
                        # dasf='asdf',
                        title=dict(
                            text=pvtoolslib.pvcz_legend_str[param],
                            side='right'
                        ),
                    )
                ),
                text= param + ': ' + np.round(pvtoolslib.pvcz_df[param], 2).astype(str),
                name='Database location'
            ),
        ],
        'layout': go.Layout(
            autosize=True,
            # width=1000,
            # height=700,
            margin={'l': 10, 'b': 10, 't': 0, 'r': 0},
            hovermode='closest',
            mapbox=dict(
                accesstoken='pk.eyJ1IjoidG9kZGthcmluIiwiYSI6Ik1aSndibmcifQ.hwkbjcZevafx2ApulodXaw',
                bearing=0,
                center=dict(
                    lat=float(40),
                    lon=float(-100)
                ),
                pitch=0,
                zoom=2,
                style='light'
            ),
            legend=dict(
                x=0,
                y=1,
                traceorder='normal',
                font=dict(
                    family='sans-serif',
                    size=12,
                    color='#000'
                ),
                bgcolor='#E2E2E2',
                bordercolor='#FFFFFF',
                borderwidth=2
            )
        )}
    return html.Div([
        dcc.Graph(id='pvcz-map',figure=figure,config=dict(scrollZoom=True)),
        html.P(''),
        html.Div(extra_text)
        ])

@app.callback(
    Output("pvcz-details-collapse", "is_open"),
    [Input("pvcz-details-button", "n_clicks")],
    [State("pvcz-details-collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("pvcz-stressors", "children"),
    [Input("pvcz-lat", 'value'),
     Input('pvcz-lon','value')],
    [],
)
def get_stressors(lat,lon):
    """
    Example for looking up stressors at a particular location.

    """

    # Note df is a flattened list of lat/lon values that only includes those over land
    df = pvcz.get_pvcz_data()

    # Point of interest specified by lat/lon coordinates.
    lat_poi = float(lat)
    lon_poi = float(lon)

    # Find the closest location on land to a point of interest
    closest_index = pvcz.arg_closest_point(lat_poi, lon_poi, df['lat'],
                                           df['lon'])


    first_table_keys = ['lat', 'lon', 'T_equiv_rack_1p1eV','T_equiv_roof_1p1eV',
                        'specific_humidity_mean',
                        'T_velocity_rack',
                        'GHI_mean',
                        'T_ambient_min',
                        'T_ambient_max','T_ambient_mean',
                        'KG_zone',
                        'T_equiv_rack_1p1eV_zone',
                        'T_equiv_roof_1p1eV_zone',
                        'specific_humidity_mean_zone',
                        'pvcz',
                        'pvcz_labeled',
                        'ASCE 7-16 MRI 25-Year',
                        'wind_speed_max']

    detail_table_keys = ['T_equiv_rack_0p1eV', 'T_equiv_rack_0p3eV', 'T_equiv_rack_0p5eV',
       'T_equiv_rack_0p7eV', 'T_equiv_rack_0p9eV', 'T_equiv_rack_1p1eV',
       'T_equiv_rack_1p3eV', 'T_equiv_rack_1p5eV', 'T_equiv_rack_1p7eV',
       'T_equiv_rack_1p9eV', 'T_equiv_rack_2p1eV', 'T_equiv_roof_0p1eV',
       'T_equiv_roof_0p3eV', 'T_equiv_roof_0p5eV', 'T_equiv_roof_0p7eV',
       'T_equiv_roof_0p9eV', 'T_equiv_roof_1p1eV', 'T_equiv_roof_1p3eV',
       'T_equiv_roof_1p5eV', 'T_equiv_roof_1p7eV', 'T_equiv_roof_1p9eV',
       'T_equiv_roof_2p1eV', 'T_velocity_rack', 'T_velocity_roof','wind_speed_rms',
                         'specific_humidity_rms']

    # Get the stressor data from this location
    # location_df = pd.DataFrame(data={'Parameter': [pvtoolslib.pvcz_legend_str[p] for p in df.keys()],
    #                                  'Value': df.iloc[closest_index]})
    location_df = pd.DataFrame(data={'Parameter': [pvtoolslib.pvcz_legend_str[p] for p in first_table_keys],
                                     'Value': df[first_table_keys].iloc[closest_index]})
    for p in ['T_equiv_rack_1p1eV','T_equiv_roof_1p1eV','specific_humidity_mean',
              'T_velocity_rack','GHI_mean','T_ambient_min','T_ambient_max',
              'T_ambient_mean','wind_speed_max','ASCE 7-16 MRI 25-Year']:
        location_df.loc[p,'Value'] = '{:.2f}'.format(location_df['Value'][p])


    detail_df = pd.DataFrame(data={
        'Parameter': [pvtoolslib.pvcz_legend_str[p] for p in detail_table_keys],
        'Value': df[detail_table_keys].iloc[closest_index]})


    for p in detail_df.index:
        detail_df.loc[p,'Value'] = '{:.2f}'.format(detail_df['Value'][p])


    return html.Div([
        dbc.Table.from_dataframe(location_df,
                                 striped=False,
                                 bordered=True,
                                 hover=True,
                                 index=False,
                                 size='sm',
                                 # style={'font-size':'0.8rem'}
                                 ),
        html.Details([
            html.Summary(
                "More stressors"),
            html.Div([
                dbc.Table.from_dataframe(detail_df,
                                         striped=False,
                                         bordered=True,
                                         hover=True,
                                         index=False,
                                         size='sm',
                                         # style={'font-size':'0.8rem'}
                                         ),
            ],style={'marginLeft': 50}
            ),

        ]),
    ])
#
# if __name__ == '__main__':
#     app.run_server(debug=True)