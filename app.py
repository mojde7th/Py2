import dash
from dash import dcc, html, Input, Output
import dash_cytoscape as cyto
from fetch_data import fetch_data
import plotly.express as px
import pandas as pd

# Fetch data
df = fetch_data()

# Debug: Check if data is correctly fetched
if "EMPLOYM_TYPE" not in df.columns:
    raise ValueError("EMPLOYM_TYPE column is missing. Ensure the SQL query is correct.")

# Prepare data for hierarchical tree
def generate_tree_elements(data):
    elements = []
    for _, row in data.iterrows():
        # Add node
        elements.append({"data": {"id": row["NodeId"], "label": row["Title"]}})
        # Add edge (parent-child relationship)
        if row["ParentId"] and row["ParentId"] != "Root":
            elements.append({"data": {"source": row["ParentId"], "target": row["NodeId"]}})
    return elements

tree_elements = generate_tree_elements(df)

# Initialize Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "Hierarchy Tree"
server = app.server

# Layout
app.layout = html.Div([
    html.H1("Hierarchy Tree", style={"textAlign": "center"}),

    # Hierarchical tree visualization
    cyto.Cytoscape(
        id="hierarchy-tree",
        layout={"name": "breadthfirst"},  # Hierarchical layout
        style={"width": "100%", "height": "600px"},
        elements=tree_elements,
        stylesheet=[
            {
                "selector": "node",
                "style": {
                    "content": "data(label)",
                    "text-valign": "center",
                    "color": "black",
                    "background-color": "lightblue",
                },
            },
            {
                "selector": "edge",
                "style": {
                    "width": 2,
                    "line-color": "#ccc",
                    "target-arrow-color": "#ccc",
                    "target-arrow-shape": "triangle",
                },
            },
        ],
    ),

    # Display node details
    html.Div(id="node-details-container", style={"marginTop": "20px"}),

    # Display gender and employment type distributions
    html.Div([
        html.Div(id="gender-chart-container", style={"display": "inline-block", "width": "48%"}),
        html.Div(id="employment-chart-container", style={"display": "inline-block", "width": "48%"}),
    ], style={"marginTop": "20px"}),
])

@app.callback(
    [Output("node-details-container", "children"),
     Output("gender-chart-container", "children"),
     Output("employment-chart-container", "children")],
    [Input("hierarchy-tree", "tapNodeData")]
)
def display_node_details(node_data):
    if not node_data:
        return html.H3("Select a node to see details"), None, None

    node_id = node_data["id"]
    filtered_data = df[df["NodeId"] == node_id]

    # Gender Distribution
    if filtered_data.empty:
        gender_chart = html.H3("No Gender Data Available")
    else:
        gender_count = pd.DataFrame({
            "Gender": ["Male", "Female"],
            "Count": [filtered_data.iloc[0]["MaleCount"], filtered_data.iloc[0]["FemaleCount"]],
        })

        gender_fig = px.pie(
            gender_count,
            names="Gender",
            values="Count",
            title="Gender Distribution",
            hole=0.4,
        )
        gender_chart = dcc.Graph(figure=gender_fig)

    # Employment Type Distribution
    if filtered_data.empty or filtered_data["EMPLOYM_TYPE"].isnull().all():
        employment_chart = html.H3("No Employment Type Data Available")
    else:
        employment_count = (
            filtered_data.groupby("EMPLOYM_TYPE")
            .size()
            .reset_index(name="Count")
        )
        employment_fig = px.pie(
            employment_count,
            names="EMPLOYM_TYPE",
            values="Count",
            title="Employment Type Distribution",
            hole=0.4,
        )
        employment_chart = dcc.Graph(figure=employment_fig)

    # Node Details
    node_details = html.Div([
        html.H3(f"Node Details for {node_data['label']}"),
        html.Pre(
            "\n".join(
                [f"{key}: {value}" for key, value in filtered_data.iloc[0].items()]
            ),
            style={"whiteSpace": "pre-wrap"},
        ),
    ])

    return node_details, gender_chart, employment_chart

if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8080)
