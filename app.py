#### Exploring linear models for prediction
# -*- coding: utf-8 -*-

# Run this app with `python app3.py` and
# visit http://127.0.0.1:8050/ in your web browser.
# documentation at https://dash.plotly.com/ 

# based on ideas at "Dash App With Multiple Inputs" in https://dash.plotly.com/basic-callbacks
# plotly express line parameters via https://plotly.com/python-api-reference/generated/plotly.express.line.html#plotly.express.line

from flask import Flask
from os import environ

import pandas as pd
import dash
from dash import dcc
from dash import html
# plotly express could be used for simple applications
# but this app needs to build plotly graph components separately 
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash.dependencies import Input, Output
import numpy as np
import datetime

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

server = Flask(__name__)
app = dash.Dash(
    server=server,
    url_base_pathname=environ.get('JUPYTERHUB_SERVICE_PREFIX', '/'),
    external_stylesheets=external_stylesheets
)

##################################
# Fetch and prep the data
# read in the data from the prepared CSV file. 
co2_data_source = "monthly_in_situ_co2_mlo.csv"
co2_data_full = pd.read_csv(
    co2_data_source, skiprows=np.arange(0, 56), na_values="-99.99"
)

co2_data_full.columns = [
    "year", "month", "date_int", "date", "raw_co2", "seasonally_adjusted",
    "fit", "seasonally_adjusted_fit", "co2 filled", "seasonally_adjusted_filled" 
]

# for handling NaN's see https://pandas.pydata.org/pandas-docs/stable/user_guide/missing_data.html
co2_data = co2_data_full.dropna()

co2_data['day'] = 15
co2_data['Datetime'] = pd.to_datetime(dict(year=co2_data.year, month=co2_data.month, day=co2_data.day))
#co2_data = co2_data.drop(['year', 'month', 'day'], axis=1)

#get Northerm Hemisphere mean monthly surface temp data
temp_data_source = "NH.Ts+dSST.csv"
#there are three seperate datasets in the csv, I'm picking out v7
temp_data_full = pd.read_csv(
    temp_data_source, skiprows=np.concatenate([np.arange(0, 23), np.arange(44, 66)]), na_values="*******"
)

temp_data = temp_data_full[['Year', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']]
temp_data = temp_data.melt(id_vars=['Year'])
temp_data = temp_data.sort_values(by='Year', kind='stable', ignore_index=True)
temp_data.rename(columns = {'variable': 'Month', 'value': 'Temp'}, inplace = True)
temp_data['Day'] = 15
temp_data['Month'] = temp_data['Month'].apply(lambda x: datetime.datetime.strptime(x, "%b").month)
temp_data['Datetime'] = pd.to_datetime(dict(year=temp_data.Year, month=temp_data.Month, day=temp_data.Day))
temp_data = temp_data.drop(['Year', 'Month', 'Day'], axis=1)



# A linear model with slope and intercept to predict CO2
def predict_co2(slope, intercept, initial_date, prediction_date):
    a = slope * (prediction_date-initial_date) + intercept
    
    return a


instructions = open("instructions.md", "r")
instructions_markdown = instructions.read()

sources = open("sources.md", "r")
sources_markdown = sources.read()

##################################
# Lay out the page 
app.layout = html.Div([
# Introduction
    dcc.Markdown(
        children=instructions_markdown
    ),
    # controls for plot
    html.Div([
        dcc.Markdown(''' **_Slope:_** '''),
        dcc.Slider(
            id='line_slope', min=0, max=3, step=0.02, value=2,
            marks={0:'0', 0.5:'0.5', 1:'1', 1.5:'1.5', 2:'2', 2.5:'2.5', 3:'3'},
            tooltip={'always_visible':True, 'placement':'topLeft'}
        ),
    ], style={'width': '48%', 'display': 'inline-block'}),
    
    html.Div([
        dcc.Markdown(''' **_Intercept:_** '''),
        dcc.Slider(
            id='line_intcpt', min=220, max=320, step=0.2,value=312,
            marks={220:'220', 240:'240', 260:'260', 280:'280', 300:'300', 320:'320'},
            tooltip={'always_visible':True, 'placement':'topLeft'}
        ),
    ], style={'width': '48%', 'display': 'inline-block'}),    


    html.Div([
        dcc.Markdown(''' **_Signal type:_** '''),
        dcc.Checklist(
            id='data_type',
            options=[
                {'label': 'Raw data', 'value': 'raw'},
                {'label': 'Seasonally adjusted data', 'value': 'adj'},
                {'label': 'Fit', 'value': 'fit'},
                {'label': 'Seasonally adjusted fit', 'value': 'adj_fit'},
            ],
            value=['raw']
        )
    ], style={'width': '48%', 'display': 'inline-block'}),

# Done this way to make easier to set appropriate y-axis limits
# Could use sliders commented out above if y-axis limits are set by calculating range for years-span
     html.Div([
         dcc.Markdown(''' **_Plot Segment:_** '''),
         dcc.RadioItems(
            id='zone',
            options=[
            {'label': '1st 5 years', 'value': '1st5yrs'},
            {'label': 'last 5 years', 'value': 'last5yrs'},
            {'label': 'All data', 'value': 'alldata'}
            ],
            value='alldata'
        ),
    ], style={'width': '48%', 'display': 'inline-block'}),


    html.Div([
        dcc.Markdown(''' **_Select Month:_** '''),
        dcc.Dropdown(
            id='month_selection',
            options=[
                {'label': 'All', 'value': 'all'},
                {'label': 'January', 'value': 1},
                {'label': 'February', 'value': 2},
                {'label': 'March', 'value': 3},
                {'label': 'April', 'value': 4},
                {'label': 'May', 'value': 5},
                {'label': 'June', 'value': 6},
                {'label': 'July', 'value': 7},
                {'label': 'August', 'value': 8},
                {'label': 'September', 'value': 9},
                {'label': 'October', 'value': 10},
                {'label': 'November', 'value': 11},
                {'label': 'December', 'value': 12}
            ],
            value='all'
        ),
    ], style={'width': '48%', 'display': 'inline-block'}),
    

# after controls, place plot
    dcc.Graph(
        id='graph',
        config={
            'displayModeBar': True,
            'modeBarButtonsToRemove': ['select', 'lasso2d', 'resetScale'],                     
        }
    ),

    #range slider to choose xlim
    html.Div([
        dcc.RangeSlider(
            id='xlim_slider',
            min=1958,
            max=2021,
            step=1.0,
            marks={
                1958: '1958',
                #1960: '1960',
                1970: '1970',
                1980: '1980',
                1990: '1990',
                2000: '2000',
                2010: '2010',
                #2020: '2020',
                2021: '2021'
            },
            value=[1958, 2021]
        ),
    ], style={'width': '70%', 'margin-left': '60px', 'display': 'inline-block'}),

    # long generic survey
    # html.Iframe(src="https://ubc.ca1.qualtrics.com/jfe/form/SV_3yiBycgV0t8YhCu", style={"height": "800px", "width": "100%"}), 
    # short generic survey: 
    # html.Iframe(src="https://ubc.ca1.qualtrics.com/jfe/form/SV_9zS1U0C7odSt76K", style={"height": "800px", "width": "100%"}),


# closing text
    dcc.Markdown(
        children=sources_markdown
    ),
], style={'width': '900px'}
)

# end of layout and definition of controls.
##################################
# The callback function with it's app.callback wrapper.
@app.callback(
    Output('graph', 'figure'),
    Input('line_slope', 'value'),
    Input('line_intcpt', 'value'),
    Input('data_type', 'value'),
    Input('zone', 'value'),
    Input('month_selection', 'value'),
    Input('xlim_slider', 'value')
)
#def update_graph(line_slope, line_intcpt, Data_type, start, end, zone):
def update_graph(line_slope, line_intcpt, data_type, zone, month_selection, xlim_slider):
# construct all the figure's components
    #multiple y axes: https://plotly.com/python/multiple-axes/
    plot = make_subplots(specs=[[{"secondary_y": True}]])

    if month_selection == 'all':
        co2_data_plot = co2_data
        temp_data_plot = temp_data
    else:
        co2_data_plot = co2_data[co2_data['Datetime'].dt.month == month_selection]
        temp_data_plot = temp_data[temp_data['Datetime'].dt.month == month_selection]

    
    l1 = line_slope * (co2_data_plot.date - np.min(co2_data_plot.date)) + line_intcpt

    if 'raw' in data_type:
        plot.add_trace(go.Scatter(x=co2_data_plot.Datetime, y=co2_data_plot.raw_co2, mode='markers',
            line=dict(color='Crimson'), name="CO2 - raw data"), secondary_y=False)
    if 'adj' in data_type:
        plot.add_trace(go.Scatter(x=co2_data_plot.Datetime, y=co2_data_plot.seasonally_adjusted, mode='markers',
            line=dict(color='Orchid'), name="CO2 - seasonally adjusted"), secondary_y=False)
    if 'fit' in data_type:
        plot.add_trace(go.Scatter(x=co2_data_plot.Datetime, y=co2_data_plot.fit, mode='markers',
            line=dict(color='DarkGreen'), name="CO2 - fit"), secondary_y=False)
    if 'adj_fit' in data_type:
        plot.add_trace(go.Scatter(x=co2_data_plot.Datetime, y=co2_data_plot.seasonally_adjusted_fit, mode='markers',
            line=dict(color='MediumTurquoise'), name="CO2 - seasonally adjusted fit"), secondary_y=False)
    
    plot.add_trace(go.Scatter(x=temp_data_plot.Datetime, y=temp_data_plot.Temp, mode='markers',
        line=dict(color='Purple'), name="temperature anomaly"), secondary_y=True)
    
    plot.add_trace(go.Scatter(x=co2_data_plot.Datetime, y=l1, mode='lines',
        line=dict(color='SandyBrown'), name="linear fit"), secondary_y=False)

    plot.update_xaxes(title_text='Date')
    plot.update_yaxes(title_text="ppm", secondary_y=False)
    plot.update_yaxes(title_text="Temperature Anomaly (deg C)", secondary_y=True)
    
    #xlim: https://stackoverflow.com/questions/21423158/how-do-i-change-the-range-of-the-x-axis-with-datetimes-in-matplotlib
    plot.update_xaxes(range=[datetime.date(xlim_slider[0], 1, 15), datetime.date(xlim_slider[1], 12, 15)])

    '''
    if zone == '1st5yrs':
        #plot.update_xaxes(range=[1958, 1963])
        plot.update_yaxes(range=[312, 322], secondary_y=False)

    if zone == 'last5yrs':
        #plot.update_xaxes(range=[2015, 2020])
        plot.update_yaxes(range=[395, 415], secondary_y=False)
    
    if zone == 'alldata':
        #plot.update_xaxes(range=[1955, 2023])
        plot.update_yaxes(range=[310, 440], secondary_y=False)
    '''
    predicted_co2 = predict_co2(line_slope, line_intcpt, 1958, 2030)
    plot.layout.title = f"Predicted CO2 for {2030}: {predicted_co2:1.2f} ppm."

    return plot

if __name__ == '__main__':
    app.run_server(debug=True)
