import plotly.graph_objects as go
from plotly.subplots import make_subplots

from loadData import gistDataBase
from plotData import *
from helperFunctions import *

def find_nearest_idx(arrays, target_value):
    absolute_diff = np.abs(arrays - target_value)
    nearest_index = absolute_diff.argmin()
    return nearest_index


def make_html_subplots(database, module, maptype, persuffix, value):
    fig_plotMap = plotMap(database, module, maptype)
    # print(fig_plotMap.layout)
    figs_spec = plotSpectra(database)

    fig = make_subplots(
        rows=3,
        cols=2,
        specs=[
            [{'rowspan': 3, 'colspan': 1}, {'colspan': 1}],
            [None, {'colspan': 1}],
            [None, {'colspan': 1}],
        ],
    vertical_spacing=0.12,
    horizontal_spacing=0.12,
    subplot_titles=[" ", " ", " ", " "])

    trace1 = go.Scatter(
               x=np.linspace(0, 2, 60),
               y=np.random.rand(60),
               mode='lines',
               line=dict(width=1, color='red')
               )


    for trace_i in fig_plotMap.data:
        fig.add_trace(trace_i, row=1, col=1)
    fig['layout']['xaxis'].update(title=fig_plotMap.layout['xaxis']['title']['text'])
    fig['layout']['yaxis'].update(title=fig_plotMap.layout['yaxis']['title']['text'])
    fig['layout']['yaxis']['scaleanchor']='x'
    fig.layout.annotations[0].update(text='%s Map (%s, BIN_ID=%s, value=%.3f)' % (maptype, persuffix, str(database.idxBinShort), value))
    # print(fig_plotMap.layout)
    # for layout_i in fig_plotMap.layout:
    #     fig.update_layout(layout_i, row=1, col=1)

    fig_spec_row = 1
    for fig_spec in figs_spec:
        # print(fig_spec.layout)
        for trace_i in fig_spec.data:
            fig.add_trace(trace_i, row=fig_spec_row, col=2)
        fig['layout']['xaxis%s' % str(fig_spec_row+1)].update(fig_spec.layout['xaxis'])
        fig['layout']['yaxis%s' % str(fig_spec_row+1)].update(fig_spec.layout['yaxis'])
        fig.layout.annotations[fig_spec_row].update(text=fig_spec.layout['title']['text'])
        fig_spec_row += 1

    # print(fig_plotMap.layout['xaxis']['title']['text'])
    # print(fig.layout.annotations)
    # print(figs_spec[0].layout['title']['text'])
    # fig.layout.annotations[1].update(figs_spec[0].layout['title'])
    fig.update_layout(coloraxis = fig_plotMap.layout['coloraxis'].update({'colorbar_x': 0.45}))
    fig.update_layout(showlegend=False, margin=dict(l=50, r=50, t=50, b=50))
    # print(fig.layout)
    return fig

# Incorporate data
module_names = ["TABLE", "MASK", "KIN", "GAS", "SFH", "LS"]
module_table_names = ["table", "Mask", "kinResults", "gasResults", "sfhResults", "lsResults"]
plot_modules = ["KIN", "GAS", "SFH", "LS"]
database = gistDataBase()
path_gist_run = '/import/photon1/zwan0382/mwdatacube/geckos/ESO120-016_ALPHAS'
# path_gist_run = '/import/photon1/zwan0382/mwdatacube/geckos/ESO120-016'
# path_gist_run = '/import/photon1/zwan0382/mwdatacube/hpc_output/gist_results/NGC5746_linear_losvd_nonoise_muse_noyoungest_true_n1e8p/gist/resultsRevisedREr5mdeg4'
# path_gist_run = '/suphys/zwan0382/Documents/projects/mapviewer-web/NGC0000Example'
database.loadData(path_gist_run)

percentiles = [1, 99]
percentile_suffixs = ['PERCENT1', 'PERCENT99']

for module in plot_modules:
    if getattr(database, module) == True:
        module_table = getattr(database, module_table_names[module_names.index(module)])
        module_table_pd = getattr(database, module_table_names[module_names.index(module)] + '_Vorbin_df')
        maptype_list = module_table.names
        maptype_list = [x for x in maptype_list if "ERR" not in x]
        for maptype in maptype_list:
            # maptype = maptype_list[1]
            for i, percentile in enumerate(percentiles):
                print("Working on generating " + "galinspec_%s_%s_%s.html" % (module, maptype, percentile_suffixs[i]))
                if maptype == 'V':
                    nearest_index = find_nearest_idx(np.abs(module_table_pd[maptype]), np.nanpercentile(np.abs(module_table_pd[maptype]), percentile))
                else:
                    nearest_index = find_nearest_idx(module_table_pd[maptype], np.nanpercentile(module_table_pd[maptype], percentile))
                database.idxBinShort = module_table_pd['BIN_ID'][nearest_index]
                fig_result = make_html_subplots(database, module, maptype, percentile_suffixs[i], module_table_pd[maptype][nearest_index])
                fig_result.write_html("galinspec_%s_%s_%s.html" % (module, maptype, percentile_suffixs[i]))





