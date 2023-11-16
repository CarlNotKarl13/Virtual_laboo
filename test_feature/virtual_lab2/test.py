import plotly.graph_objects as go

# Définir les paramètres du diagramme
x_min, x_max = 0, 1
y_min, y_max = 0, 1

# Créer un curseur
cursor = go.Slider(
    x=0.5,
    y=0.5,
    min=x_min,
    max=x_max,
    step=0.01,
    orientation="horizontal",
)

# Afficher le diagramme
fig = go.Figure(
    data=[
        go.Contour(
            x=np.arange(x_min, x_max, 0.01),
            y=np.arange(y_min, y_max, 0.01),
            z=np.full(X.shape, 1),
            colorscale="gray",
        ),
        go.Scatter(
            x=[0, cursor.x],
            y=[0, cursor.y],
            mode="markers",
            marker=dict(color="red", size=10),
        ),
    ]
)

fig.update_layout(
    xaxis=dict(range=[x_min, x_max]),
    yaxis=dict(range=[y_min, y_max]),
    updatemenus=[
        dict(
            type="buttons",
            buttons=[
                dict(label="Reset", args=[{"x": x_min, "y": y_min}], method="relayout")
            ],
        )
    ],
)

fig.show()