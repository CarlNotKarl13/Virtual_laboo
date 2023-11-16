import plotly.graph_objects as go
import ipywidgets as widgets
from IPython.display import display

# Créez un diagramme ternaire vide
fig = go.Figure()

# Créez un point initial
initial_point = {'A': 0.2, 'B': 0.2, 'C': 0.6}
trace = go.Scatterternary(
    a=[initial_point['A']],
    b=[initial_point['B']],
    c=[initial_point['C']],
    mode='markers',
    marker=dict(size=10, color='blue'),
    hoverinfo=['a', 'b', 'c'],
    name='Point'
)

fig.add_trace(trace)


# Affichez le diagramme ternaire
fig.show()
