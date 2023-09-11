
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, Input, Output, callback

from app import app

# Initialize the app - incorporate css
# external_stylesheets = [dbc.themes.BOOTSTRAP]
# app = Dash(__name__, external_stylesheets=external_stylesheets)

layout = dbc.Container([

    dbc.Row([
        dbc.Col([
            html.H2('About'),
            html.P(
                """PVTOOLS is a set of web applications and 
                python libraries for photovoltaic-specific 
                applications. This work is funded by the Duramat coalition.
                
                """
            )
        ], 
        md=4, 
        # width=4
        ),

        dbc.Col([

            html.H2([
                "IV Curve Correction Tool ",
                dbc.Badge("New!", color="success")]
            ),
            html.P(
                """ Tools for IV curve correction based on IEC 60891:2021 procedures and Pdynamic for healthy or degraded PV modules
                """
            ),
            html.Div([
                html.A( dbc.Button("Launch Tool", color="secondary"),
                        href='iv-curve-correction-tool'
                        )
            ]),
            html.P(""),
            html.A(
                html.Img(
                    src=app.get_asset_url(
                        'ivcorrection.png'),
                    style={'width': '70%'}),
                href='iv-curve-correction-tool'
            ),

            html.P(""),

            html.H2(["String Length Calculator "]),
            html.P(
                """The string length calculator is an industry 
                standard tool for calculating the maximum string 
                length for a PV system in a given location.  
            
                """
            ),
            html.Div([
                html.A( dbc.Button("Launch Tool", color="secondary"),
                    href='string-length-calculator'
                    )
            ]),

            html.A(
                html.Img(
                    src=app.get_asset_url(
                        'string_length_screenshot.png'),
                    style={'width': '70%'}),
                href='string-length-calculator'
            ),

            html.H2([
                "Photovoltaic Climate Zones "]
            ),
            html.P(
                """Explore the geographic distribution of 
                environmental stress on solar photovoltaics. 
                """
            ),
            html.Div([
                html.A( dbc.Button("Launch Tool", color="secondary"),
                        href='string-length-calculator'
                        )
            ]),
            html.P(""),
            html.A(
                html.Img(
                    src=app.get_asset_url(
                        'pvcz_screenshow2.jpg'),
                    style={'width': '70%'}),
                href='pv-climate-stressors'
            ),

            html.P(''),
            html.P(''),
        ], 
        ),
            
    ]),     
])



if __name__ == "__main__":
    app.layout = html.Div(layout)
    app.run_server()
    # app.run(debug=True)