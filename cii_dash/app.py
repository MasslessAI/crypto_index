import sys
import os
from datetime import datetime, timedelta

import pandas as pd

import plotly.graph_objs as go

import dash
import dash_core_components as dcc
import dash_html_components as html

from helpers import *
from styles import *

DB_PATH = '../data/testdb.db'
conn = getdb(DB_PATH)

dateparse = lambda x: pd.datetime.strptime(x, '%Y-%m-%dT%H:%M:%S.%fZ')
query = 'SELECT * FROM df_btc'
df_btc = pd.read_sql(query, conn)
query = 'SELECT * FROM df_eth'
df_eth = pd.read_sql(query, conn)

reportDF = test_strategy(df_btc, df_eth)

app = dash.Dash()

#layout
app.layout=html.Div(
    children = [
        html.Div(
            style={
                'color':'white',
                'background-color': '#471584',
                'width':'100%',
                'height':'60px'
            },
            className='twelve columns',
            children=[
                html.Div(
                    style={
                        'width':'90%',
                        'font-weight':'bold',
                        'font-size': '2.0rem',
                        'padding-left':'25px',
                        'padding-top':'0px',
                        'padding-bottom':'0px',
                        #'background-color':'blue',
                    },
                    children='Massless Crypto Index')
            ],
        ),
        html.Div(
            id='my-canvas',
            style=style_my_canvas,
            children=[
                html.Div(
                    style=style_hidden,
                    children=reportDF.to_json(date_format='iso', orient='split')
                ),

                html.Div(
                    id='my-jumbotron',
                    style={
                        'background-color':'#5f1daf',
                        'height':'300px',
                        'width':'100%',
                        'display':'none',
                    },

                ),
                html.Div(
                    className='row',
                    children=[
                        html.Div(
                            className='twelve columns',
                            children=[
                                html.H6(
                                    style=style_section_header,
                                    children='Market Update'
                                ),
                            ]
                        ),
                    ]
                ),
                html.Div(
                    id='my-dashboard',
                    className='row',

                    children=[
                        # html.Div(make_candlestick(df_btc, 'btc')),
                        
                        html.Div(
                            id='div-dash-control-area',
                            className='three columns',
                            children=[
                                html.H6(
                                            style=style_section_header,
                                            children='Market Data Console'
                                ),

                                html.P(
                                    children='Select and Update'
                                ),

                                dcc.Dropdown(
                                    id='dropdown-asset-name',
                                    options=[
                                        {'label':'BTC', 'value':'df_btc'},
                                        {'label':'ETH', 'value':'df_eth'},
                                    ],
                                    value='df_btc'
                                ),

                                html.P(),

                                html.Button(
                                    id='botton-update-market-data',
                                    children='Update'
                                ),

                                html.H6(
                                    style=style_section_header,
                                    children='Market Indicators'
                                ),

                                html.Table(
                                    children=[
                                        html.Tr(
                                            children=[
                                                html.Th('Asset'),
                                                html.Th('Index 0'),
                                                html.Th('Index 1'),
                                            ]
                                        ),

                                        html.Tr(
                                            children=[
                                                html.Td('ETH'),
                                                html.Td('Number 0'),
                                                html.Td('Number 1'),
                                            ]
                                        ),

                                        html.Tr(
                                            children=[
                                                html.Td('BTC'),
                                                html.Td('Number 1'),
                                                html.Td('Number 2'),
                                            ]
                                        ),
                                    ]
                                    
                                    
                                ),

                            ]
                        ),

                        html.Div(
                            id='div-dash-plot-area',
                            className='nine columns',
                            children=[
                                html.H6(
                                    style=style_section_header,
                                    children=['Visual Area Place Holder']
                                ),
                                html.Div(
                                    id='plot-asset-oclhv',
                                    children=[ 
                                        
                                        dcc.Graph(
                                            id='plot-price-candlestick',
                                            figure = {
                                                'data': [make_candlestick(df_btc,'btc')],
                                                'layout': {
                                                    'title': 'Price',
                                                    'margin': {'b': 15, 'r': 10, 'l': 60, 't': 30},
                                                    'legend': {'x': 0},
                                                    'padding-top':'5rem'
                                                }
                                            }
                                        ),
                                        
                                        dcc.Graph(
                                            id='plot-eth-candlestick',
                                            figure = {
                                                'data': [make_candlestick(df_eth,'eth')],
                                                'layout': {
                                                    'title':'Price',
                                                    'margin': {'b': 15, 'r': 10, 'l': 60, 't': 30},
                                                    'legend': {'x': 0}
                                                }
                                            }
                                        ),
                                        

                                        
                                    ]
                                
                                ),
                            ]

                        )
                    ]
                ),
                html.Div(
                    className='row',
                    children=[
                        html.Div(
                            className='twelve columns',
                            children=[
                                html.H6(
                                    style=style_section_header,
                                    children='Test Your Strategy')
                            ]
                        )
                    ]
                ),

                html.Div(
                    id='div-strategy-area',
                    className='row',
                    children=[
                        html.Div(
                            id='div-strategy-console-area',
                            className='three columns',
                            children=[
                                html.H6(
                                    style=style_section_header,
                                    children='Strategy Console',
                                ),
                                html.P('Initial Cash'),
                                dcc.Input(
                                    id='input-strategy-init-cash',
                                    placeholder=100000,
                                    type='number'
                                ),
                                html.P('Initial BTC'),
                                dcc.Input(
                                    id='input-strategy-init-btc',
                                    placeholder=0,
                                    type='number'
                                ),
                                html.P('Initial ETH'),
                                dcc.Input(
                                    id='input-strategy-init-eth',
                                    placeholder=0,
                                    type='number'
                                ),
                                html.P('Up tolerance'),
                                dcc.Input(
                                    id='input-strategy-up-tolerance',
                                    placeholder=0.1,
                                    type='number'
                                ),
                                html.P('Down tolerance'),
                                dcc.Input(
                                    id='input-strategy-down-tolerance',
                                    placeholder=0.1,
                                    type='number'
                                ),
                                html.P('Back testing start date'),
                                dcc.DatePickerSingle(
                                    id='date-picker-single-back-testing-start',
                                    # min_date_allowed=dt(1995, 8, 5),
                                    # max_date_allowed=dt(2017, 9, 19),
                                    # initial_visible_month=dt(2017, 8, 5),
                                    date=datetime(2017, 2, 1)
                                ),
                                html.P('Test Your Strategy'),
                                html.Button(
                                    id='button-test-strategy',
                                    children='Run'
                                ),
                            ]
                        ),

                        html.Div(
                            id='div-strategy-plot-area',
                            className='nine columns',
                            children=[
                                html.H6(
                                    style=style_section_header,
                                    children='Strategy Returns'),
                                dcc.Graph(
                                    id='strategy-pnl',
                                    figure = {
                                        'data':[
                                            go.Scatter(
                                                x=reportDF['date'],
                                                y=reportDF['total'],
                                                name='Test'
                                            ),
                                            go.Scatter(
                                                x=reportDF['date'],
                                                y=reportDF['btc_return'],
                                                name='BTC'
                                            ),
                                            go.Scatter(
                                                x=reportDF['date'],
                                                y=reportDF['eth_return'],
                                                name='ETH'
                                            ),
                                        ],
                                        'layout':{
                                            'title': 'Strategy Return'
                                        }
                                    }
                                ),
                            ]
                        ),
                    ]
                )
            ]
        )
    ]
)

#callbacks
@app.callback(
    dash.dependencies.Output('plot-price-candlestick','figure'),
    [dash.dependencies.Input('botton-update-market-data','n_clicks')],
    state=[
        dash.dependencies.State('dropdown-asset-name','value')
    ]
)
def update_plot_price(buttonClick, ticker, conn=conn):
    tableName =df_+'ticker'
    query = 'select * from %s' % tableName
    df = pd.read_sql(query, conn)
    figure = {
        'data': [make_candlestick(df,ticker)],
        'layout': {
            'title':'Price',
            'margin': {'b': 15, 'r': 10, 'l': 60, 't': 30},
            'legend': {'x': 0}
        }
    }
    return figure

#additional style sheets
app.css.append_css({'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'})

if __name__ == '__main__':
    app.run_server(debug=False, host='0.0.0.0')

#add a dropdown for signal