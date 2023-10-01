from DataLoader import gistDataBase
from plotData import *


from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
from astropy.table import Table
# import plotly.express as px
import dash_mantine_components as dmc
import dash_ag_grid as dag


path_gist_run = '/home/zwan0382/Documents/projects/mapviewer-web/NGC0000Example'
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
                    dcc.Graph(figure=plotMap(database, 'KIN', 'V'))],
                span=6,),

            # dmc.Col(
            #     children=[
            #         dash_table.DataTable(
            #             data=Table(database.kinResults_Vorbin).to_pandas().round(3).to_dict('records'),
            #             fixed_rows={'headers': True},
            #             # page_size=12,
            #             page_action='none',
            #             style_table={'height': 400, 'overflowY': 'auto'},
            #             style_cell={'textAlign': 'center'},
            #             # sort_action='custom',
            #             # sort_mode='single',
            #             # sort_by=[]
            #             style_data_conditional=[
            #                 {
            #                     'if': {'row_index': 'odd'},
            #                     'backgroundColor': 'rgb(220, 220, 220)',
            #                 }
            #             ],
            #             style_header={
            #                 'backgroundColor': 'rgb(210, 210, 210)',
            #                 'color': 'black',
            #                 'fontWeight': 'bold'
            #             }
            #         )],
            #     span=6),
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
        children=[
            dmc.Col(
                children=[
                    dcc.Graph(
                        figure=plotSpectraKIN(database, database.Spectra[1], database.kinBestfit[1], database.kinGoodpix),
                        style={'height': '38vh'})],
                span=8,),
            dmc.Col(
                children=[
                    dcc.Graph(
                        figure=plotSFH(database, idxBinShort=0),
                        style={'height': '38vh'})],
                span=4,),

            dmc.Col(
                children=[
                    dcc.Graph(
                        figure=plotSpectraGAS(database, database.Spectra[1], database.gasBestfit[1], database.kinGoodpix, 0, 0),
                        style={'height': '38vh'})],
                span=8,),
            dmc.Col(
                children=[
                    dcc.Graph(
                        figure=plotMDF(database, idxBinShort=0, idx_alpha=0),
                        style={'height': '38vh'})],
                span=4,),

            dmc.Col(
                children=[
                    dcc.Graph(
                        figure=plotSpectraSFH(database, database.Spectra[1], database.sfhBestfit[1], database.kinGoodpix, 0, 0),
                        style={'height': '38vh'})],
                span=8,),
            # dmc.Col(
            #     children=[
            #         dcc.Graph(
            #             figure=plotMDF(database, idxBinShort=0, idx_alpha=1),
            #             style={'height': '38vh'})],
            #     span=4,),
        ],
        justify='space-between',
        align='center',
        gutter='md',
    ),
], fluid=True)

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
