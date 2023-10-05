from loadData import gistDataBase
from plotData import *
from helperFunctions import *
from dash_iconify import DashIconify
import json

from dash import Dash, html, dash_table, dcc, callback, Output, Input, ctx
import pandas as pd
from astropy.table import Table
# import plotly.express as px
import dash_mantine_components as dmc
import dash_ag_grid as dag
from dash.exceptions import PreventUpdate

import warnings
warnings.filterwarnings("ignore")


def create_main_table(database, value):
    if value in ['table', 'Mask']:
        df_module = Table(getattr(database, value)).to_pandas()

    else:
        df_module = getattr(database, value+'_Vorbin_df')

    columnDefs = []
    if 'ID' in df_module.columns:
        columnDefs += [{"field": "ID", "pinned": "left", "lockPinned": True}]
    if 'BIN_ID' in df_module.columns:
        columnDefs += [{"field": "BIN_ID", "pinned": "left", "lockPinned": True}]
    columnDefs += [{"field": i, "valueFormatter": {"function": "d3.format(',.3f')(params.value)"}}
                   for i in df_module.columns if i != 'BIN_ID' and i != 'ID']
        # columnDefs=[{"field": i, "valueFormatter": {"function": "d3.format(',.3f')(params.value)"}} for i in df_module.columns]
    return  dag.AgGrid(id='main-table',
                       rowData=df_module.to_dict('records'),
                       columnDefs=columnDefs,
                       columnSize="sizeToFit",
                       columnSizeOptions={'defaultMinWidth': 100, 'defaultMaxWidth': 200},
                       defaultColDef={"resizable": True, "sortable": True, "filter": True},
                       className="ag-theme-balham",
                       dashGridOptions={"rowSelection":"single"},
                       style={'height': '55vh'},
                       )

def create_main_map(database):
    return dcc.Graph(id='main-map',
                 figure=plotMap(database, database.module, database.maptype),
                 style={'height': '55vh'},
                 )

def update_dashboard(database):
    # print({"styleConditions": [{"condition": "params.rowIndex === " + str(database.idxBinShort), "style": {"backgroundColor": "red"}}]})
    return \
        [ create_main_map(database) ], \
        [ dcc.Graph(figure=x, style={'height': '35vh'}) for x in plotSpectra(database) ], \
        [ dcc.Graph(figure=plotSFH(database), style={'height': '35vh'} ) ] + [ dcc.Graph( figure=x, style={'height': '38vh'} ) for x in plotMDF(database) ]



modules = ['TABLE', 'MASK', 'KIN', 'GAS', 'SFH', 'LS']
results = ['table', 'Mask', 'kinResults', 'gasResults', 'sfhResults', 'lsResults']

# Incorporate data
path_gist_run = '/home/zwan0382/Documents/projects/mapviewer-web/NGC0000Example'
# path_gist_run = '/home/zwan0382/Documents/projects/mapviewer-web/resultsRevisedREr5'
database = gistDataBase(path_gist_run)
database.loadData()
database.module = "TABLE"
database.maptype = "FLUX"
print('initial', database.module)
print('initial', database.maptype)
# df = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/gapminder2007.csv")


# Initialize the app - incorporate a Dash Mantine theme
external_stylesheets = [dmc.theme.DEFAULT_COLORS]
app = Dash(__name__, external_stylesheets=external_stylesheets)


# App layout
app.layout = dmc.Container([
    dmc.Title('My First App with Data, Graph, and Controls', color="blue", size="h3"),
    dmc.Group(
        [
            dmc.Button(
                "Load from database",
                leftIcon=DashIconify(icon="fluent:database-plug-connected-20-filled"),
                id="loading-button",
                style={"marginTop": 12, "marginBottom": 12}
            ),
            dmc.SegmentedControl(
                    id="module-select",
                    value=results[modules.index(database.module)],
                    # value='table',
                    data=[{"value": 'table', "label": 'TABLE'}] +
                         [{"value": results[i], "label": modules[i]}
                          for i in range(1, len(modules)) if getattr(database, modules[i])],
                    style={"marginTop": 12, "marginBottom": 12},
                ),
            dmc.Select(
                placeholder="choose a parameter",
                id="parameter-select",
                data=[{"value": parameter_i, "label": parameter_i}
                      for parameter_i in getattr(database, results[modules.index(database.module)]).names],
                value=database.maptype,
                # value='FLUX',
                style={"width": 200, "marginTop": 12, "marginBottom": 12},
                maxDropdownHeight=500,
            )
        ],
        align='inherit',
    ),
    # dmc.RadioGroup(
    #     [dmc.Radio(l, value=k) for k, l in data],
    #     id="radiogroup-simple",
    #     value="react",
    #     label="Select your favorite framework/library",
    #     size="sm",
    #     mt=10,
    # ),
    # dmc.Grid(
    #     children=[
    #         dmc.Col(
    #             children=[
    #                 dmc.Button(
    #                     "Load from database",
    #                     # leftIcon=DashIconify(icon="fluent:database-plug-connected-20-filled"),
    #                     id="loading-button",
    #                 ),
    #             ],
    #             span="auto"
    #         ),
    #         dmc.Col(
    #             children=[
    #                 dmc.ButtonGroup(
    #                     [dmc.Button('Table', variant='outline')] +
    #                     [dmc.Button(menu_i, variant='outline') for menu_i in menus[1:] if getattr(database, menu_i)]
    #                     ),
    #             ],
    #             span="auto",
    #         ),
    #     ],
    #     justify='flex-start',
    #     align='flex-start',
    # ),
    # dmc.RadioGroup([dmc.Radio(i, value=i) for i in  ['pop', 'lifeExp', 'gdpPercap']], id='my-dmc-radio-item', value='lifeExp', size="sm"),
    dmc.Grid(
        children=[
            dmc.Col(
                id='child-main-map',
                children=[create_main_map(database)],
                span=6,
            ),
            dmc.Col(
                id='child-main-table',
                children=[
                    create_main_table(database, results[modules.index(database.module)]),
                    # html.Div(id="quickclick-output"),
                ],
                span=6,),
        ],
        justify='center',
        align='stretch',
        gutter='sm',
    ),

    dmc.Grid(
        children=[
            dmc.Col(
                id='plot-spec-map',
                span=8,),
            dmc.Col(
                id='plot-mfd-map',
                span=4,),
        ],
        justify='space-around',
        align='flex-start',
        gutter='md',
    ),

], fluid=True)




# Complicated version by coloring the selected row
# def update_dashboard(database):
#     # print({"styleConditions": [{"condition": "params.rowIndex === " + str(database.idxBinShort), "style": {"backgroundColor": "red"}}]})
#     return \
#         plotMap(database, 'TABLE', 'BIN_ID'), \
#         [
#                     dag.AgGrid(
#                         id='main-table',
#                         rowData=database.kinResults_Vorbin_df.to_dict('records'),
#                         columnDefs=[{"field": "BIN_ID", "pinned": "left", "lockPinned": True}] +
#                                    [{"field": i, "valueFormatter": {"function": "d3.format(',.3f')(params.value)"}} for i in database.kinResults_Vorbin_df.columns if i != 'BIN_ID'],
#                         columnSize="sizeToFit",
#                         columnSizeOptions={'defaultMinWidth': 100, 'defaultMaxWidth': 200},
#                         defaultColDef={"resizable": True, "sortable": True, "filter": True},
#                         className="ag-theme-balham",
#                         dashGridOptions={"rowSelection":"single"},
#                         style={'height': '55vh'},
#                         getRowStyle={"styleConditions": [{"condition": "params.rowIndex === " + str(database.idxBinShort), "style": {"backgroundColor": "lightcoral"}}]},
#                         ),
#                     html.Div(id="quickclick-output"),
#                 ], \
#         [ dcc.Graph(figure=x, style={'height': '35vh'}) for x in plotSpectra(database) ], \
#         [ dcc.Graph(figure=plotSFH(database), style={'height': '35vh'} ) ] + [ dcc.Graph( figure=x, style={'height': '38vh'} ) for x in plotMDF(database) ]



@callback(
    Output('child-main-table', 'children'),
    Output("parameter-select", "data"),
    Output("parameter-select", "value"),
    Input("module-select", "value"),
    prevent_initial_call=True
)
def select_module(value):
    print('select_module', value)
    names = getattr(database, value).names
    database.module = modules[results.index(value)]
    return [create_main_table(database, value)], [{"value": parameter_i, "label": parameter_i} for parameter_i in names], names[0]


@callback(
    Output('child-main-map', 'children'),
    Input("parameter-select", "value"),
    # prevent_initial_call=True
)
def select_parameter(value):
    print(['select_parameter', value])
    if value == None:
        raise PreventUpdate
    database.maptype = value
    print(['database', database.module, database.maptype])
    return [create_main_map(database)]



@callback(
    Output('child-main-map', 'children', allow_duplicate=True),
    # Output('child-main-table', 'children'),
    Output('plot-spec-map', 'children'),
    Output('plot-mfd-map', 'children'),
    Input('main-map', 'clickData'),
    Input("main-table", "cellClicked"),
    prevent_initial_call=True
)
def display_click_vorbin(clickData, cellClicked):
    triggered_id = ctx.triggered_id
    if triggered_id == 'main-map':
        if clickData == None:
            raise PreventUpdate
        else:
            database.idxBinLong, database.idxBinShort = getVoronoiBin(database, clickData['points'][0]['x'], clickData['points'][0]['y'])
            print(database.idxBinLong, database.idxBinShort)
            return update_dashboard(database)
    elif triggered_id == 'main-table':
        if cellClicked == None:
            raise PreventUpdate
        else:
            database.idxBinLong, database.idxBinShort = None, int(cellClicked['rowId'])
            print(database.idxBinLong, database.idxBinShort)
            return update_dashboard(database)



# @app.callback(
#     Output("quickclick-output", "children"),
#     Input("main-table", "cellClicked")
# )
# def display_cell_clicked_on(cellClicked):
#     if cellClicked is None:
#         return f"No data selected"
#     return f"clicked on cell value:  {cellClicked['value']}, column:   {cellClicked['colId']}, BIN_ID:   {cellClicked['rowId']}"


# @app.callback(
#     Output('main-map', 'figure'),
#     Output('plot-spec-map', 'children'),
#     Output('plot-mfd-map', 'children'),
#     Input("main-table", "cellDoubleClicked")
# )
# def display_cell_doubleclicked_on(cell):
#     if cell is None:
#         raise PreventUpdate
#     database.idxBinShort = int(cell['rowId'])
#     return update_figures(database)


# Run the App
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5800)
