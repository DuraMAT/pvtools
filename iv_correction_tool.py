from dash import dcc, html, Input, Output, callback, State, dash_table
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import pvlib
import ivcorrection
import ivcorrectionlib
import pandas as pd
import vocmax
import plotly.graph_objs as go
import numpy as np
from plotly.subplots import make_subplots
import plotly.express as px
from plotly.tools import mpl_to_plotly
from matplotlib.colors import LinearSegmentedColormap
import base64
import datetime
import io
import ast
import json

from app import app

# List of modules in the CEC database.
cec_modules = ivcorrectionlib.cec_modules
cec_module_dropdown_list = ivcorrectionlib.cec_module_dropdown_list

ini_color = '#A6A6A6'
select_color = '#0070C0'

layout = dbc.Container([
    html.Hr(),
    html.Div([
        html.H1("IV Curve Correction Tool"),
    ], style={
        # 'background-color': 'lightblue',
        'width': '100%',
        'padding-left': '10px',
        'padding-right': '10px',
        'textAlign': 'center'}),
    html.Hr(),

    html.H2('Overview'),
    html.P(''),
    dbc.Row([
        dbc.Col([
            dcc.Markdown("""This tool realize two functions:
                         * Calculate the IV curve correction coefficients 
                         for the Procecure 1, 2, and 4 of IEC 60891:2021 standard \[1\] 
                         * Performs the correction of IV curves (healthy or degraded) using 
                         Procecure 1, 2, 4 and a proposed Procedure (Pdynamic).

                A python-based package is available: 
                [https://github.com/DuraMAT/IVcorrection](https://github.com/DuraMAT/IVcorrection).

                **We would highly appreciate any feedback** (praise, bug reports, 
                suggestions, etc.). Please contact us at pvtools.duramat@gmail.com. 
                
                """.replace('    ', '')
                 ),
        ], width = 9),

        dbc.Col([
            html.Img(src=app.get_asset_url('ivcorrection_logo.png'),
            style={'width': '100%'}),
        ], width = 3),
    ]),

    dbc.Button(id='details-button',
            n_clicks=0,
            children='More information',
            color="light"),

    dbc.Collapse(
        dbc.Card(
            dbc.CardBody([
                dcc.Markdown("""
            
                ### Summary
                
                The calculation proceeds with the following steps:
                
                - Provide PV module parameters
                - Calculate correction coefficients
                - Correct example I-V curve(s) (optional)
                                
                ### What is I-V curve correction 
                
                I-V curve correction refers to correct the I-V curve measured 
                under different environmental condition to an identical one. 
                Generally, the standard test condition (STC) is adopted as the 
                target condition.
                                
                ### Correction methods
                
                This tool can perform I-V curve correction using Procedure 1, 2, 4 
                of IEC 60891:2021 \[1\] and a proposed Procedure dynamic. 
                The determination of correction coefficients follow the IEC 60891:2021 standard \[1\].
                
                ### Who we are
                
                We are a collection of national lab researchers funded under the 
                [Durable module materials consortium (DuraMAT)](https://www.duramat.org/). 
                                
                """),
                             
                dbc.Row([
                    dbc.Col(
                        html.Img(
                            src=app.get_asset_url('duramat_logo.png'),
                            style={'height': 50})
                    ),
                    dbc.Col(
                        html.Img(
                            src=app.get_asset_url(
                                'LBL_Masterbrand_logo_with_Tagline-01.jpg'),
                            style={'height': 50})
                    )
                ], justify='center')
            
            ])
        ), id="details-collapse"
    ),

    
    html.P(''),
    html.H2('Step 1: Provide PV module parameters'),

    dbc.Card([
        dbc.CardBody([
            dcc.Markdown("""To select module parameters from a library of common 
            modules (CEC database \[2\]), select 'Library Lookup'. Or select 'manual entry' to 
            enter the parameters manually. 
            
            """),
            dbc.Tabs([
                dbc.Tab([
                    dbc.Card(
                        dbc.CardBody([
                            html.H6("Module name (from CEC database)"),
                            dcc.Dropdown(
                                    id='module_name_select',
                                    options=cec_module_dropdown_list,
                                    value=cec_module_dropdown_list[0][
                                        'value'],
                                    style={'max-width': 500}
                                ),
                            dcc.Loading(html.Div(id='figure_iv_datasheet'))
                        ])
                    )
                ], tab_id='lookup', label='Library Lookup'),

                dbc.Tab([
                    dbc.Card(
                        dbc.CardBody([
                            dcc.Markdown("""Manually set the following module and 
                                         single-diode model (SDM) parameters.
                                """),
                            
                            dbc.Row([
                                dbc.Col([

                                    dbc.Label("""Module name"""),
                                    dbc.Input(id='module_name_manual',
                                                value='Custom Module',
                                                type='text',
                                                style={'max-width': 200}),
                                    dbc.FormText("""Module name for outfile"""),
                                    html.P(''),

                                    dbc.Label("""N_cells"""),
                                    dbc.Input(id='N_cells', value='60', type='text',
                                                style={'max-width': 200}),
                                    dbc.FormText('Number of cells of module'),
                                    html.P(''),

                                    dbc.Label("""V_oc_ref"""),
                                    dbc.Input(id='v_oc_ref', value='44.0', type='text',
                                                style={'max-width': 200}),
                                    dbc.FormText('The open-circuit voltage at reference conditions in units of V'),
                                    html.P(''),

                                    dbc.Label("""I_sc_ref"""),
                                    dbc.Input(id='i_sc_ref', value='5.17', type='text',
                                                style={'max-width': 200}),
                                    dbc.FormText('The short-circuit current at reference conditions in units of A'),
                                    html.P(''),

                                    dbc.Label("""alpha_sc"""),
                                    dbc.Input(id='alpha_sc', value='0.0021', type='text',
                                                style={'max-width': 200}),
                                    dbc.FormText('The short-circuit current temperature coefficient in units of A/C'),
                                    html.P(''),

                                    dbc.Label("""beta_oc"""),
                                    dbc.Input(id='beta_oc', value='-0.159', type='text',
                                                style={'max-width': 200}),
                                    dbc.FormText('The open-circuit voltage temperature coefficient in units of V/C'),
                                    html.P('')

                                ]),
                                dbc.Col([

                                    dbc.Label("""I_L_ref"""),
                                    dbc.Input(id='I_L_ref', value='5.18', type='text',
                                                style={'max-width': 200}),
                                    dbc.FormText('The light-generated current (or photocurrent) at reference conditions, in A'),
                                    html.P(''),

                                    dbc.Label("""I_o_ref"""),
                                    dbc.Input(id='I_o_ref', value='1.15e-9', type='text',
                                                style={'max-width': 200}),
                                    dbc.FormText('The dark or diode reverse saturation current at reference conditions, in A'),
                                    html.P(''),

                                    dbc.Label("""R_s"""),
                                    dbc.Input(id='R_s', value='0.317', type='text',
                                                style={'max-width': 200}),
                                    dbc.FormText('The series resistance at reference conditions, in ohms'),
                                    html.P(''),

                                    dbc.Label("""R_sh_ref"""),
                                    dbc.Input(id='R_sh_ref', value='287.1', type='text',
                                                style={'max-width': 200}),
                                    dbc.FormText('The shunt resistance at reference conditions, in ohms'),
                                    html.P(''),

                                    dbc.Label("""a_ref"""),
                                    dbc.Input(id='a_ref', value='1.98', type='text',
                                                style={'max-width': 200}),
                                    dbc.FormText("""The product of the usual diode ideality factor (n, unitless), 
                                                 number of cells in series (Ns),
                                                   and cell thermal voltage at reference conditions, in V"""),
                                    html.P('')
                                    
                                    
                                ])
                            ])
                            
                        ])
                    )
                ], tab_id='manual', label='Manual Entry')
            ], id='module_parameter_input_type', active_tab='lookup')
        ])
    ]),

    html.P(''),
    html.H2('Step 2: Calculate correction coefficients'),

    dbc.Card([
        dbc.CardBody([

            html.P('Press "Calculate" to calculate correction coefficients for the Procedure 1, 2 of IEC 60891:2021'),

            html.Details([
                html.Summary('Detail of the correction coefficients'),
                dcc.Markdown("""
                
                **Procedure 1** requires 2 pre-determined coefficients:
                    * rs: internal series resistance
                    * k: curve correction factor
                            
                **Procedure 2** requires 4 pre-determined coefficients:
                    * rs: internal series resistance
                    * k: curve correction factor
                    * B1, B2: irradiance correction factors
                             
                            
                """.replace('    ', '')),
            ]),

            html.P(''),

            dbc.Button(id='calc-button',
                    n_clicks=0,
                    children='Calculate',
                    color="secondary"),
            
            html.P(''),
            dcc.Loading(html.Div(id='coefficents')),
            dcc.Store(id='results-store'),
               
        ])
    ]),

    html.P(''),
    html.H2('Step 3 : Correct example I-V curve(s) (optional)'),

    dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.H4('Option 1:'),
                    dcc.Markdown('Generate example I-V curves to correct by entering irradiance and temperature:'),
                    dcc.Markdown("Irradiance ($W/m^2$)", mathjax = True),
                    dbc.Input(id='G_manual',
                                value='400,  500,  600,  700,  800,  900, 1000, 1100, 1200',
                                type='text',
                                style={'max-width': 500}),
                    dbc.FormText("""1 or more values (divided by ',') can be entered"""),
                    html.P(''),

                    dcc.Markdown("Module temperature ($^\circ C$)", mathjax = True),
                    dbc.Input(id='Tm_manual',
                                value='20, 26, 32, 38, 44, 50, 56, 62, 68',
                                type='text',
                                style={'max-width': 500}),
                    dbc.FormText("""1 or more values (divided by ',') can be entered.
                                 
                                 Make sure the value number is equal to irradiance value number.
                                 """),
                    html.P(''),

                    dcc.Markdown("Degradation can be included (optional) by selecting the following checkbox:", mathjax = True),

                    dbc.Row([
                        dbc.Col([
                                dcc.Checklist(
                                    id='checkbox_rs',
                                    options=[{'label': ' Rs degradation', 'value': 'checkbox-1'}],
                                    value=[],
                                    style={'color': ini_color}
                                )
                            ], width={"size": 4, "offset": 0}),

                        dbc.Col([
                            dbc.Row([
                                dbc.Col([
                                    dcc.Markdown("$R_{s\_degra} (\Omega)$: ", mathjax = True),
                                ], 
                                width={"size": 6, "offset": 0},
                                id = 'rs_text', 
                                style={'color': ini_color}),

                                dbc.Col([
                                    dbc.Input(id='rs_input', value='0.5', type='text',
                                            style={'max-width': 20}),
                                ]),
                            ]),
                            
                            dbc.FormText('(Value of addtional Rs resistance)', id = 'rs_explain'),

                            html.P('')
                        ], width = 8),

                    ], className="g-0"),

                    dbc.Row([
                        dbc.Col([
                                dcc.Checklist(
                                    id='checkbox_rsh',
                                    options=[{'label': ' Rsh degradation', 'value': 'checkbox-rsh'}],
                                    value=[],
                                    style={'color': ini_color}
                                )
                            ], width={"size": 4, "offset": 0}),

                        dbc.Col([
                            dbc.Row([
                                dbc.Col([
                                    dcc.Markdown("$R_{sh\_degra} (\Omega)$: ", mathjax = True),
                                ], 
                                width={"size": 6, "offset": 0},
                                id = 'rsh_text', 
                                style={'color': ini_color}),

                                dbc.Col([
                                    dbc.Input(id='rsh_input', value='50', type='text',
                                            style={'max-width': 20}),
                                ]),
                            ]),
                            
                            dbc.FormText('(Value of addtional Rsh resistance)', id = 'rsh_explain'),

                            html.P('')
                        ], width = 8),

                    ], className="g-0"),

                    dbc.Row([
                            dcc.Checklist(
                                id='checkbox_re_esti',
                                options=[{'label': ' Re-estimate coefficients for degradation', 
                                          'value': 'checkbox-re_esti'}],
                                value=[],
                                style={'color': ini_color}
                            ),
                            dbc.FormText('(Make coefficients adapted for Rs degrdation)', id = 're_esti_explain'),

                    ], className="g-0"),

                    html.Div(id='new_coeff'),

                    html.Details([
                        html.Summary('Detail of the degradation setting'),
                        dcc.Markdown("""
                        Two types of degradation can be simulated:
                                     
                        **Rs degradation**: Add an additional $R_{s\_degra}$ 
                                     in series to the PV module
                                    
                        **Rsh degradation**: Add an additional $R_{sh\_degra}$ 
                                     in parallel to the PV module
                                    
                        """.replace('    ', ''), mathjax = True),
                    ]),

                    html.P(''),

                    dbc.Button(id='iv_example_button',
                        n_clicks=0,
                        children='Generate and correct I-V curves',
                        color="secondary"),


                    html.P(''),
                    html.Div(id='GT_message'),

                    html.P(''),
                    html.Hr(),
                    html.H4('Option 2:'),
                    dcc.Markdown("Upload your IV curves file below:", mathjax = True),
                    dbc.FormText("""(Excel file xls., contains columns 'G', 'T', 'v', and 'i')
                                 """),
                    html.P(''),
                    html.A('Download example file',
                        href='https://github.com/lbj2011/IVcorrection/blob/main/examples/data/example_data.xlsx'
                        ),

                    dcc.Upload(
                        id='upload-data',
                        children=html.Div([
                            'Drag and Drop or ',
                            html.A('Select a file')
                        ]),
                        style={
                            'width': '100%',
                            'height': '60px',
                            'lineHeight': '60px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign': 'center',
                            'margin': '10px'
                        },
                        # Allow multiple files to be uploaded
                        multiple=True
                    ),
                    html.Div(id='output-data-upload'),
                    html.P(''),

                ], width = 6),

                dbc.Col([
                    dcc.Loading(html.Div(id='iv_example'))
                    
                ], width = 6)

            ]),

            dbc.Row([
                dcc.Loading(html.Div(id='corrected_iv')),
                
            ])

        ])
    ]),

    dbc.Row([
        html.P(''),
        html.P(''),
        html.H4('Frequently Asked Questions'),
        html.Details([
            html.Summary(
                "What if I want to run the correction myself? Where's the source code?"),
            html.Div([
                dcc.Markdown("""If you would like to run the calculation as a 
                python program, please visit the [github page for ivcorrection]( 
                https://github.com/lbj2011/IVcorrection) 

                """)

            ], style={'marginLeft': 50}
            ),

        ]),
        html.Details([
            html.Summary(
                "Where can I find the details of the standard?"),
            html.Div([
                dcc.Markdown("""Please visit the [page of IEC 60891:2021]( 
                    https://webstore.iec.ch/publication/61766) to download the standard.

                    """)
            ], style={'marginLeft': 50}
            ),
        ]),
        html.Details([
            html.Summary(
                "Do you store any of my data?"),
            html.Div([
                dcc.Markdown("""We take your privacy seriously. We do not store 
                any metadata related to the simulation. For understanding the 
                usage of the app, we count the number of times the 'calculate' 
                button is pressed and also record whether default values were 
                used or not. We also count the number of unique users that use 
                the app. We specifically exclude logging any events that generate 
                identifiable metadata. 
                """),
            ], style={'marginLeft': 50}
            ),
        ]),
        html.P(''),
        html.H4('References'),
        html.P("""
            [1] IEC 60891, Photovoltaic devices - Procedures for temperature and 
               irradiance corrections to measured I-V characteristics, 2021.
            """),
        html.P("""
            [2] A. Dobos, “An Improved Coefficient Calculator for the 
            California Energy Commission 6 Parameter Photovoltaic Module Model”, 
            Journal of Solar Energy Engineering, vol 134, 2012. 
            """),
        html.P("""
            [3] C.B. Jones, C.W. Hansen, Single Diode Parameter Extraction from In-Field Photovoltaic I-V Curves 
            on a Single Board Computer, Conference Record of the IEEE Photovoltaic Specialists Conference. (2019) 382–387. 
            """),
        html.P("""
            [4] J.C.H. Phang, D.S.H. Chan, A review of curve fitting error criteria 
                for solar cell I-V characteristics, 
                Solar Cells. 18 (1986) 1-12.
            """),
        html.H4('About'),
        html.P("""Funding was primarily provided as part of the Durable Modules 
        Consortium (DuraMAT), an Energy Materials Network Consortium funded by 
        the U.S. Department of Energy, Office of Energy Efficiency and Renewable 
        Energy, Solar Energy Technologies Office. Lawrence Berkeley National 
        Laboratory is funded by the DOE under award DE-AC02-05CH11231 """),
        html.P('ivcorrection version ' + str(ivcorrectionlib.__version__)), 
        html.P('Author: Baojie Li'),
        html.P('Contact: ' + ivcorrectionlib.contact_email)
    ])
])

@app.callback(Output('figure_iv_datasheet', 'children'),
              [Input('module_name_select', 'value')])

def plot_lookup_IV(module_name):
    """
    Callback for IV curve plotting in setting module parameters.

    Parameters
    ----------
    module_name

    Returns
    -------
    layout_show

    """
    module_parameters = cec_modules[module_name].to_dict()
    module_parameters['name'] = module_name

    info_df = pd.DataFrame.from_dict({
        'Parameter': list(module_parameters.keys())
    })
    info_df['Value'] = info_df['Parameter'].map(module_parameters)

    paras_used = info_df[info_df['Parameter'].isin(
                ['alpha_sc', 'beta_oc', 'V_oc_ref', 'I_sc_ref', 'I_L_ref', 'I_o_ref', 'R_s', 'R_sh_ref' ,'a_ref'])]

    # Calculate some IV curves.
    irradiance_list = [1000, 800, 600, 400, 200]
    iv_curve = []
    for e in irradiance_list:
        ret = vocmax.calculate_iv_curve(e, 25, module_parameters)
        ret['effective_irradiance'] = e
        ret['legend'] = '$ {} \ W/m^2$'.format(e)
        iv_curve.append(ret)

    allc_step1 = get_colorway(irradiance_list)

    return [
        html.P(''),
        dbc.Row([

            dbc.Col([
                dcc.Markdown("""Module parameters needed for IV curve correction
                are shown in the table below. 
                             
                (It is recommended to 
                cross-check these values with the module datasheet provided 
                by the manufacturer. )
                             
                """.replace('    ', '')),
                html.Details([
                html.Summary('View details of these parameters'),
                dcc.Markdown("""
                
                * **V_oc_ref**. The open-circuit voltage at 
                reference conditions in units of V
                             
                * **I_sc_ref**. The short-circuit current at 
                reference conditions in units of A
                             
                * **alpha_sc**. The short-circuit current temperature coefficient in units of A/C
                             
                * **beta_oc**. The open-circuit voltage temperature coefficient in units of V/C
        
                * **a_ref**. The product of the usual diode ideality factor (n, 
                unitless), number of cells in series (Ns), and cell thermal 
                voltage at reference conditions, in units of V
        
                * **I_L_ref**. The light-generated current (or photocurrent) at 
                reference conditions, in A
        
                * **I_o_ref**. The dark or diode reverse saturation current at 
                reference conditions, in A
        
                * **R_sh_ref**. The shunt resistance at reference conditions, 
                in ohms
        
                * **R_s**. The series resistance at reference conditions, in ohms.
                             
                """.replace('    ', '')),
                ]),

                dbc.Table.from_dataframe(paras_used,
                                         striped=False,
                                         bordered=True,
                                         hover=True,
                                         index=False,
                                         size='sm',
                                         style={'font-size': '1rem'})

            ], width=6),

            dbc.Col([
                html.H5('I-V curves at 25 ºC'),
                dcc.Graph(
                    figure={
                        'data': [
                            {'x': s['v'], 'y': s['i'], 'type': 'line',
                             'name': s['legend']} for s in iv_curve
                        ],
                        'layout': go.Layout(
                            legend=dict(x=.05, y=0.05),
                            autosize=True,
                            xaxis={'title': 'Voltage (V)'},
                            yaxis={'title': 'Current (A)'},
                            margin={'l': 40, 'b': 90, 't': 10, 'r': 10},
                            hovermode='closest',
                            colorway = allc_step1
                        )
                    },
                    config=dict(
                        toImageButtonOptions=dict(
                            scale=5,
                            filename='IV_curves',
                        )
                    ),
                    mathjax = True
                ),
            ], width=6)

            
        ])
    ]
 
@app.callback([Output('coefficents', 'children'),
               Output('results-store', 'data')],
              [Input('calc-button', 'n_clicks')
               ],
              [State('module_parameter_input_type', 'active_tab'),
               State('module_name_select', 'value'),
               State('module_name_manual', 'value'),
               State('v_oc_ref', 'value'),
               State('i_sc_ref', 'value'),
               State('alpha_sc', 'value'),
               State('beta_oc', 'value'),
               State('I_L_ref', 'value'),
               State('I_o_ref', 'value'),
               State('R_s', 'value'),
               State('R_sh_ref', 'value'),
               State('a_ref', 'value'),
               State('N_cells', 'value'),
               
               ]
              )

def run_simulation(n_clicks, 
                   module_parameter_input_type,
                   module_name, 
                   module_name_manual, 
                   v_oc_ref,
                   i_sc_ref,
                   alpha_sc,
                   beta_oc,
                   I_L_ref,
                   I_o_ref,
                   R_s,
                   R_sh_ref,
                   a_ref,
                   N_cells
                   ):
    
    
    if n_clicks < 1:
        raise PreventUpdate
    
    if module_parameter_input_type == 'lookup':
    
        paras = cec_modules[module_name].to_dict()
        module_name_show = module_name

        N_cells = paras['N_s']
        Voc_ref = paras['V_oc_ref']
        Isc_ref = paras['I_sc_ref']
        alpha_isc_rel = paras['alpha_sc']/paras['I_sc_ref']
        beta_voc_rel = paras['beta_oc']/paras['V_oc_ref']
        alpha_isc_abs = paras['alpha_sc']
        beta_voc_abs = paras['beta_oc']

        SDMparams = {'I_L_ref': paras['I_L_ref'], 
                    'I_o_ref': paras['I_o_ref'], 
                    'R_s': paras['R_s'], 
                    'R_sh_ref': paras['R_sh_ref'], 
                    'a_ref':paras['a_ref']}
        
    elif module_parameter_input_type == 'manual':

        Voc_ref = float(v_oc_ref)
        Isc_ref = float(i_sc_ref)
        alpha_isc_abs = float(alpha_sc)
        beta_voc_abs = float(beta_oc)
        alpha_isc_rel = float(alpha_sc)/float(i_sc_ref)
        beta_voc_rel = float(beta_oc)/float(v_oc_ref)
        N_cells = int(N_cells)
        module_name_show = module_name_manual
       
        SDMparams = {
            'I_L_ref': float(I_L_ref),
            'I_o_ref': float(I_o_ref),
            'R_s': float(R_s),
            'R_sh_ref': float(R_sh_ref),
            'a_ref': float(a_ref),
        }
    
    coefs_P1 = ivcorrection.get_P1_coefs(alpha_isc_abs, beta_voc_abs, SDMparams)
    coefs_P2 = ivcorrection.get_P2_coefs(alpha_isc_abs = alpha_isc_abs,
                        alpha_isc_rel= alpha_isc_rel,
                        beta_voc_rel= beta_voc_rel,
                        voc_ref= Voc_ref,
                        SDMparams= SDMparams)
    
    coefs_P1_df = pd.DataFrame.from_dict({
        'Coefficients': list(coefs_P1.keys()) })
    coefs_P1_df['Value'] = coefs_P1_df['Coefficients'].map(coefs_P1)
    coefs_P1_df['Value'] = coefs_P1_df['Value'].apply(lambda x: '{:.4f}'.format(x))

    coefs_P2_df = pd.DataFrame.from_dict({
        'Coefficients': list(coefs_P2.keys()) })
    coefs_P2_df['Value'] = coefs_P2_df['Coefficients'].map(coefs_P2)
    coefs_P2_df['Value'] = coefs_P2_df['Value'].apply(lambda x: '{:.4f}'.format(x))
    
    results_store = dict(coefs_P1=coefs_P1,
            coefs_P2=coefs_P2,
            alpha_isc_rel = alpha_isc_rel,
            beta_voc_rel = beta_voc_rel,
            alpha_isc_abs = alpha_isc_abs,
            beta_voc_abs = beta_voc_abs,
            Voc_ref = Voc_ref,
            Isc_ref = Isc_ref,
            SDMparams = SDMparams,
            N_cells = N_cells,
            module_name_show = module_name_show)
    
    return_layout = [
        dbc.Row([

            dbc.Col([
                html.H4('Coefficients of Procedure 1'),
                dbc.FormText('(PV module: {})'.format(module_name_show)),
                html.Div([
                    dbc.Table.from_dataframe(coefs_P1_df,
                                            striped=False,
                                            bordered=True,
                                            hover=True,
                                            index=False,
                                            size='sm',
                                            style={'font-size': '1rem'})
                ])
            ]),

            dbc.Col([
                html.H4('Coefficients of Procedure 2'),
                dbc.FormText('(PV module: {})'.format(module_name_show)),
                html.Div([
                    dbc.Table.from_dataframe(coefs_P2_df,
                                            striped=False,
                                            bordered=True,
                                            hover=True,
                                            index=False,
                                            size='sm',
                                            style={'font-size': '1rem'})
                ])
            ]),
        ]),

        dcc.Markdown("""For Procedure 4 and Pdynamic:
               - **Procedure 4** does not require correction coefficients
               - **Pdynamic** uses the partial correction coefficients (k, B1, B2) of Procedure 2. 
                    rs is determined via sandia function \[3\].""".replace('    ', '')),

    ]
        
    return [
        return_layout,
        results_store
    ]

@app.callback([Output('GT_message', 'children'),
               Output('new_coeff', 'children'),
               Output('iv_example', 'children', allow_duplicate=True),
               Output('corrected_iv', 'children', allow_duplicate=True)],
              [Input('iv_example_button', 'n_clicks')],
              [State('G_manual', 'value'),
               State('Tm_manual', 'value'),
               State('checkbox_rs', 'value'),
               State('checkbox_rsh', 'value'),
               State('rs_input', 'value'),
               State('rsh_input', 'value'),
               State('results-store', 'data'),
               State('checkbox_re_esti', 'value'),],
               prevent_initial_call=True
              )

def generate_correct_iv(n_clicks, G_manual,
                   Tm_manual, checkbox_rs, checkbox_rsh, rs_degra, rsh_degra,
                   coeffs_results, checkbox_re_esti):
    
    if n_clicks < 1:
        raise PreventUpdate
    
    if not coeffs_results:
        return [
            html.H4('Please run the calculation of correction coefficients in Step 2.'),
            html.P(''),
            html.P(''),
            html.P(''),
        ]

    # check input G and T
    if (not G_manual.strip()) | (not Tm_manual.strip()):
        return [
            html.H4('Please provide values for irradiance and temperature!'),
            html.P(''),
            html.P(''),
            html.P(''),
        ]
    try:
        G_manual = G_manual.rstrip(',').replace(" ", "")
        Tm_manual = Tm_manual.rstrip(',').replace(" ", "")

        G_list = [float(idx.strip()) for idx in G_manual.split(',')]
        Tm_list = [float(idx.strip()) for idx in Tm_manual.split(',')]
    except:
        return [
            html.H4('Please provide valid values for irradiance and temperature!'),
            html.P(''),
            html.P(''),
            html.P(''),
        ]

    if len(G_list) != len(Tm_list):

        return [
            html.H4('Please make sure irradiance point number is equal to temperature point number!'),
            html.P(''),
            html.P(''),
            html.P(''),
        ]
    

    # check rs and rsh value
    if checkbox_rs:
        rs_degra = float(rs_degra)
    else:
        rs_degra = None

    if checkbox_rsh:
        rsh_degra = float(rsh_degra)
    else:
        rsh_degra = None

    # re-estimate coefficients if requested

    alpha_isc_abs = coeffs_results['alpha_isc_abs']
    SDMparams = coeffs_results['SDMparams']

    # update coefficients when both the re-esti and rs-degradation box are checked
    new_coeff_layout = html.P('')

    if bool(checkbox_re_esti) & bool(checkbox_rs):

        SDMparams_degra = SDMparams.copy()
        SDMparams_degra['R_s'] = SDMparams_degra['R_s'] + rs_degra

        coefs_P1 = ivcorrection.get_P1_coefs(alpha_isc_abs, 
                                            coeffs_results['beta_voc_abs'], 
                                            SDMparams_degra)
        coefs_P2 = ivcorrection.get_P2_coefs(alpha_isc_abs,
                            alpha_isc_rel= coeffs_results['alpha_isc_rel'],
                            beta_voc_rel= coeffs_results['beta_voc_rel'],
                            voc_ref= coeffs_results['Voc_ref'],
                            SDMparams= SDMparams_degra)
        
        coeffs_results['coefs_P1'] = coefs_P1
        coeffs_results['coefs_P2'] = coefs_P2

        coefs_P1_df = pd.DataFrame.from_dict({
            'Coefficients': list(coefs_P1.keys()) })
        coefs_P1_df['Value'] = coefs_P1_df['Coefficients'].map(coefs_P1)
        coefs_P1_df['Value'] = coefs_P1_df['Value'].apply(lambda x: '{:.4f}'.format(x))

        coefs_P2_df = pd.DataFrame.from_dict({
            'Coefficients': list(coefs_P2.keys()) })
        coefs_P2_df['Value'] = coefs_P2_df['Coefficients'].map(coefs_P2)
        coefs_P2_df['Value'] = coefs_P2_df['Value'].apply(lambda x: '{:.4f}'.format(x))

        new_coeff_layout = html.Div([
            html.H6('New coefficients of Procedure 1'),
            html.Div([
                dbc.Table.from_dataframe(coefs_P1_df,
                                        striped=False,
                                        bordered=True,
                                        hover=True,
                                        index=False,
                                        size='sm',
                                        style={'font-size': '1rem'})
            ]),
            html.H6('New coefficients of Procedure 2'),
            html.Div([
                dbc.Table.from_dataframe(coefs_P2_df,
                                        striped=False,
                                        bordered=True,
                                        hover=True,
                                        index=False,
                                        size='sm',
                                        style={'font-size': '1rem'})
            ])
        ])

    # Generate IV curves

    iv_raw = ivcorrection.simu_IV_curve(G_list, Tm_list, alpha_isc_abs, SDMparams, 
                                        rs_degra, rsh_degra)
    iv_ref = ivcorrection.simu_IV_curve([1000], [25], alpha_isc_abs, SDMparams, 
                                        rs_degra, rsh_degra)

    return[
        html.P(''),
        new_coeff_layout,
        iv_example_layout(iv_raw, coeffs_results, checkbox_rs, checkbox_rsh, 
                          rs_degra, rsh_degra),
        iv_corrected_layout(iv_raw, iv_ref, coeffs_results, checkbox_rs, checkbox_rsh, 
                            rs_degra, rsh_degra, checkbox_re_esti)
    ]

@app.callback(
    Output("details-collapse", "is_open"),
    [Input("details-button", "n_clicks")],
    [State("details-collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

def get_legend(iv):
    alllegend = []
    for nGT in range(iv['G'].size):
        G = iv['G'][nGT]
        Tm = iv['T'][nGT]
        alllegend.append('${:.1f}\ W/m^2 \ {:.1f} ^\circ C$'.format(G,Tm))

    return alllegend

def get_colorway(allG):

    # Colormap
    colors = ["lightseagreen", "lawngreen", "gold", "darkorange"]
    cmap = LinearSegmentedColormap.from_list("mycmap", colors)

    allc = []
    for i in range(np.array(allG).size):
        G = allG[i]
        idG = (G-min(allG))/(max(allG)-min(allG)+1)
        ctemp =cmap(idG)[:3]
        c = tuple(int(val * 255) for val in ctemp)
        allc.append('#'+'%02x%02x%02x' %c)

    return allc

def iv_example_layout(iv_raw, coeffs_results, 
                      checkbox_rs = None,  
                      checkbox_rsh = None, 
                      rs_degra = None, 
                      rsh_degra = None):

    G_list = iv_raw['G']
    legend_raw = get_legend(iv_raw)
    allc = get_colorway(G_list)
    module_name_show = coeffs_results['module_name_show']
    yshowmax = coeffs_results['Isc_ref'] * max(iv_raw['G'])/1000 * 1.1

    title = dcc.Markdown("""#### Example I-V curves to correct """)

    if bool(checkbox_rs) | bool(checkbox_rsh):
        extra_title = ""
        if checkbox_rs:
            extra_title = extra_title + "$R_{s\_degra} = " + str(rs_degra) + "\Omega$"
        if checkbox_rsh:
            extra_title = extra_title + " $R_{sh\_degra} = " + str(rsh_degra) + "\Omega$"

        extra_title = "###### (" + extra_title + ")"
        title = html.Div([
                title,
                html.Div([dcc.Markdown(extra_title, mathjax = True)], style={'color': select_color}),
        ])

    generated_iv_layout = [
        title,
        dbc.FormText('(PV module: {})'.format(module_name_show)),
        dcc.Graph(
            figure={
                'data': [
                    {'x': iv_raw['v'][s], 'y': iv_raw['i'][s], 
                     'type': 'line',
                     'name': legend_raw[s],
                     'line_color':'red'
                    } for s in range(iv_raw['G'].size)
                ],
                'layout': go.Layout(
                    legend=dict(x=.05, y=0.05),
                    autosize=True,
                    xaxis={'title': 'Voltage (V)'},
                    yaxis={'title': 'Current (A)', 'range': [0, yshowmax]},
                    margin={'l': 40, 'b': 90, 't': 10, 'r': 10},
                    hovermode='closest',
                    colorway = allc
                )
            },
            config=dict(
                toImageButtonOptions=dict(
                    scale=5,
                    filename='IV_curves',
                )
            ),
            mathjax = True
        ),
    ]
    return generated_iv_layout

def iv_corrected_layout(iv_raw, iv_ref, coeffs_results, 
                        checkbox_rs = None,  
                        checkbox_rsh = None, 
                        rs_degra = None, 
                        rsh_degra = None,
                        checkbox_re_esti = None):
    
    G_list = iv_raw['G']
    allc = get_colorway(G_list)
    module_name_show = coeffs_results['module_name_show']

    # Correct IV curves
    if coeffs_results is None:
        corrected_layout = [
            html.P(''),
            html.H4("""To get corrected I-V curves, 
                    please run the calculation of coefficients first in Step 2"""),
        ]

    else:
        coefs_P1 = coeffs_results['coefs_P1']
        coefs_P2 = coeffs_results['coefs_P2']
        alpha_isc_abs = coeffs_results['alpha_isc_abs']
        beta_voc_abs = coeffs_results['beta_voc_abs']
        alpha_isc_rel = coeffs_results['alpha_isc_rel']
        beta_voc_rel = coeffs_results['beta_voc_rel']
        Voc_ref = coeffs_results['Voc_ref']
        N_cells = coeffs_results['N_cells']

        iv_P1 = ivcorrection.get_corrected_IV_P1(iv_raw, alpha_isc_abs, beta_voc_abs, **coefs_P1)
        iv_P2 = ivcorrection.get_corrected_IV_P2(iv_raw, alpha_isc_rel, beta_voc_rel, Voc_ref, **coefs_P2)
        iv_P4 = ivcorrection.get_corrected_IV_P4(iv_raw, alpha_isc_abs, N_cells)
        iv_Pdyna = ivcorrection.get_corrected_IV_Pdyna(iv_raw, alpha_isc_rel, beta_voc_rel, Voc_ref, **coefs_P2)
        legend_P = get_legend(iv_P1)

        err_P1 = ivcorrection.calc_correction_error(iv_P1, iv_ref)
        err_P2 = ivcorrection.calc_correction_error(iv_P2, iv_ref)
        err_P4 = ivcorrection.calc_correction_error(iv_P4, iv_ref)
        err_Pdyna = ivcorrection.calc_correction_error(iv_Pdyna, iv_ref)
        
        yshowmax = coeffs_results['Isc_ref']*1.1
        xshowmax = coeffs_results['Voc_ref']*1.1

        p1_trace = [{'x': iv_P1['v'][s], 'y': iv_P1['i'][s], 
                    'type': 'line',
                    'name': legend_P[s]
                    } for s in range(iv_P1['G'].size)]
        p2_trace = [{'x': iv_P2['v'][s], 'y': iv_P2['i'][s], 
                    'type': 'line',
                    'name': legend_P[s]
                    } for s in range(iv_P2['G'].size)]
        p4_trace = [{'x': iv_P4['v'][s], 'y': iv_P4['i'][s], 
                    'type': 'line',
                    'name': legend_P[s]
                    } for s in range(iv_P4['G'].size)]
        pdyna_trace = [{'x': iv_Pdyna['v'][s], 'y': iv_Pdyna['i'][s], 
                    'type': 'line',
                    'name': legend_P[s]
                    } for s in range(iv_Pdyna['G'].size)]
        
        
        ref_trace = {'x': iv_ref['v'][0], 'y': iv_ref['i'][0], 
                    'type': 'line',
                    'name': r'$\text{Ref:}\ 1000.0\ W/m^2 \ 25.0 ^\circ C$',
                    'line': dict( width= 2, dash = 'dash'),
                    } 
        allc.append('#000000')

        p1_trace.append(ref_trace)
        p2_trace.append(ref_trace)
        p4_trace.append(ref_trace)
        pdyna_trace.append(ref_trace)

        layout_p1 = dbc.Col([
                    html.H5("""Using Procedure 1 """),
                    dbc.FormText("""(Correction error: {:.2f}%)
                            """.format(np.nanmean(err_P1))),
                    dcc.Graph(
                        figure={
                            'data': p1_trace,
                            'layout': go.Layout(
                                legend=dict(x=.05, y=0.05),
                                autosize=True,
                                xaxis={'title': 'Voltage (V)', 'range': [0, xshowmax]},
                                yaxis={'title': 'Current (A)', 'range': [0, yshowmax]},
                                margin={'l': 40, 'b': 90, 't': 10, 'r': 10},
                                hovermode='closest',
                                colorway = allc,
                            )
                        },
                        config=dict(
                            toImageButtonOptions=dict(
                                scale=5,
                                filename='IV_curves_P1',
                            )
                        ),
                        mathjax = True
                    ),
                ])
        layout_p2 = dbc.Col([
                    html.H5("""Using Procedure 2 """),
                    dbc.FormText("""(Correction error: {:.2f}%)
                            """.format(np.nanmean(err_P2))),
                    dcc.Graph(
                        figure={
                            'data': p2_trace,
                            'layout': go.Layout(
                                legend=dict(x=.05, y=0.05),
                                autosize=True,
                                xaxis={'title': 'Voltage (V)', 'range': [0, xshowmax]},
                                yaxis={'title': 'Current (A)', 'range': [0, yshowmax]},
                                margin={'l': 40, 'b': 90, 't': 10, 'r': 10},
                                hovermode='closest',
                                colorway = allc
                            )
                        },
                        config=dict(
                            toImageButtonOptions=dict(
                                scale=5,
                                filename='IV_curves_P2',
                            )
                        ),
                        mathjax = True
                    ),
                ])
        
        layout_p4 = dbc.Col([
                    html.H5("""Using Procedure 4 """),
                    dbc.FormText("""(Correction error: {:.2f}%)
                            """.format(np.nanmean(err_P4))),
                    dcc.Graph(
                        figure={
                            'data': p4_trace,
                            'layout': go.Layout(
                                legend=dict(x=.05, y=0.05),
                                autosize=True,
                                xaxis={'title': 'Voltage (V)', 'range': [0, xshowmax]},
                                yaxis={'title': 'Current (A)', 'range': [0, yshowmax]},
                                margin={'l': 40, 'b': 90, 't': 10, 'r': 10},
                                hovermode='closest',
                                colorway = allc
                            )
                        },
                        config=dict(
                            toImageButtonOptions=dict(
                                scale=5,
                                filename='IV_curves_P2',
                            )
                        ),
                        mathjax = True
                    ),
                ])
        layout_pdyna = dbc.Col([
                    html.H5("""Using Procedure dynamic """),
                    dbc.FormText("""(Correction error: {:.2f}%)
                            """.format(np.nanmean(err_Pdyna))),
                    dcc.Graph(
                        figure={
                            'data': pdyna_trace,
                            'layout': go.Layout(
                                legend=dict(x=.05, y=0.05),
                                autosize=True,
                                xaxis={'title': 'Voltage (V)', 'range': [0, xshowmax]},
                                yaxis={'title': 'Current (A)', 'range': [0, yshowmax]},
                                margin={'l': 40, 'b': 90, 't': 10, 'r': 10},
                                hovermode='closest',
                                colorway = allc
                            )
                        },
                        config=dict(
                            toImageButtonOptions=dict(
                                scale=5,
                                filename='IV_curves_Pdyna',
                            )
                        ),
                        mathjax = True
                    ),
                ])
        
        title = dcc.Markdown("""#### Corrected I-V curves to correct """)

        if bool(checkbox_rs) | bool(checkbox_rsh) | bool(checkbox_re_esti):
            extra_title = ""
            if checkbox_rs:
                extra_title = extra_title + "$R_{s\_degra} = " + str(rs_degra) + "\Omega$"
            if checkbox_rsh:
                extra_title = extra_title + " $R_{sh\_degra} = " + str(rsh_degra) + "\Omega$"
            if checkbox_re_esti:
                extra_title = extra_title + " with re-estimated coefficients"

            extra_title = "###### (" + extra_title + ")"
            title = html.Div([
                title,
                html.Div([dcc.Markdown(extra_title, mathjax = True)], style={'color': select_color}),
        ])

        corrected_layout = [
            html.Hr(),
            title,
            dbc.FormText('(PV module: {})'.format(module_name_show)),
            html.Details([
                html.Summary('Metric of the correction error'),
                dcc.Markdown("""
                
                The correction error is expressed by the error of area ($E_{area}$) \[4\]:
                                
                $E_{area} = A_{err}/A_{ref}*100%$
                                
                where, $A_{ref}$ is the area size under the reference curve 
                (directly simulated at STC) 
                and $A_{err}$ the area size between 
                the corrected curve and the reference curve.  
                            
                            
                """.replace('    ', ''), mathjax = True),
            ]),

            html.P(''),
            
            dbc.Row([
                layout_p1,
                layout_p2
            ]),

            dbc.Row([
                layout_p4,
                layout_pdyna 
            ])
            
        ]

        return corrected_layout


@callback(Output('output-data-upload', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              prevent_initial_call=True)
def process_updated_data(content, filename):
    if content is not None:

        _, content_string = content[0].split(',')
        decoded = base64.b64decode(content_string)
        try:
            if 'csv' in filename[0]:
                # Assume that the user uploaded a CSV file
                df = pd.read_csv(
                    io.StringIO(decoded.decode('utf-8')))

            elif 'xls' in filename[0]:
                # Assume that the user uploaded an excel file
                df = pd.read_excel(io.BytesIO(decoded))

            else:
                return html.H4(
                        "Please upload a 'csv' or 'xls' file.")

        except Exception as e:
            print(e)
            return html.H4(
                'There was an error processing this file.')

        button_layout = html.Div([
            dbc.FormText('{} uploaded.'.format(filename[0])),
            html.P(''),
            dbc.Button(id='uploaded_iv_button',
                            n_clicks=0,
                            children='Plot and correct I-V curves',
                            color="secondary"),
        ])

        return button_layout
    
@callback([Output('iv_example', 'children'),
           Output('corrected_iv', 'children')],
           Input('uploaded_iv_button', 'n_clicks'),
           State('upload-data', 'contents'),
           State('results-store', 'data'),
           prevent_initial_call=True)
def plot_correct_uploaded_iv(n_clicks, content, coeffs_results):

    if n_clicks < 1:
        raise PreventUpdate
    
    if not coeffs_results:
        return [
            html.P(''), 
            html.H4('Please run the calculation of correction coefficients in Step 2.'), 
                 
        ]
    
    _, content_string = content[0].split(',')
    decoded = base64.b64decode(content_string)
    
    df = pd.read_excel(io.BytesIO(decoded))
    iv_raw = df_to_dict(df)

    alpha_isc_abs = coeffs_results['alpha_isc_abs']
    SDMparams = coeffs_results['SDMparams']
    iv_ref = ivcorrection.simu_IV_curve([1000], [25], alpha_isc_abs, SDMparams)

    return [
        iv_example_layout(iv_raw, coeffs_results),
        iv_corrected_layout(iv_raw, iv_ref, coeffs_results)
    ]

def df_to_dict(df):
    ivcurves = {}
    alli = {}
    allv = {}
    for i in range(len(df)):
        alli[i] = np.array(ast.literal_eval(df['i'][i]))
        allv[i] = np.array(ast.literal_eval(df['v'][i]))

    ivcurves['G'] = df['G'].to_numpy()
    ivcurves['T'] = df['T'].to_numpy()
    ivcurves['v'] = allv
    ivcurves['i'] = alli

    return ivcurves

@app.callback(
    Output('checkbox_rs', 'style'),
    Output('rs_text', 'style'),
    Output('rs_input', 'style'),
    Output('rs_explain', 'style'),
    Input('checkbox_rs', 'value')
)
def update_rs_box(rs_value):
    if rs_value:
        return [{'color': select_color, 'font-weight': 'bold'}, 
                {'color': select_color}, 
                {'color': select_color, 'max-width': 50},
                {'color': '#7F7F7F'}, ]
    else:
        return [{'color': ini_color, 'font-weight': 'bold'}, 
                {'color': ini_color},
                {'color': ini_color, 'max-width': 50},
                {'color': ini_color}]


@app.callback(
    Output('checkbox_re_esti', 'style'),
    Output('re_esti_explain', 'style'),
    Input('checkbox_re_esti', 'value')
)
def update_re_esti_box(checkbox_re_esti):
    if checkbox_re_esti:
        return [{'color': select_color, 'font-weight': 'bold'}, 
                {'color': select_color}]
    else:
        return [{'color': ini_color, 'font-weight': 'bold'}, 
                {'color': ini_color}]

@app.callback(
    Output('checkbox_rsh', 'style'),
    Output('rsh_text', 'style'),
    Output('rsh_input', 'style'),
    Output('rsh_explain', 'style'),
    Input('checkbox_rsh', 'value')
)
def update_rsh_box(rs_value):
    if rs_value:
        return [{'color': select_color, 'font-weight': 'bold'}, 
                {'color': select_color}, 
                {'color': select_color, 'max-width': 50},
                {'color': '#7F7F7F'}, ]
    else:
        return [{'color': ini_color, 'font-weight': 'bold'}, 
                {'color': ini_color},
                {'color': ini_color, 'max-width': 50},
                {'color': ini_color}]


if __name__ == "__main__":
    # app.layout = html.Div(layout)
    app.run(debug=True)