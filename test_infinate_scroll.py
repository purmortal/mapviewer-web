import dash_ag_grid as dag
from dash import Dash, Input, Output, dcc, html, no_update, callback
import pandas as pd

app = Dash(__name__)

raw_data = {"id": [], "name": []}
for i in range(0, 10):
    raw_data["id"].append(i)
    raw_data["name"].append(f"{i*3%5}-{i*7%15}-{i%8}")
global df
df = pd.DataFrame(data=raw_data)


def gen_table():

    for i in range(0, 10000):
        raw_data["id"].append(i)
        raw_data["name"].append(f"{i*3%5}-{i*7%15}-{i%8}")

    df = pd.DataFrame(data=raw_data)


    return [
        dag.AgGrid(
            id="infinite-grid",
            # rowData=df.to_dict('records'),
            columnSize="sizeToFit",
            columnDefs=[{"field": "id"}, {"field": "name"}],
            defaultColDef={"sortable": True},
            rowModelType="infinite",
            dashGridOptions={
                # The number of rows rendered outside the viewable area the grid renders.
                "rowBuffer": 0,
                # How many blocks to keep in the store. Default is no limit, so every requested block is kept.
                "maxBlocksInCache": 100,
                "rowSelection": "single",
            },
        ),
    ]


app.layout = html.Div(
    children=[
        html.Button('Show table', id='submit-val', n_clicks=0),
        html.Div(children=[
            dag.AgGrid(
            id="infinite-grid",
            # rowData=df.to_dict('records'),
            columnSize="sizeToFit",
            columnDefs=[{"field": "id"}, {"field": "name"}],
            defaultColDef={"sortable": True},
            rowModelType="infinite",
            dashGridOptions={
                # The number of rows rendered outside the viewable area the grid renders.
                "rowBuffer": 0,
                # How many blocks to keep in the store. Default is no limit, so every requested block is kept.
                "maxBlocksInCache": 100,
                "rowSelection": "single",
            },
        ),], id='main-table'),
    ],
    style={"margin": 20},
)


# @callback(
#     Output("infinite-output", "children"), Input("infinite-grid", "selectedRows")
# )
# def display_selected_car2(selectedRows):
#     if selectedRows:
#         return [f"You selected id {s['id']} and name {s['name']}" for s in selectedRows]
#     return no_update


@callback(
    Output('main-table', 'children'),
    Input('submit-val', 'n_clicks'),
)
def show_table(n_clicks):
    return gen_table()

@callback(
    Output("infinite-grid", "getRowsResponse"),
    Input("infinite-grid", "getRowsRequest"),
    prevent_initial_call=True,
)
def infinite_scroll(request):
    print('infinite_scroll')

    if request is None:
        return no_update
    partial = df.iloc[request["startRow"] : request["endRow"]]
    print(partial)
    return {"rowData": partial.to_dict("records"), "rowCount": len(df.index)}


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5801)
