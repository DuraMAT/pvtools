import os

from dash import dash, html, dcc
import dash_bootstrap_components as dbc

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app = dash.Dash(__name__,
                external_stylesheets=[dbc.themes.BOOTSTRAP],
                meta_tags=[{
                    'name': "google-site-verification",
                    'content': "S1RjgJU6ZoVdko93JeLNEnn5viVxN1cXL2me3LB9J5I",
                }]
                )

server = app.server
server.secret_key = os.environ.get('secret_key', 'secret')

# Allow to set callbacks before setting layout:
app.config['suppress_callback_exceptions']=True
app.title = 'PVTOOLS'

# For google analytics to work:
app.scripts.config.serve_locally = True

# Add meta tag for google search



# app.scripts.append_script({
#     'external_url': 'https://cdn.jsdelivr.net/gh/lppier/lppier.github.io/async_src.js'
# })
# app.scripts.append_script({
#     'external_url': 'https://cdn.jsdelivr.net/gh/lppier/lppier.github.io/gtag.js'
# })

#
# app.config.suppress_callback_exceptions = True
# # app.config.suppress_callback_exceptions = False
# app.css.config.serve_locally = False
# app.scripts.config.serve_locally = False
#



# import test_layout
#
# header = dbc.Container([
#     dbc.Row([
#         dbc.Col([
#             html.Img(
#                 src=app.get_asset_url('LBL_Masterbrand_logo_with_Tagline-01.jpg'),
#                 style={'height': 50})
#             ],width=4),
#         dbc.Col([
#             html.Img(
#                 src=app.get_asset_url('duramat_logo.png'),
#                 style={'height': 50})
#             ],width=4)
#
#         ],justify='between')
# ])
#
# navbar = dbc.NavbarSimple(
#     children=[
#         dbc.DropdownMenu(
#             nav=True,
#             in_navbar=True,
#             label="Tools",
#             children=[
#                 dbc.DropdownMenuItem("String Length Calculator",href='/string-length-calculator'),
#                 dbc.DropdownMenuItem("Photovoltaic Climate Zones"),
#                 dbc.DropdownMenuItem(divider=True),
#                 dbc.DropdownMenuItem("Documentation"),
#             ],
#         ),
#         dbc.NavItem(dbc.NavLink("Contact", href="#")),
#     ],
#     brand="PVTOOLS",
#     brand_href="/",
#     sticky="top",
# )
#
#
#
#
# app.layout = html.Div([
#     dcc.Location(id='url', refresh=False),
#     html.Div(id='page-content',children=[header, navbar, home.layout])
# ])


#
#
# app.layout = html.Div([
#     html.H2('Hello World'),
#     dcc.Dropdown(
#         id='dropdown',
#         options=[{'label': i, 'value': i} for i in ['LA', 'NYC', 'MTL']],
#         value='LA'
#     ),
#     html.Div(id='display-value')
# ])
#
# @app.callback(dash.dependencies.Output('display-value', 'children'),
#               [dash.dependencies.Input('dropdown', 'value')])
# def display_value(value):
#     return 'You have selected "{}"'.format(value)

if __name__ == '__main__':
    app.run_server(debug=True)



# # external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
# # app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
#
# app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
# server = app.server
#
# app.layout = html.Div([
#     html.H2('Hello World')
# ])
#
#
# app.config.suppress_callback_exceptions = True
#
# # app.config.suppress_callback_exceptions = False
# app.css.config.serve_locally = True
# app.scripts.config.serve_locally = False
#
#
# if __name__ == '__main__':
#     app.run_server(debug=True)