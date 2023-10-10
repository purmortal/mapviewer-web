import webbrowser
import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
from Open_Save_File import open_file_dialog

import tkinter
from tkinter import filedialog as fd

FILE_DIR = '/home/zwan0382'

webbrowser.get('windows-default').open('http://localhost:8050', new=2)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.H4('Update my list',
            style={
                'textAlign': 'center'
            }),
    html.Br(),
    html.Hr(),

    html.Div([
        html.H5('Excel Directory:',
                style = {'width': '20%', 'display': 'inline-block', \
                    'text-align': 'left'}),
        html.Div(id='selected_directory', children='No file selected!', \
            style={'width': '30%', 'display': 'inline-block'}),
        html.Button('Browse', id='open_excel_button', \
            n_clicks=0, style={'float': 'right', 'display': 'inline-block'})
    ]),
])

# 1. Callback for open_excel button
@app.callback(
    Output(component_id='selected_directory', component_property='children'),
    Input(component_id='open_excel_button', component_property='n_clicks'),
    prevent_initial_call=True
)
def open_excel_function(open_excel):
    print ('*** 1A. Callback open_file_dialog')
    ctx = dash.callback_context
    trigger = ctx.triggered[0]['prop_id'].split('.')[0]
    print("***", trigger, "is triggered.")
    root = tkinter.Tk()
    root.withdraw()
    # root.iconbitmap(default='Extras/transparent.ico')
    if trigger == 'open_excel_button':
        file_directory = tkinter.filedialog.askopenfilename(initialdir=FILE_DIR) <-- Source of all evil....
        print('***', file_directory)
    else:
        file_directory = None
    return file_directory

if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)
