from DataLoader import gistDataBase
from plotData import *
from helperFunctions import *
import json

from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
from astropy.table import Table
# import plotly.express as px
import dash_mantine_components as dmc
import dash_ag_grid as dag

import warnings
warnings.filterwarnings("ignore")

path_gist_run = '/home/zwan0382/Documents/projects/mapviewer-web/NGC0000Example'
# path_gist_run = '/home/zwan0382/Documents/projects/mapviewer-web/resultsRevisedREr5'
database = gistDataBase(path_gist_run)
database.loadData()

# Incorporate data
df = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/gapminder2007.csv")

# Initialize the app - incorporate a Dash Mantine theme
external_stylesheets = [dmc.theme.DEFAULT_COLORS]
app = Dash(__name__, external_stylesheets=external_stylesheets)

# App layout
app.layout = dmc.Container([
    dmc.Title('My First App with Data, Graph, and Controls', color="blue", size="h3"),
    # dmc.RadioGroup([dmc.Radio(i, value=i) for i in  ['pop', 'lifeExp', 'gdpPercap']], id='my-dmc-radio-item', value='lifeExp', size="sm"),
    dmc.Grid(
        children=[
            dmc.Col(
                children=[
                    dcc.Graph(id='interaction-click',
                              figure=plotMap(database, 'KIN', 'V'),
                              style={'height': '55vh'},
                              ),
                ],
                span=6,
            ),
            dmc.Col(
                children=[
                    dag.AgGrid(
                        rowData=Table(database.kinResults_Vorbin).to_pandas().to_dict('records'),
                        columnDefs=[{"headerName": "BIN_ID", "valueGetter": {"function": "params.node.id"}, "pinned": "left", "lockPinned": True}] +
                                   [{"field": i, "valueFormatter": {"function": "d3.format(',.3f')(params.value)"}} for i in Table(database.kinResults_Vorbin).to_pandas().columns],
                        columnSize="autoSize",
                        defaultColDef={"resizable": True, "sortable": True, "filter": True},
                        className="ag-theme-balham",
                        dashGridOptions={"rowSelection":"single"},
                        style={'height': '55vh'},
                        # getRowId="params.data.id",
                        )
                ],
                span=6,),
        ],
        justify='center',
        align='stretch',
        gutter='md',
    ),

    dmc.Grid(
        id = 'click-data', children=[],
        justify='space-around',
        align='flex-start',
        gutter='md',
    ),
], fluid=True)


@callback(
    Output('click-data', 'children'),
    Input('interaction-click', 'clickData'))
def display_click_data(clickData):
    idxBinLong, idxBinShort = getVoronoiBin(database, clickData['points'][0]['x'], clickData['points'][0]['y'])
    return [
            dmc.Col(
                children=[
                             dcc.Graph(
                                 figure=x,
                                 style={'height': '38vh'}
                             )
                             for x in plotSpectra(database, idxBinShort, idxBinLong)
                ],
                span=8,),
            dmc.Col(
                children=[
                             dcc.Graph(
                                 figure=plotSFH(database, idxBinShort, idxBinLong),
                                 style={'height': '38vh'}
                             )
                         ] +
                         [
                             dcc.Graph(
                                 figure=x,
                                 style={'height': '38vh'}
                             )
                             for x in plotMDF(database, idxBinShort)
                         ],
                span=4,),
        ]




# # Add controls to build the interaction
# @callback(
#     Output(component_id='graph-placeholder', component_property='figure'),
#     Input(component_id='my-dmc-radio-item', component_property='value')
# )
# def update_graph(col_chosen):
#     fig = px.histogram(df, x='continent', y=col_chosen, histfunc='avg')
#     return fig



# Run the App
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5800)
