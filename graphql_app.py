import time

import dash
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
from ibapi.contract import Contract
from ibapi.order import Order
from dash import dcc
from dash import html
from dash.exceptions import PreventUpdate
import dash_daq as daq

# Make a Dash app!
app = dash.Dash(__name__)

# Define the layout.
app.layout = html.Div([
    html.Div(
        id='sync-connection-status',
        children='False',
        style={'display': 'none'}
    ),
    html.Div([
        # Section title
        html.H3("Fetch & Display required ITP data"),
        html.H4("Select value for whatToShow:"),
        html.Div(
            dcc.Dropdown(
                ["TRADES", "MIDPOINT", "BID", "ASK", "BID_ASK", "ADJUSTED_LAST",
                 "HISTORICAL_VOLATILITY", "OPTION_IMPLIED_VOLATILITY",
                 'REBATE_RATE', 'FEE_RATE', "YIELD_BID", "YIELD_ASK",
                 'YIELD_BID_ASK', 'YIELD_LAST', "SCHEDULE"],
                "MIDPOINT",
                id='what-to-show'
            )
        ),
        html.H4("Select value for Time range:"),
        html.Div(
            children=[
                html.P(
                    "You may select a specific endDateTime for the call to " + \
                    "fetch_historical_data. If any of the below is empty, " + \
                    "the current present moment will be used."
                )
            ]
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Label('Date:'),
                        dcc.DatePickerSingle(id='edt-date')
                    ],
                    style={
                        'display': 'inline-block',
                        'margin-right': '20px',
                    }
                ),
                html.Div(
                    children=[
                        html.Label('Hour:'),
                        dcc.Dropdown(list(range(24)), id='edt-hour'),
                    ],
                    style={
                        'display': 'inline-block',
                        'padding-right': '5px'
                    }
                ),
                html.Div(
                    children=[
                        html.Label('Minute:'),
                        dcc.Dropdown(list(range(60)), id='edt-minute'),
                    ],
                    style={
                        'display': 'inline-block',
                        'padding-right': '5px'
                    }
                ),
                html.Div(
                    children=[
                        html.Label('Second:'),
                        dcc.Dropdown(list(range(60)), id='edt-second'),
                    ],
                    style={'display': 'inline-block'}
                )
            ]
        ),
        # Submit button
        html.Button('Submit', id='submit-button', n_clicks=0),
        # Div for initial instructions and the updated info once submit is pressed
        html.Div(
            id='currency-output',
            children='Enter a required code and press submit'),
    ],
        style={'width': '365px', 'display': 'inline-block'}
    ),
    html.Div([
        html.Div([
            html.H4(
                'Hostname: ',
                style={'display': 'inline-block', 'margin-right': 20}
            ),
            dcc.Input(
                id='default-host',
                value='127.0.0.01',
                type='text',
                style={'display': 'inline-block'}
            ),
            html.H4(
                'Port: ',
                style={'display': 'inline-block', 'margin-right': 59}
            ),
            dcc.Input(
                id='default-port',
                value='7497',
                type='text',
                style={'display': 'inline-block'}
            ),
            html.H4(
                'Client ID: ',
                style={'display': 'inline-block', 'margin-right': 27}
            ),
            dcc.Input(
                id='default-clientid',
                value='10645',
                type='text',
                style={'display': 'inline-block'}
            )
        ]
        ),
        html.Br(),
        html.Button('TEST SYNC CONNECTION', id='connect-button', n_clicks=0),
        html.Div(id='connect-indicator'),
        html.Div(id='contract-details')
    ],
        style={'width': '365px', 'display': 'inline-block'}
    ),
    # Line break
    html.Br(),
    # Div to hold the candlestick graph
    html.Div([dcc.Graph(id='candlestick-graph')]),
    # Another line break
    html.Br(),
    # Section title
    html.H6("Make a Trade"),
    # Div to confirm what trade was made
    html.Div(id='trade-output'),
    # Radio items to select buy or sell
    dcc.RadioItems(
        id='buy-or-sell',
        options=[
            {'label': 'BUY', 'value': 'BUY'},
            {'label': 'SELL', 'value': 'SELL'}
        ],
        value='BUY'
    ),
    # Text input for the currency pair to be traded
    dcc.Input(id='trade-currency', value='Stock-Code', type='text'),
    # Numeric input for the trade amount
    dcc.Input(id='trade-amt', value='20000', type='number'),
    # Submit button for the trade
    html.Button('Trade', id='trade-button', n_clicks=0)

])

@app.callback(
    [
        Output("connect-indicator", "children"),
        Output("sync-connection-status", "children")
    ],
    Input("connect-button", "n_clicks")
)
def update_connect_indicator(n_clicks):
    try:
        managed_accounts = fetch_managed_accounts()
        message = "Connection successful! Managed accounts: " + ", ".join(
            managed_accounts)
        sync_connection_status = "True"
    except Exception as inst:
        x, y, z = inst.args
        message = "Error in " + x + ": " + y + ". " + z
        sync_connection_status = "False"
    return message, sync_connection_status

@app.callback(
    [ # there's more than one output here, so you have to use square brackets to
        # pass it in as an array.
        Output(component_id='currency-output', component_property='children'),
        Output(component_id='candlestick-graph', component_property='figure')
    ],
    Input('submit-button', 'n_clicks'),
    # The callback function will run when the submit button's n_clicks
    #   changes because the user pressed "submit".
    # The currency input's value is passed in as a "State" because if the user
    #   is typing and the value changes, then the callback function won't run.
    # But when the callback does run because the submit button was pressed,
    #   then the value of 'currency-input' at the time the button was pressed
    #   DOES get passed in to the function.
    [State('currency-input', 'value'), State('what-to-show', 'value'),
     State('edt-date', 'date'), State('edt-hour', 'value'),
     State('edt-minute', 'value'), State('edt-second', 'value')],
    prevent_initial_call = True
)
def update_candlestick_graph(n_clicks, currency_string, what_to_show,
                             edt_date, edt_hour, edt_minute, edt_second):
    # n_clicks doesn't get used, we only include it for the dependency.

    if any([i is None for i in [edt_date, edt_hour, edt_minute, edt_second]]):
        endDateTime = ''
    else:
        print(edt_date, edt_hour, edt_minute, edt_second)

    # First things first -- what currency pair history do you want to fetch?
    # Define it as a contract object!
    contract = Contract()
    contract.symbol   = currency_string.split(".")[0]
    contract.secType  = 'CASH'
    contract.exchange = 'IDEALPRO' # 'IDEALPRO' is the currency exchange.
    contract.currency = currency_string.split(".")[1]

    contract_details = fetch_contract_details(contract)

    # time.sleep(5)

    ############################################################################
    ############################################################################
    # This block is the one you'll need to work on. UN-comment the code in this
    #   section and alter it to fetch & display your currency data!
    # Make the historical data request.
    # Where indicated below, you need to make a REACTIVE INPUT for each one of
    #   the required inputs for req_historical_data().
    # This resource should help: https://dash.plotly.com/dash-core-components

    # Some default values are provided below to help with your testing.
    # Don't forget -- you'll need to update the signature in this callback
    #   function to include your new vars!
    cph = fetch_historical_data(
        contract=contract,
        endDateTime=endDateTime,
        durationStr='30 D',
        barSizeSetting='1 hour',
        whatToShow=what_to_show,
        useRTH=True
    )
    # # Make the candlestick figure
    fig = go.Figure(
        data=[
            go.Candlestick(
                x=cph['date'],
                open=cph['open'],
                high=cph['high'],
                low=cph['low'],
                close=cph['close']
            )
        ]
    )
    # # Give the candlestick figure a title
    fig.update_layout(title=('Exchange Rate: ' + currency_string))
    ############################################################################
    ############################################################################

    currency_string = "fetched data for: " + contract_details

    # Return your updated text to currency-output, and the figure to
    #   candlestick-graph outputs
    return ('Submitted query for ' + currency_string), fig

# Callback for what to do when trade-button is pressed
@app.callback(
    # We're going to output the result to trade-output
    Output(component_id='trade-output', component_property='children'),
    # Only run this callback function when the trade-button is pressed
    Input('trade-button', 'n_clicks'),
    # We DON'T want to run this function whenever buy-or-sell, trade-currency,
    #   or trade-amt is updated, so we pass those in as States, not Inputs:
    [State('buy-or-sell', 'value'), State('trade-currency', 'value'),
     State('trade-amt', 'value')],
    # DON'T start executing trades just because n_clicks was initialized to 0!!!
    prevent_initial_call=True
)
def trade(n_clicks, action, trade_currency, trade_amt):
    # Still don't use n_clicks, but we need the dependency

    # Make the message that we want to send back to trade-output
    msg = action + ' ' + trade_amt + ' ' + trade_currency

    order = Order()
    order.action = action
    order.orderType = "MKT"
    order.totalQuantity = trade_amt



    # Return the message, which goes to the trade-output div's children
    return msg

# Run it!
if __name__ == '__main__':
    app.run_server(debug=True)
