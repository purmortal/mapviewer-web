from loadData import gistDataBase
from plotData import *
from helperFunctions import *
from dash_iconify import DashIconify

from dash import Dash, dcc, callback, Output, Input, ctx, State, no_update
from time import perf_counter as clock
import dash_mantine_components as dmc
import dash_ag_grid as dag
from dash.exceptions import PreventUpdate

import warnings
warnings.filterwarnings("ignore")


# Incorporate data
module_names = ["TABLE", "MASK", "KIN", "GAS", "SFH", "LS"]
module_table_names = ["table", "Mask", "kinResults", "gasResults", "sfhResults", "lsResults"]
global database
database = gistDataBase()


# Initialize the app - incorporate a Dash Mantine theme
external_stylesheets = [dmc.theme.DEFAULT_COLORS]
app = Dash(__name__, external_stylesheets=external_stylesheets)



# Complicated version by coloring the selected row
# def update_dashboard(database):
#     # print({"styleConditions": [{"condition": "params.rowIndex === " + str(database.idxBinShort), "style": {"backgroundColor": "red"}}]})
#     return \
#         plotMap(database, "TABLE", "BIN_ID"), \
#         [
#                     dag.AgGrid(
#                         id="main-table",
#                         rowData=database.kinResults_Vorbin_df.to_dict("records"),
#                         columnDefs=[{"field": "BIN_ID", "pinned": "left", "lockPinned": True}] +
#                                    [{"field": i, "valueFormatter": {"function": "d3.format(",.3f")(params.value)"}} for i in database.kinResults_Vorbin_df.columns if i != "BIN_ID"],
#                         columnSize="sizeToFit",
#                         columnSizeOptions={"defaultMinWidth": 100, "defaultMaxWidth": 200},
#                         defaultColDef={"resizable": True, "sortable": True, "filter": True},
#                         className="ag-theme-balham",
#                         dashGridOptions={"rowSelection":"single"},
#                         style={"height": "55vh"},
#                         getRowStyle={"styleConditions": [{"condition": "params.rowIndex === " + str(database.idxBinShort), "style": {"backgroundColor": "lightcoral"}}]},
#                         ),
#                     html.Div(id="quickclick-output"),
#                 ], \
#         [ dcc.Graph(figure=x, style={"height": "35vh"}) for x in plotSpectra(database) ], \
#         [ dcc.Graph(figure=plotSFH(database), style={"height": "35vh"} ) ] + [ dcc.Graph( figure=x, style={"height": "38vh"} ) for x in plotMDF(database) ]


def create_property_groups(database):
    print("Function call create_property_groups")
    if hasattr(database, "module") == False:
        database.module = "KIN"
    return [
            dmc.SegmentedControl(
                    id="module-select",
                    value=module_table_names[module_names.index(database.module)],
                    data=[{"value": "table", "label": "TABLE"}] +
                         [{"value": module_table_names[i], "label": module_names[i]}
                          for i in range(1, len(module_names)) if getattr(database, module_names[i])],
                    style={"marginTop": 12, "marginBottom": 12},
                ),
            dmc.Select(
                placeholder="choose a parameter",
                id="parameter-select",
                data=[{"value": parameter_i, "label": parameter_i}
                      for parameter_i in getattr(database, module_table_names[module_names.index(database.module)]).names],
                style={"width": 200, "marginTop": 12, "marginBottom": 12},
                maxDropdownHeight=500,
            )
        ]

# def update_main_table_columnDefs(database):
#     return [{"field": i} for i in database.current_df.columns]
def create_main_table(database, value):
    print("Function call create_main_table")
    if value in ["table", "Mask"]:
        database.current_df = getattr(database, value+"_df")
        # columnSize = None
        # columnSizeOptions = None
        # defaultColDef={"resizable": False, "sortable": True}

    else:
        database.current_df = getattr(database, value+"_Vorbin_df")
        # columnSize = "sizeToFit"
        # columnSizeOptions={
        #     "defaultMinWidth": 120,
        # }
        # defaultColDef={"resizable": True, "sortable": True},

    # columnDefs = []
    # if "ID" in database.current_df.columns:
    #     columnDefs += [{"field": "ID", "pinned": "left", "lockPinned": True}]
    # if "BIN_ID" in database.current_df.columns:
    #     columnDefs += [{"field": "BIN_ID", "pinned": "left", "lockPinned": True}]
    # columnDefs += [{"field": i, "valueFormatter": {"function": "d3.format('.3f')(params.value)"}}
    #                for i in database.current_df.columns if i != "BIN_ID" and i != "ID"]
    # columnDefs += [{"field": i}
    #                for i in database.current_df.columns if i != "BIN_ID" and i != "ID"]
    # columnDefs=[{"field": i} for i in database.current_df.columns]
    return  dag.AgGrid(
        id="main-table",
        rowData=database.current_df.to_dict("records"),
        columnDefs=[{"field": i} for i in database.current_df.columns],
        columnSize="sizeToFit",
        # scrollTo={"rowPosition":"bottom"},
        columnSizeOptions={
            "defaultMinWidth": 120,
        },
        defaultColDef={"resizable": True, "sortable": True},
        rowModelType="infinite",
        className="ag-theme-balham",
        dashGridOptions={
           "rowBuffer": 0,
           "maxBlocksInCache": 1,
           # "cacheBlockSize": 100,
           # "cacheOverflowSize": 2,
           # "maxConcurrentDatasourceRequests": 1,
           "infiniteInitialRowCount": 40,
           "rowSelection":"single",
            # "pagination": True,
            # "paginationAutoPageSize": True
        },
        style={"height": "55vh"},
    )

def create_main_map(database):
    print("Function call create_main_map")
    return dcc.Graph(id="main-map",
                 figure=plotMap(database, database.module, database.maptype),
                 style={"height": "55vh"},
                 )

def update_dashboard(database):
    print("Function call update_dashboard")
    # if hasattr(database, "fig_plotMap") == False:
    #     fig_plotMap = plotMap(database, database.module, database.maptype)
    #     print("Create new fig_plotMap")
    # else:
    #     fig_plotMap = database.fig_plotMap
    #     print("found existing fig_plotMap")

    # print({"styleConditions": [{"condition": "params.rowIndex === " + str(database.idxBinShort), "style": {"backgroundColor": "red"}}]})
    if hasattr(database, "idxBinLong") == True and hasattr(database, "idxBinShort") == True:
        if database.idxBinShort < 0:
                return \
                    plotMap(database, database.module, database.maptype), \
                    None, \
                    None

    return \
        plotMap(database, database.module, database.maptype), \
        [ dcc.Graph(figure=x, style={"height": "35vh"}) for x in plotSpectra(database) ], \
        [ dcc.Graph(figure=plotSFH(database), style={"height": "35vh"} ) ] + [ dcc.Graph( figure=x, style={"height": "35vh"} ) for x in plotMDF(database) ]



# App layout
app.layout = dmc.Container([
    dmc.Title("MapViewer-Web 1.0", color="blue", size="h3"),
    dmc.Grid(
        children=[
            dmc.Col(
                children=[
                    dmc.Group(
                        children=[
                            dmc.TextInput(
                                style={"width": "60vh"},
                                placeholder="please input your GIST directory path",
                                id="data-directory-ptah",
                            ),
                            dmc.Button(
                                id="load-data",
                                children="Load from database",
                                leftIcon=DashIconify(icon="fluent:database-plug-connected-20-filled"),
                                style={"marginTop": 12, "marginBottom": 12}
                            ),
                        ],
                    ),
                ],
                span=6
            ),
            dmc.Col(
                children=[
                    dmc.Group(
                        children=[
                            dmc.SegmentedControl(
                                id="module-select",
                                data = [{"value": "tem", "label": "No data loaded"}],
                                style={"marginTop": 12, "marginBottom": 12},
                            ),
                            dmc.Select(
                                id="parameter-select",
                                style={"width": 200, "marginTop": 12, "marginBottom": 12},
                                maxDropdownHeight=500,
                            ),
                        ],
                        align="inherit",
                        id="property-selections",
                        # position="apart",
                    ),
                ],
                span=6,
                )
        ],
    ),
    dmc.Grid(
        children=[
            dmc.Col(
                id="child-main-map",
                children=[dcc.Graph(id="main-map")],
                span=6,
            ),
            dmc.Col(
                id="child-main-table",
                children=[dag.AgGrid(id="main-table")],
                span=6,
            ),
        ],
        justify="center",
        align="stretch",
        gutter="sm",
        id="children-main-info",
    ),

    dmc.Grid(
        children=[
            dmc.Col(
                id="plot-spec-map",
                span=8,),
            dmc.Col(
                id="plot-mfd-map",
                span=4,),
        ],
        justify="space-around",
        align="flex-start",
        gutter="md",
        id="spec-inspect",
    ),

], fluid=True)


@callback(
    # Output("child-main-table", "children"),
    # Output("child-main-map", "children"),
    # Output("parameter-select", "data"),
    Output("property-selections", "children"),
    Output("children-main-info", "children"),
    Output("spec-inspect", "children"),
    Input("load-data", "n_clicks"),
    State("data-directory-ptah", "value"),
    prevent_initial_call=True
)
def load_selects(n_clicks, path_gist_run):
    print("----------------------------------")
    print("Interactivity call load_selects")
    # print("select_module", value)
    # names = getattr(database, value).names
    # database.module = modules[results.index(value)]
    # print(value)
    # print(type(value))
    # path_gist_run = "/home/zwan0382/Documents/projects/mapviewer-web/NGC0000Example"
    # path_gist_run = "/home/zwan0382/Documents/projects/mapviewer-web/resultsRevisedREr5"
    print(path_gist_run)
    # database = gistDataBase()
    database.reset()
    database.loadData(path_gist_run)
    return create_property_groups(database), \
        [
            dmc.Col(
                id="child-main-map",
                children=[
                    dcc.Graph(
                        id="main-map",
                        style={"height": "55vh"},
                    )
                ],
                span=6,
            ),
            dmc.Col(
                id="child-main-table",
                children=[dag.AgGrid(id="main-table")],
                span=6,
            ),
            # dmc.Col(
            #     id="child-main-table",
            #     children=[
            #         dag.AgGrid(
            #             id="main-table",
            #             columnSize="sizeToFit",
            #             columnSizeOptions={
            #                 "defaultMinWidth": 110,
            #                 # "defaultMaxWidth": 111,
            #             },
            #             defaultColDef={"resizable": True, "sortable": True},
            #             rowModelType="infinite",
            #             className="ag-theme-balham",
            #             dashGridOptions={
            #                 "rowBuffer": 0,
            #                 "maxBlocksInCache": 1,
            #                 "infiniteInitialRowCount": 40,
            #                 "rowSelection":"single",
            #             },
            #             style={"height": "55vh"},
            #             )
            #     ],
            #     span=6,
            # ),
        ], \
        [
            dmc.Col(
                id="plot-spec-map",
                span=8,),
            dmc.Col(
                id="plot-mfd-map",
                span=4,),
        ]
    # return create_property_groups(database), [create_main_table(database, database.module)], [create_main_map(database)]


@callback(
    Output("child-main-table", "children"),
    # Output("main-table", "rowData"),
    # Output("main-table", "columnDefs"),
    # Output("main-table", "columnSize"),
    # Output("main-table", "columnSizeOptions"),
    Output("parameter-select", "data"),
    Output("parameter-select", "value"),
    Input("module-select", "value"),
    prevent_initial_call=True
)
def select_module(value):
    print("Interactivity call select_module")
    print("select_module", value)
    names = getattr(database, value).names
    database.module = module_names[module_table_names.index(value)]
    return [create_main_table(database, value)], [{"value": parameter_i, "label": parameter_i} for parameter_i in names], names[0]
    # return database.current_df.to_dict("records"), columnDefs, "sizeToFit", {"defaultMinWidth": 115}, \
    #     [{"value": parameter_i, "label": parameter_i} for parameter_i in names], names[0]

@callback(
    Output("child-main-map", "children"),
    Input("parameter-select", "value"),
    prevent_initial_call=True
)
def select_parameter(value):
    print("Interactivity call select_parameter")
    print(["select_parameter", value])
    if value == None:
        raise PreventUpdate
    database.maptype = value
    print(["database", database.module, database.maptype])
    return [create_main_map(database)]

# @callback(
#     Output("main-table", "getRowsResponse"),
#     Input("main-table", "getRowsRequest"),
#     prevent_initial_call=True,
# )
# def infinite_scroll(request):
#     print("Interactivity call infinite_scroll")
#     print(request)
#     # time.sleep(2)
#     if request is None:
#         return no_update
#     partial = database.current_df.iloc[request["startRow"] : request["endRow"]]
#     print(partial)
#     return {"rowData": partial.to_dict("records"), "rowCount": len(database.current_df.index)}



@callback(
    Output("main-map", "figure"),
    Output("plot-spec-map", "children"),
    Output("plot-mfd-map", "children"),
    Input("main-map", "clickData"),
    Input("main-table", "cellClicked"),
    prevent_initial_call=True
)
def display_click_vorbin(clickData, cellClicked):
    print("Interactivity call display_click_vorbin")
    triggered_id = ctx.triggered_id
    if triggered_id == "main-map":
        if clickData == None:
            raise PreventUpdate
        else:
            remove_idxBin(database)
            database.idxBinLong, database.idxBinShort = getVoronoiBin(database, clickData["points"][0]["x"], clickData["points"][0]["y"])
            return update_dashboard(database)
    elif triggered_id == "main-table":
        if cellClicked == None:
            raise PreventUpdate
        else:
            remove_idxBin(database)
            if database.module in ['TABLE', 'MASK']:
                database.idxBinLong = int(cellClicked["rowId"])
                database.idxBinShort = database.table['BIN_ID'][database.idxBinLong]
            else:
                database.idxBinShort = int(cellClicked["rowId"])
            return update_dashboard(database)




# Run the App
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5801)
