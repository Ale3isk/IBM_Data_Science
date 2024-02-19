#import necessary libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import plotly.express as px
from dash import no_update
import datetime as dt
import requests
from io import StringIO

# store the URL where the dataset is
url = "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-DV0101EN-SkillsNetwork/Data%20Files/historical_automobile_sales.csv"

response = requests.get(url)

# if the request is successfull
if response.status_code == 200:
    print("Request sucessfull!")
    content = response.content

    # Create a StringIO object from the raw binary data
    # This allows pandas to read the CSV directly from memory
    csv_data = StringIO(content.decode('utf-8'))

    # create the dataframe
    df = pd.read_csv(csv_data)
    print("Data Frame created.")
else:
    print("Something's wrong.")

# create a list for years
year_list = [i for i in range(1980, 2024, 1)]

# create a dash application
app = dash.Dash(__name__)

# Clear the layout and do not display exception till callback gets executed
app.config.suppress_callback_exceptions = True

# Define the layout
app.layout = html.Div(children=([html.H1("Automobile Sales Statistics Dashboard",
                                         style={'textAlign': 'center',
                                                'color': '#503D36',
                                                'font-size': 24}),

                                 dcc.Dropdown(id="dropdown-menu",
                                              options=[{'label': 'Yearly Statistics', 'value': 'Yearly Statistics'},
                                                       {'label': 'Recession Period Statistics',
                                                        'value': 'Recession Period Statistics'}

                                                       ],
                                              placeholder='Select a report',
                                              style={
                                                  'width': '80%',  # set width as 80%
                                                  'padding': '3px',  # set padding as 3px
                                                  'fontsize': '20px',  # set font size as 20px
                                                  'textAlignLast': 'center'  # set text-align0last as center
                                              }
                                              ),
                                 dcc.Dropdown(id='Year',
                                              options=[{'label': i, 'value': i} for i in year_list],
                                              placeholder='select-year',
                                              style={
                                                  'width': '80%',  # set width as 80%
                                                  'padding': '3px',  # set padding as 3px
                                                  'fontsize': '20px',  # set font size as 20px
                                                  'textAlignLast': 'center'  # set text-align-last as center
                                              }

                                              ),
                                 html.Div([
                                     html.Div(id='output-container',
                                              className='chart-grid',
                                              style={'display': 'flex'})
                                 ])

                                 ]
)
                      )


@app.callback(
    Output(component_id='Year', component_property='disabled'),
    Input(component_id='dropdown-menu', component_property='value')
)
def update_input_container(selected_statistics):
    if selected_statistics == 'Yearly Statistics':
        return False
    else:
        return True


@app.callback(
    Output(component_id='output-container', component_property='children'),
    [Input(component_id='dropdown-menu', component_property='value'),
     Input(component_id='Year', component_property='value')]
)
def update_output_container(selected_report, year):
    if selected_report == 'Recession Period Statistics':
        # Filter the data for recession periods
        recession_data = df[df['Recession'] == 1]

        # Plot 1 Automobile sales fluctuate over Recession Period (year wise) using line chart
        # grouping data for plotting
        yearly_rec = recession_data.groupby('Year')['Automobile_Sales'].mean().reset_index()
        # plotting the graph
        R_chart1 = dcc.Graph(
            figure=px.line(yearly_rec, x='Year',
                           y='Automobile_Sales',
                           title="Yearly Automobile Sales"))

        # Plot 2 Calculate the average number of vehicles sold by vehicle type and represent as a Bar chart
        R_chart2 = dcc.Graph(
            figure=px.bar(recession_data,
                          x='Vehicle_Type',
                          y='Automobile_Sales',
                          title="Average Number of Vehicles Sold per Vehicle Type"))

        # Plot 3 : Pie chart for total expenditure share by vehicle type during recessions
        # grouping data for plotting
        exp_rec = recession_data.groupby('Vehicle_Type')["Advertising_Expenditure"].sum().reset_index()
        R_chart3 = dcc.Graph(figure=px.pie(exp_rec,
                                           names='Vehicle_Type',
                                           values='Advertising_Expenditure',
                                           title="Advertising Expenditure per Vehicle Type"))

        # Plot 4 Develop a Bar chart for the effect of unemployment rate on vehicle type and sales

        R_chart4 = dcc.Graph(figure=px.bar(recession_data,
                                           x="Vehicle_Type",
                                           y='Automobile_Sales',
                                           color='unemployment_rate',
                                           title="Effect of Unemployment Rate on Vehicle Type and Sales",
                                           barmode='group'))

        return [
            html.Div(className='chart-item', children=[html.Div(children=R_chart1), html.Div(children=R_chart2)]),
            html.Div(className='chart-item', children=[html.Div(children=R_chart3), html.Div(children=R_chart4)])
        ]




    elif (year and selected_report == 'Yearly Statistics'):
        yearly_data = df[df['Year'] == year]

        # Plot 1 :Yearly Automobile sales using line chart for the whole period.
        yas = df.groupby('Year')['Automobile_Sales'].mean().reset_index()
        R_chart1 = dcc.Graph(
            figure=px.line(yas, x='Year',
                           y='Automobile_Sales',
                           title="Total Automobile Sales for the Whole Period"))

        # Plot 2 :Total Monthly Automobile sales using line chart.

        month = df.groupby('Month')['Automobile_Sales'].sum().reset_index()
        R_chart2 = dcc.Graph(
            figure=px.line(month,
                           x='Month',
                           y='Automobile_Sales',
                           title=f"Total Automobile Sales per Month in Year {year}"))

        # Plot bar chart for average number of vehicles sold during the given year

        avr_vdata = yearly_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()

        R_chart3 = dcc.Graph(
            figure=px.bar(avr_vdata,
                          x='Vehicle_Type',
                          y='Automobile_Sales',
                          title=f"Average Sales per Vehicle Type in year {year}",
                          color='Vehicle_Type'

                          ))

        # Plot 4 Total Advertisement Expenditure for each vehicle using pie chart

        total = yearly_data.groupby('Vehicle_Type')['Automobile_Sales'].sum().reset_index()

        R_chart4 = dcc.Graph(
            figure=px.pie(total,
                          names='Vehicle_Type',
                          values='Automobile_Sales',
                          title=f"Total Sales per Vehicle in {year}"
                          ))

        return [
            html.Div(className='chart-item', children=[html.Div(children=R_chart1), html.Div(children=R_chart2)]),
            html.Div(className='chart-item', children=[html.Div(children=R_chart3), html.Div(children=R_chart4)])
        ]


if __name__ == '__main__':
    app.run_server()

