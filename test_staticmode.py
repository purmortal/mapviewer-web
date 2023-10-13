# import plotly.graph_objects as go
# import plotly.subplots as sp
#
# # Create some sample scatter plots
# scatter_plot1 = go.Figure(go.Scatter(x=[1, 2, 3, 4, 5], y=[10, 11, 12, 13, 14], mode='markers', name='Plot 1'))
# scatter_plot2 = go.Figure(go.Scatter(x=[1, 2, 3, 4, 5], y=[15, 14, 13, 12, 11], mode='markers', name='Plot 2'))
#
# # Create a subplot with the plots
# subplots = sp.make_subplots(rows=1, cols=2)
# subplots.add_trace(scatter_plot1.data[0], row=1, col=1)
# subplots.add_trace(scatter_plot2.data[0], row=1, col=2)
#
# # Set the layout of the subplots
# subplots.update_layout(
#     title="Multiple Plots in a Single HTML File",
#     xaxis_title="X-Axis",
#     yaxis_title="Y-Axis",
# )
#
# # Save the subplots to an HTML file
# subplots.write_html("multiple_plots.html")


import plotly.graph_objects as go

# Create some sample scatter plots
scatter_plot1 = go.Figure(go.Scatter(x=[1, 2, 3, 4, 5], y=[10, 11, 12, 13, 14], mode='markers', name='Plot 1'))
scatter_plot2 = go.Figure(go.Scatter(x=[1, 2, 3, 4, 5], y=[15, 14, 13, 12, 11], mode='markers', name='Plot 2'))

# Set the layout of each scatter plot
scatter_plot1.update_layout(
    title="Scatter Plot 1",
    xaxis_title="X-Axis",
    yaxis_title="Y-Axis",
)

scatter_plot2.update_layout(
    title="Scatter Plot 2",
    xaxis_title="X-Axis",
    yaxis_title="Y-Axis",
)

# Save each scatter plot to separate HTML files
scatter_plot1.write_html("scatter_plot1.html")
scatter_plot2.write_html("scatter_plot2.html")

