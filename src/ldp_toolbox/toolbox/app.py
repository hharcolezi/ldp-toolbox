import dash
from dash import dcc, html
from ldp_toolbox.toolbox.pages import visualization, custom_upload
import flask
import os

# Flask server
server = flask.Flask(__name__)
app = dash.Dash(
    __name__,
    server=server,
    suppress_callback_exceptions=True,
    external_stylesheets=["https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css"],
    title="LDP Toolbox",
    update_title=None,  # Hide default loading message
)

# Set favicon (optional: replace with actual favicon path)
app._favicon = ""

# Custom splash screen (invisible after loading)
splash_style = {
    "position": "fixed",
    "width": "100vw",
    "height": "100vh",
    "backgroundColor": "#0d6efd",
    "zIndex": 9999,
    "display": "flex",
    "justifyContent": "center",
    "alignItems": "center",
    "color": "white",
    "fontSize": "2em"
}

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            .navbar-custom {
                background-color: #e7f1fb;
                color: black;
                padding: 1rem;
                font-weight: bold;
                font-size: 36px;
            }
            .footer {
                background-color: #fdecea;
                color: black;
                padding: 1rem;
                margin-top: 2rem;
                text-align: center;
            }
            .footer img {
                height: 30px;
                margin: 0 10px;
                vertical-align: middle;
            }
        </style>
    </head>
    <body>
        <div id="splash" style="{splash_style}">
            🔒 Loading LDP Toolbox...
        </div>
        <script>
            window.addEventListener('load', function () {
                document.getElementById('splash').style.display = 'none';
            });
        </script>
        {%app_entry%}
        <footer class="footer">
            <div>
                Supported by <img src="/assets/inria_logo_rouge.jpg" alt="Inria"> 
                and <img src="/assets/logo-insa.jpg" alt="INSA CVL"> <br>
                © 2025 Haoying Zhang, Abhishek K. Mishra, Héber H. Arcolezi
            </div>
        </footer>
        {%config%}
        {%scripts%}
        {%renderer%}
    </body>
</html>
'''.replace("{splash_style}", "; ".join(f"{k}: {v}" for k, v in splash_style.items()))

# Main Layout
app.layout = html.Div([
    html.Div("🔐 LDP Toolbox", className="navbar-custom text-center"),
    dcc.Tabs(id="tabs", value='tab-1', children=[
        dcc.Tab(label='📊 Analytical Visualization', value='tab-1', children=visualization.layout, 
                style={
                    'fontSize': '22px',     # Bigger text
                    'padding': '12px 20px'  # Optional: more spacing
                },
                selected_style={
                    'fontSize': '22px',
                    'fontWeight': 'bold',
                    'padding': '12px 20px',
                    'borderBottom': '3px solid #0074D9',  # Optional styling
                    'backgroundColor': '#f0f0f0'
                }),
        dcc.Tab(label='📁 Custom Upload', value='tab-2', children=custom_upload.layout,
                style={
                    'fontSize': '22px',     # Bigger text
                    'padding': '12px 20px'  # Optional: more spacing
                },
                selected_style={
                    'fontSize': '22px',
                    'fontWeight': 'bold',
                    'padding': '12px 20px',
                    'borderBottom': '3px solid #0074D9',  # Optional styling
                    'backgroundColor': '#f0f0f0'
                }),
    ])
])

# Register callbacks
visualization.register_callbacks(app)
custom_upload.register_callbacks(app)

if __name__ == '__main__':
    app.run_server(debug=True)