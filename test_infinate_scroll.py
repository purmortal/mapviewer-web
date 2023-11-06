import dash_ag_grid as dag
from dash import Dash, Input, Output, dcc, html, no_update, callback
import pandas as pd
#
# app = Dash(__name__)
#
# raw_data = {"id": [], "name": []}
# for i in range(0, 1000):
#     raw_data["id"].append(i)
#     raw_data["name"].append(f"{i*3%5}-{i*7%15}-{i%8}")
# # global df
# df = None
#
#
# def gen_table():
#
#     for i in range(0, 10000):
#         raw_data["id"].append(i)
#         raw_data["name"].append(f"{i*3%5}-{i*7%15}-{i%8}")
#
#     df = pd.DataFrame(data=raw_data)
#     return df
#
#
#     # return [
#     #     dag.AgGrid(
#     #         id="infinite-grid",
#     #         # rowData=df.to_dict('records'),
#     #         columnSize="sizeToFit",
#     #         columnDefs=[{"field": "id"}, {"field": "name"}],
#     #         defaultColDef={"sortable": True},
#     #         rowModelType="infinite",
#     #         dashGridOptions={
#     #             # The number of rows rendered outside the viewable area the grid renders.
#     #             "rowBuffer": 0,
#     #             # How many blocks to keep in the store. Default is no limit, so every requested block is kept.
#     #             "maxBlocksInCache": 100,
#     #             "rowSelection": "single",
#     #         },
#     #     ),
#     # ]
#
#
# app.layout = html.Div(
#     children=[
#         html.Button('Show table', id='submit-val', n_clicks=0),
#         html.Div(children=[
#             dag.AgGrid(
#             id="infinite-grid",
#             # rowData=None,
#             columnSize="sizeToFit",
#             columnDefs=[{"field": "id"}, {"field": "name"}],
#             defaultColDef={"sortable": True},
#             rowModelType="infinite",
#             dashGridOptions={
#                 # The number of rows rendered outside the viewable area the grid renders.
#                 "rowBuffer": 0,
#                 # How many blocks to keep in the store. Default is no limit, so every requested block is kept.
#                 "maxBlocksInCache": 1,
#                 "rowSelection": "single",
#             },
#         ),], id='main-table'),
#     ],
#     style={"margin": 20},
# )
#
#
# # @callback(
# #     Output("infinite-output", "children"), Input("infinite-grid", "selectedRows")
# # )
# # def display_selected_car2(selectedRows):
# #     if selectedRows:
# #         return [f"You selected id {s['id']} and name {s['name']}" for s in selectedRows]
# #     return no_update
#
#
# #@callback(
# #     Output('main-table', 'children'),
# #     Input('submit-val', 'n_clicks'),
# # )
# # def show_table(n_clicks):
# #     return gen_table()
#
# @callback(
#     Output("infinite-grid", "getRowsResponse", allow_duplicate=True),
#     # Output("infinite-grid", "rowData"),
#     Input('submit-val', 'n_clicks'),
#     prevent_initial_call=True
# )
# def show_table(n_clicks):
#     df = gen_table()
#     print(df)
#     partial = df.iloc[0 : 100]
#     return {"rowData": partial.to_dict("records"), "rowCount": len(df.index)}
#     # return df.to_dict("records")
#
# @callback(
#     Output("infinite-grid", "getRowsResponse", allow_duplicate=True),
#     Input("infinite-grid", "getRowsRequest"),
#     prevent_initial_call=True,
# )
# def infinite_scroll(request):
#     print('infinite_scroll')
#     df = gen_table()
#     if request is None:
#         return no_update
#     try:
#         print(df == None)
#     except:
#         return no_update
#     partial = df.iloc[request["startRow"] : request["endRow"]]
#     print(partial)
#     return {"rowData": partial.to_dict("records"), "rowCount": len(df.index)}

# import dash_ag_grid as dag
# from dash import Dash, Input, Output, html, callback
# import pandas as pd
#
# app = Dash(__name__)
#
# df = pd.read_csv(
#     "https://raw.githubusercontent.com/plotly/datasets/master/ag-grid/olympic-winners.csv"
# )
# df["index"] = df.index
#
# columnDefs = [
#     {"field": "athlete", "suppressMenu": True},
#     {
#         "field": "age",
#         "filter": "agNumberColumnFilter",
#         "filterParams": {
#             "filterOptions": ["equals", "lessThan", "greaterThan"],
#             "maxNumConditions": 1,
#         },
#     },
#     {
#         "field": "country",
#         "filter": True
#     },
#     {
#         "field": "year",
#         "filter": "agNumberColumnFilter",
#
#     },
#     {"field": "athlete"},
#     {"field": "date"},
#     {"field": "sport", "suppressMenu": True},
#     {"field": "total", "suppressMenu": True},
# ]
#
# defaultColDef = {
#     "flex": 1,
#     "minWidth": 150,
#     "sortable": True,
#     "resizable": True,
#     "floatingFilter": True,
# }
#
# app.layout = html.Div(
#     [
#         dag.AgGrid(
#             id="infinite-row-sort-filter-select",
#             columnDefs=columnDefs,
#             defaultColDef=defaultColDef,
#             rowModelType="infinite",
#             dashGridOptions={
#                 # The number of rows rendered outside the viewable area the grid renders.
#                 "rowBuffer": 0,
#                 # How many blocks to keep in the store. Default is no limit, so every requested block is kept.
#                 "maxBlocksInCache": 2,
#                 "cacheBlockSize": 100,
#                 "cacheOverflowSize": 2,
#                 "maxConcurrentDatasourceRequests": 2,
#                 "infiniteInitialRowCount": 1,
#                 "rowSelection": "multiple",
#             },
#             getRowId="params.data.index",
#         ),
#     ],
# )
#
# operators = {
#     "greaterThanOrEqual": "ge",
#     "lessThanOrEqual": "le",
#     "lessThan": "lt",
#     "greaterThan": "gt",
#     "notEqual": "ne",
#     "equals": "eq",
# }
#
#
# def filter_df(dff, filter_model, col):
#     if "filter" in filter_model:
#         if filter_model["filterType"] == "date":
#             crit1 = filter_model["dateFrom"]
#             crit1 = pd.Series(crit1).astype(dff[col].dtype)[0]
#             if "dateTo" in filter_model:
#                 crit2 = filter_model["dateTo"]
#                 crit2 = pd.Series(crit2).astype(dff[col].dtype)[0]
#         else:
#             crit1 = filter_model["filter"]
#             crit1 = pd.Series(crit1).astype(dff[col].dtype)[0]
#             if "filterTo" in filter_model:
#                 crit2 = filter_model["filterTo"]
#                 crit2 = pd.Series(crit2).astype(dff[col].dtype)[0]
#     if "type" in filter_model:
#         if filter_model["type"] == "contains":
#             dff = dff.loc[dff[col].str.contains(crit1)]
#         elif filter_model["type"] == "notContains":
#             dff = dff.loc[~dff[col].str.contains(crit1)]
#         elif filter_model["type"] == "startsWith":
#             dff = dff.loc[dff[col].str.startswith(crit1)]
#         elif filter_model["type"] == "notStartsWith":
#             dff = dff.loc[~dff[col].str.startswith(crit1)]
#         elif filter_model["type"] == "endsWith":
#             dff = dff.loc[dff[col].str.endswith(crit1)]
#         elif filter_model["type"] == "notEndsWith":
#             dff = dff.loc[~dff[col].str.endswith(crit1)]
#         elif filter_model["type"] == "inRange":
#             if filter_model["filterType"] == "date":
#                 dff = dff.loc[
#                     dff[col].astype("datetime64[ns]").between_time(crit1, crit2)
#                 ]
#             else:
#                 dff = dff.loc[dff[col].between(crit1, crit2)]
#         elif filter_model["type"] == "blank":
#             dff = dff.loc[dff[col].isnull()]
#         elif filter_model["type"] == "notBlank":
#             dff = dff.loc[~dff[col].isnull()]
#         else:
#             dff = dff.loc[getattr(dff[col], operators[filter_model["type"]])(crit1)]
#     elif filter_model["filterType"] == "set":
#         dff = dff.loc[dff[col].astype("string").isin(filter_model["values"])]
#     return dff
#
#
# @callback(
#     Output("infinite-row-sort-filter-select", "getRowsResponse"),
#     Input("infinite-row-sort-filter-select", "getRowsRequest"),
# )
# def infinite_scroll(request):
#     dff = df.copy()
#
#     if request:
#         if request["filterModel"]:
#             filters = request["filterModel"]
#             for f in filters:
#                 try:
#                     if "operator" in filters[f]:
#                         if filters[f]["operator"] == "AND":
#                             dff = filter_df(dff, filters[f]["condition1"], f)
#                             dff = filter_df(dff, filters[f]["condition2"], f)
#                         else:
#                             dff1 = filter_df(dff, filters[f]["condition1"], f)
#                             dff2 = filter_df(dff, filters[f]["condition2"], f)
#                             dff = pd.concat([dff1, dff2])
#                     else:
#                         dff = filter_df(dff, filters[f], f)
#                 except:
#                     pass
#
#         if request["sortModel"]:
#             sorting = []
#             asc = []
#             for sort in request["sortModel"]:
#                 sorting.append(sort["colId"])
#                 if sort["sort"] == "asc":
#                     asc.append(True)
#                 else:
#                     asc.append(False)
#             dff = dff.sort_values(by=sorting, ascending=asc)
#
#         lines = len(dff.index)
#         if lines == 0:
#             lines = 1
#
#         partial = dff.iloc[request["startRow"]: request["endRow"]]
#         return {"rowData": partial.to_dict("records"), "rowCount": lines}
#


from dash import Dash, html, Input, Output, no_update, State, ctx
from dash_ag_grid import AgGrid
import dash_mantine_components as dmc
import pandas as pd


df = pd.read_csv(
        "https://raw.githubusercontent.com/plotly/datasets/master/ag-grid/olympic-winners.csv"
    )
app = Dash()

# basic columns definition with column defaults
columnDefs = [{"field": c} for c in df.columns]

app.layout = html.Div(
    [
        AgGrid(
            id="grid",
            columnDefs=columnDefs,
            defaultColDef={"resizable": True, "sortable": True, "filter": True},
            rowModelType="infinite",
            dashGridOptions={
                # "pagination": True
            },
            style={"height": 900, "width": "100%"},
        ),
        dmc.ChipGroup(
            [dmc.Chip(x, value=x) for x in ["United States", "Afghanistan"]],
            value="United States",
            id="filters",
        ),
        html.Button(id="fire-filters", children="Fire Filters"),
    ]
)


@app.callback(
    Output("grid", "getRowsResponse"),
    Input("grid", "getRowsRequest"),
    State("filters", "value"),
)
def update_grid(request, filters_data):
    if request:
        filtered_df = df[df['country'] == filters_data]

        partial = filtered_df.iloc[request["startRow"]: request["endRow"]]
        return {"rowData": partial.to_dict("records"), "rowCount": len(filtered_df.index)}

app.clientside_callback(
    """function (n) {
        dash_ag_grid.getApi('grid').refreshInfiniteCache()
        return dash_clientside.no_update
    }""",
    Output("fire-filters", "n_clicks"),
    Input("fire-filters", "n_clicks"),
    prevent_initial_call=True
)


if __name__ == '__main__':
    app.run(debug=True)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5810)
