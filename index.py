"""
Main page for pvtools website. Run this script to start.

10/09/2023
toddkarin
baojie li

"""

from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc


from app import app

# Line is important for Heroku.w
server = app.server

# Load layouts for different pages
import home, iv_correction_tool, about
import string_length_calculator, pv_climate_stressors


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content',children=[home.layout])
])


header = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.A(
                html.Img(
                    src=app.get_asset_url('LBL_Masterbrand_logo_with_Tagline-01.jpg'),
                    style={'height': 50}),
                href="https://www.lbl.gov/"
            )
            ],width=9),
        dbc.Col([
            html.A(
                html.Img(
                    src=app.get_asset_url('duramat_logo.png'),
                    style={'height': 50}),
                href="https://www.duramat.org/"
            )
            ],width=3)

        ],justify='between')
])

navbar = dbc.NavbarSimple(
    children=[
        dbc.DropdownMenu(
            nav=True,
            in_navbar=True,
            label="Tools",
            children=[
                dbc.DropdownMenuItem("IV Curve Correction Tool",href='/iv-curve-correction-tool'),
                dbc.DropdownMenuItem("String Length Calculator",href='/string-length-calculator'),
                dbc.DropdownMenuItem("Photovoltaic Climate Stressors",href='/pv-climate-stressors'),
            ],
        ),
    ],
    brand="PVTOOLS",
    brand_href="/",
    sticky="top",
)



@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/string-length-calculator':
        body = string_length_calculator.layout
        # body = home.layout
    elif pathname == '/home':
        body = home.layout
    elif pathname == '/pv-climate-stressors':
        body = pv_climate_stressors.layout
        # body = home.layout
    elif pathname == '/iv-curve-correction-tool':
        body = iv_correction_tool.layout
    elif pathname == '/':
        body = home.layout
    else:
        body = '404'

    return [header, navbar, body]

if __name__ == '__main__':
    app.run_server(debug=True)