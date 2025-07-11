import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import base64
import io, json, os, re
from tqdm import tqdm
from ldp_toolbox.toolbox.pages.utils import *
from ldp_toolbox.toolbox.pages.visualization import (
    color_scales, symbol_map, conditional_format, protocol_map, ALL_PROTOCOLS
)
from ldp_toolbox.toolbox.pages.style import p_style, p_titleStyle, p_textStyle, p_inputStyle, p_labelStyle, fontsize_text, fontsize_title
# Example protocol imports
from ldp_toolbox.protocols.frequency.grr import GeneralizedRandomizedResponse
from ldp_toolbox.protocols.frequency.ue import UnaryEncoding
from ldp_toolbox.protocols.frequency.lh import LocalHashing
from ldp_toolbox.protocols.frequency.he import HistogramEncoding
from ldp_toolbox.protocols.frequency.ss import SubsetSelection

# -------------------------- #
# Global map for metric functions
utility_func = {
    "MSE" : mse,
    "RMSE" : rmse,
    "KL-divergence" : kl_divergence,
    "Kendall-rank-correlation-coefficient" : kendall_rank_correlation
}

# Upload + Controls
upload_card = dbc.Card([
    dbc.CardHeader("Upload Custom Dataset", style={'fontSize': str(fontsize_title)+'px'}),
    dbc.CardBody([
        dcc.Upload(
            id='upload-data',
            children=html.Div(['Drag and Drop or ', html.A('Select CSV File')]),
            style={
                'width': '100%', 'height': '60px', 'lineHeight': '60px',
                'borderWidth': '1px', 'borderStyle': 'dashed',
                'borderRadius': '5px', 'textAlign': 'center', 'margin': '10px',
                'fontSize': str(fontsize_text)+'px'
            },
            multiple=False
        ),
        html.Div(id='upload-stats', className='text-info'),
        html.Br(),
        html.Label("Select attribute:", style={'fontSize': str(fontsize_text)+'px'}),
        html.Div([
            dcc.Dropdown(
                id='attribute-checkboxes',
                options=[],
                value=None,  # Optional: pre-select none
                style=p_style 
            )
        ]),
        #html.Br(),
        html.Div([
            dcc.Checklist(
                options=[{'label': 'Define value range', 'value': 'show'}],
                value=[],
                labelStyle=p_labelStyle,
                id='toggle-checkbox',
                inputStyle={
                    "width": str(fontsize_text)+"px",      # checkbox box width
                    "height": str(fontsize_text)+"px",     # checkbox box height
                    "margin-right": "10px"
                },
                style=p_style
            ),
            html.Div(id="input-container", children = [
                html.Div([
                    html.Label("Min value:", style={'marginRight': '10px', 'whiteSpace': 'nowrap'}),
                    dcc.Input(id='min-input', type='number', value=0, min=0, step=1),
                ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '10px', 'fontSize':'25px'}),

                html.Div([
                    html.Label("Max value:", style={'marginRight': '10px', 'whiteSpace': 'nowrap'}),
                    dcc.Input(id='max-input', type='number', value=1000, min=1, step=1),
                ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '10px', 'fontSize':'25px'}),
            ])
        ]),
        html.Br(),
        html.Label("Is this a location dataset? (Heatmap visualization)", style={'fontSize': str(fontsize_text)+'px'}),
        dcc.Checklist(
            id='location-toggle',
            options=[{'label': 'Yes', 'value': 'yes'}],
            value=[],
            inputStyle={
                "width": str(fontsize_text)+"px",      # checkbox box width
                "height": str(fontsize_text)+"px",     # checkbox box height
                "margin-right": "10px"
            },
            style=p_style,
            labelStyle=p_labelStyle
        ),
        html.Label("Percentage of users to sample:", style={'fontSize': str(fontsize_text)+'px'}),
        dcc.Slider(
            id='user-sample-slider',
            min=1,
            max=100,
            step=1,
            value=100,
            marks={1: {'label': '1%', 'style': {'font-size': str(fontsize_text)+'px'}}, 100: {'label': '100%', 'style': {'font-size': str(fontsize_text)+'px'}}, },
            tooltip={"placement": "bottom", "always_visible": True}
        ),
        html.Br(),

        dbc.Row([
            dbc.Col(html.Label("Select Protocol(s):"), width="auto", style={'fontSize': str(fontsize_text)+'px'}),
            dbc.Col(
                dbc.Button("Select All", id="select-all-button-usecase", n_clicks=0, color="secondary"),
                width="auto",
                className="ms-auto"
            ),
        ], className="g-0 align-items-center mb-2"),
        dcc.Checklist(
            id='protocols-checklist-usecase',
            options=[
                {'label': 'Generalized Randomized Response (GRR)', 'value': 'GRR'},
                {'label': 'Binary Local Hashing (BLH)', 'value': 'BLH'},
                {'label': 'Optimized Local Hashing (OLH)', 'value': 'OLH'},
                {'label': 'Symmetric Unary Encoding (SUE)', 'value': 'SUE'},
                {'label': 'Optimized Unary Encoding (OUE)', 'value': 'OUE'},
                {'label': 'Subset Selection (SS)', 'value': 'SS'},
                {'label': 'Summation with HE (SHE)', 'value': 'SHE'},
                {'label': 'Thresholding with HE (THE)', 'value': 'THE'},
            ],
            value=['GRR', 'OUE'],  # default
            labelStyle=p_labelStyle,
            style=p_style,
            inputStyle={
                "width": str(fontsize_text)+"px",      # checkbox box width
                "height": str(fontsize_text)+"px",     # checkbox box height
                "margin-right": "10px"
            }
        ),
        html.Br(),

        html.Label("ε Range:", style={'fontSize': str(fontsize_text)+'px'}),
        dcc.RangeSlider(
            id='epsilon-range-custom',
            min=0.1, max=20., step=0.1, value=[0.5, 10],
            marks={i: {'label' : str(i), 'style': {'font-size': str(fontsize_text)+'px'}} for i in range(0, 21, 2)},
            tooltip={"placement": "bottom", "always_visible": True}
        ),
        
        html.Br(), html.Br(),
        dbc.Button("Compute", id="compute-button-custom", color="primary", n_clicks=0, style={'fontSize': str(fontsize_text)+'px'}),
        html.Br(), 
        dcc.Store(id='progress-store', data={}),
        dcc.Interval(id='progress-interval', interval=1000, n_intervals=0, disabled=True),
        html.Div(id='progress-bars-container'),
        html.Br(), 
        html.Div(id='compute-res', className='text-info'),
    ])
])

utility_metric_options = [
    {"label": "MSE ⬇️", "value": "MSE"},
    {"label": "RMSE ⬇️", "value": "RMSE"},
    {"label": "KL-divergence ⬇️", "value": "KL-divergence"},
    {"label": "Kendall-rank-correlation-coefficient ⬆️", "value": "Kendall-rank-correlation-coefficient"}
]

viz_card = dbc.Card([
    dbc.CardHeader("Utility Loss", style={'fontSize': str(fontsize_title)+'px'}),
    dbc.CardBody([
        dcc.Loading(type="default", children=[
            html.Div([
            html.Span("Choose a Utility Metric:", style={'fontSize': str(fontsize_text)+'px'}),
            html.Br(),
            html.Span("⬇️ smaller is better | ⬆️ higher is better", 
                    style={'fontSize': str(fontsize_text - 2) + 'px', 'color': 'gray'})
        ]),
            dcc.Dropdown(
                id='utility-metric-selector',
                options=utility_metric_options,
                value="MSE",  # Default value
                clearable=False,
                style=p_style
            ),
            dcc.Store(id='metric', data=None),
            dcc.Graph(id='utility-benchmark-low'),
            dcc.Graph(id='utility-benchmark-mid'),
            dcc.Graph(id='utility-benchmark-high'),
        ])
    ])
])

attack_card = dbc.Card([
    dbc.CardHeader("Attackability", style={'fontSize': str(fontsize_title)+'px'}),
    dbc.CardBody([
        dcc.Loading(type="default", children=[
            dcc.Graph(id='attack-plot-low'),
            dcc.Graph(id='attack-plot-mid'),
            dcc.Graph(id='attack-plot-high')
        ])
    ])
])

distribution_card = dbc.Card([
    dbc.CardHeader("Distribution", style={'fontSize': str(fontsize_title)+'px'}),
    dbc.CardBody([
        dcc.Loading(type="default", children=[
            html.Label("Choose a protocol : ", style={'fontSize': str(fontsize_text)+'px'}),
            dcc.Dropdown(
                id='protocol-selector-distribution',
                options=ALL_PROTOCOLS,
                value=None,
                clearable=False,
                style=p_style
            ),
            html.Label("Choose an epsilon range between low, medium and high : ", style={'fontSize': str(fontsize_text)+'px'}),
            dcc.Dropdown(
                id='distribution-epsilon',
                options=["low", "medium", "high"],
                value=None,
                clearable=False,
                style=p_style
            ),
            dcc.Graph(id='distribution-plot'),
        ])
    ])
])

heatmap_card = html.Div(id='heatmap-container', style={'display': 'none'}, children=[
    dbc.Card([
        dbc.CardHeader("Heat Map", style={'fontSize': str(fontsize_title)+'px'}),
        dbc.CardBody([
            dcc.Loading(type="default", children=[
                dcc.Graph(id='heatmap-original'),
                dcc.Graph(id='heatmap-noisy')
            ])
        ])
    ])
])

store = dcc.Store(id='ldp-custom-store')

layout = dbc.Container([
    dbc.Row([
        dbc.Col([upload_card, html.Br()], width=4),
        dbc.Col([attack_card, viz_card, distribution_card, heatmap_card], width=8),

    ]),
    store
], fluid=True)

# -------------- Help function ---------------

def sanitize_numeric_array(arr):
    """Ensure numeric array has no invalid values for serialization"""
    arr = np.array(arr, dtype=float)
    arr = np.nan_to_num(arr, nan=0.0, posinf=0.0, neginf=0.0)
    return arr.astype(int)

def perturb_col(protocol_name, perturber, values, min_perturbed_attr):
    """
    Obfuscate the input data using the protocol protocol_name with the object perturber.

    Parameters
    ----------
    protocol_name : string
        The protocol name. In the possible protocol list.
    perturber : Protocol object
        The object corresponding to the protocol_name.
    values : np.ndarray
        The original values.
    min_perturbed_attr : int
        The shift off to min = 0.

    Returns
    -------
    list
        The estimated distribution in form (key, value).
    np.ndarray or list (for THE)
        The noisy values.
    np.ndarray
        The reconstructed values.
    """
    shifted_values = values - min_perturbed_attr
    n = len(values)

    obfuscate = perturber.obfuscate
    attack = perturber.attack
    print("--------obfuscate --------------")
    results = [obfuscate(input_data=v) for v in shifted_values]
    print("--------obfuscate  done--------------")

    if protocol_name in ["BLH", "OLH"]:
        # tupples in the list
        results_array = np.array(results)
        noisy_values = sanitize_numeric_array(results_array[:, 0] + min_perturbed_attr)
        print("--------estimate --------------")
        est_distribution = perturber.estimate(results_array)
        print("--------estimate done --------------")
        distribution = [(i + min_perturbed_attr, val) for i, val in enumerate(est_distribution)]

        print("--------attack --------------")
        reconstructed_values = sanitize_numeric_array([
            attack((v, s)) + min_perturbed_attr for v, s in results
        ])
        print("--------attack done --------------")

    elif protocol_name == "THE":
        # cannot convert to array
        est_distribution = perturber.estimate(results)
        distribution = [(i + min_perturbed_attr, val) for i, val in enumerate(est_distribution)]
        noisy_values = [v + min_perturbed_attr for v in results]
        reconstructed_values = sanitize_numeric_array([attack(v) + min_perturbed_attr for v in results])
    else:
        results_array = np.array(results)
        noisy_values = sanitize_numeric_array(results_array + min_perturbed_attr)
        est_distribution = perturber.estimate(results_array)
        distribution = [(i + min_perturbed_attr, val) for i, val in enumerate(est_distribution)]
        reconstructed_values = sanitize_numeric_array([
            attack(v) + min_perturbed_attr for v in results
        ])

    return distribution, noisy_values, reconstructed_values

def convert_location_attribute(text):
    pattern = r"\((\d+),\s*(\d+)\)"
    match = re.search(pattern, text)
    
    if match:
        content = match.groups()
        day_id = content[0]
        time_id = int(content[1])
        replaced_text = f"day {day_id} {int(time_id/2)}h" if time_id%2==0 else f"day {day_id} {int(time_id/2)}h30" 
    else:
        replaced_text = text
    
    return replaced_text

# ---------- callback functions ---------------------
def register_callbacks(app):
    @app.callback(
        Output('protocols-checklist-usecase', 'value'),
        Input('select-all-button-usecase', 'n_clicks'),
        State('protocols-checklist-usecase', 'value')
    )
    def toggle_select_all(n_clicks, current_values):
        if n_clicks == 0:
            raise dash.exceptions.PreventUpdate
        if set(current_values) == set(ALL_PROTOCOLS):
            return []
        else:
            return ALL_PROTOCOLS

    @app.callback(
        Output('input-container', 'style'),
        Output('min-input', 'value'),
        Output('max-input', 'value'),
        Input('toggle-checkbox', 'value')
    )
    def toggle_inputs(checked_values):
        if 'show' in checked_values:
            return {'display': 'block'}, None, None
        else:
            # Hide inputs and clear their values
            return {'display': 'none'}, None, None
    
    @app.callback(
        Output('heatmap-container', 'style'),
        Input('location-toggle', 'value')  # adjust based on your toggle component
    )
    def toggle_heatmap_visibility(toggle_value):
        if toggle_value and 'yes' in toggle_value:
            return {'display': 'block'}
        return {'display': 'none'}
    
    @app.callback(
        Output('progress-bars-container', 'children'),
        Output('progress-interval', 'disabled'),
        Input('progress-interval', 'n_intervals'),
        Input('compute-button-custom', 'n_clicks'),
        prevent_initial_call=True
    )
    def update_protocol_progress(n_intervals, n_clicks):
        ctx = dash.callback_context
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None

        # If compute button clicked: reset progress + enable interval
        if triggered_id == 'compute-button-custom':
            return [], False  # empty bars, enable progress bar updates

        # Otherwise: interval triggered → update progress bars
        try:
            with open("progress.json") as f:
                progress_dict = json.load(f)
        except Exception:
            progress_dict = {}

        bars = []
        for prot, prog in progress_dict.items():
            bars.append(html.Div([
                html.Div(f"{prot}:", style=p_style),
                dbc.Progress(value=int(prog), label=f"{int(prog)}%", striped=True, animated=True, style={'height': '20px'}),
                html.Br()
            ]))

        done = all(p >= 100 for p in progress_dict.values()) if progress_dict else False
        return bars, done  # disable when done

    @app.callback(
        Output('upload-stats', 'children'),
        Output('ldp-custom-store', 'data'),
        Output('attribute-checkboxes', 'options'),
        Output('compute-res', 'children'),
        Output('protocol-selector-distribution', 'options'),
        Output('protocol-selector-distribution', 'value'),
        Output('utility-metric-selector', 'value'),
        Output('distribution-epsilon', 'value'),
        Input('upload-data', 'contents'),
        Input('compute-button-custom', 'n_clicks'),
        Input('min-input', 'value'),
        Input('max-input', 'value'),
        Input('location-toggle', 'value'),
        State('user-sample-slider', 'value'),
        State('epsilon-range-custom', 'value'),
        State('attribute-checkboxes','value'),
        State('protocols-checklist-usecase', 'value'),
        prevent_initial_call=True
    )

    def handle_upload_and_compute(contents, n_clicks, min_input, max_input, location_toggle, sample_percentage, epsilon_range, attributes, protocols):
        if contents is None:
            raise dash.exceptions.PreventUpdate

        is_location_data = 'yes' in location_toggle
        print(f"Is location data: {is_location_data}")

        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        try:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        except Exception as e:
            return f"❌ Error reading file: {e}", {}, [], "", protocols, None

        df = df.dropna(how='all')
        sample_size = int(len(df)*sample_percentage/100)
        num_users = len(df)
        attribute_names = df.columns.tolist()
        #num_attributes_avg = np.mean(df.notnull().sum(axis=1))
        stats_text = f"📊 {num_users} users loaded | {len(attribute_names)} attributes"
        options=[{'label': convert_location_attribute(col), 'value': col} for col in attribute_names]
        
        # ------------ Click the button compute ------------------
        triggered = dash.callback_context.triggered_id
        if triggered != 'compute-button-custom':
            return stats_text, None, options, "", protocols, None, "MSE", "medium"
        else:
            # Empty the progress bar
            with open("progress.json", "w") as f:
                json.dump({prot: 0 for prot in protocols}, f)

            df_sampled = df.sample(n=sample_size, replace=False)
            df_sampled = df_sampled.astype(int)
            n = df_sampled.shape[0]

            # Define the value of k
            k_attribute = 0
            if min_input is None:
                k_min = np.min(df_sampled[attributes])
            else:
                k_min = int(min_input)
                if k_min > np.min(df_sampled[attributes]):
                    raise ValueError("Some values in the dataset is lower than the defined k min")
            if max_input is None:
                k_max = np.max(df_sampled[attributes])
            else:
                k_max = int(max_input)
                if k_max < np.max(df_sampled[attributes]):
                    raise ValueError("Some values in the dataset is bigger than the defined k max")
            print(f"Using min k : {k_min} | max k : {k_max}")

            k_attribute = int(k_max - k_min  + 1)
            if k_attribute < 2 :
                raise ValueError("k must be an integer value >= 2.")
            print(f"Attribute {attributes} | k = {k_attribute}")

            eps_min, eps_max = epsilon_range
            epsilons = [eps_min, (eps_min+eps_max)/2, eps_max]

            # original_distribution = df_sampled[attributes].melt()['value'].value_counts().sort_index()
            original_distribution = df_sampled[attributes].value_counts().sort_index()
            original_distribution = np.array([(val, count) for (val, count) in original_distribution.items()])
            

            results = {}
            
            # progress bar
            progress_dict = {prot: 0 for prot in protocols}
            total_eps = len(epsilons)
            step = 100 / total_eps

            for prot in protocols:
                mse_vals, asr_vals, priv_dists, reconst_dists, distribution, dra_vals = [], [], [], [], [], []
                for eps in tqdm(epsilons):

                    # For certain protocol with certain epsilon, compute the mse, asr, estimated distribution, noisy values, and attack values
                    p = protocol_map[prot](k_attribute, eps, n)
                    mse_list=p.get_mse(n=n)
                    asr_list=p.get_asr()
                    original_values = np.array(df_sampled[attributes])
                    # print("Started column perturbation")
                    noisy_distribution, noisy_values, reconstructed_values = perturb_col(prot, p, original_values, k_min)
                    total = sum(v[1] for v in noisy_distribution)  
                    assert  0.9 <= total <= 1.1, f"The distribution is not equal to 1"
                    # print("Column perturbation done!")
                    noisy_distribution_reverse = [(ind, np.round(value*n).astype(int)) for (ind,value) in noisy_distribution]
                    dra = sum(1 for i in range(n) if reconstructed_values[i] == original_values[i])
                    dra_vals.append(dra/n)
                    mse_vals.append(mse_list if mse_list else 0)
                    asr_vals.append(asr_list if asr_list else 0)
                    priv_dists.append(noisy_values)
                    reconst_dists.append(reconstructed_values)
                    distribution.append(noisy_distribution_reverse)

                    progress_dict[prot]+=step
                    with open("progress.json", "w") as f:
                        json.dump(progress_dict, f)

                results[prot] = {
                    "epsilons": epsilons,
                    "mse": mse_vals,
                    "asr": asr_vals,
                    "noisy_distributions": distribution,
                    "noisy_values": priv_dists,
                    "reconstructed_distributions": reconst_dists,
                    "dra": dra_vals
                }

            # Store noisy tables as DataFrames
            low_idx, mid_idx, high_idx = 0, 1, 2
            low_df, mid_df, high_df = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

            for prot in protocols:
                values = results[prot]['noisy_distributions']
                if len(values) > 0:
                    low_df[prot] = values[low_idx]
                    mid_df[prot] = values[mid_idx]
                    high_df[prot] = values[high_idx]

            return stats_text, {
                'original': original_distribution,            
                'k_min' : k_min,
                'k_max' : k_max,
                'results': results,
                'epsilons': epsilons,
                'noisy_datasets': {
                    'low': low_df.to_dict(),
                    'mid': mid_df.to_dict(),
                    'high': high_df.to_dict()
                },
                'is_location_data': is_location_data
            },options, f" ✅ Computed for {n} users", protocols, protocols[0], "MSE", "medium"
    
    @app.callback(
            Output('attack-plot-low', 'figure'),
            Output('attack-plot-mid', 'figure'),
            Output('attack-plot-high', 'figure'),
            Input('ldp-custom-store', 'data'),
            Input('compute-button-custom', 'n_clicks'),
            State('protocols-checklist-usecase', 'value')
        )
    def update_attackability_figure(ldp_data, n_clicks, all_protocols):
        empty_figs = [go.Figure(), go.Figure(), go.Figure()]
        if not ldp_data or not n_clicks:
            return empty_figs

        epsilons = ldp_data["epsilons"]
        indices = list(range(len(epsilons)))
        labels = ["Low ε", "Medium ε", "High ε"]

        figs = []
        for idx, label in zip(indices, labels):
            fig = go.Figure()
            for protocol in all_protocols:
                # Check protocol exists
                if protocol not in ldp_data["results"]:
                    continue
                dra_list = ldp_data["results"][protocol].get("dra", [])
                if len(dra_list) <= idx:
                    continue
                dra_score = dra_list[idx]
                fig.add_trace(go.Bar(x=[protocol], y=[dra_score * 100], name=protocol))
            fig.update_layout(
                title=f"Attackability for {label} = {epsilons[idx]:.2f}",
                yaxis=dict(range=[0, 100], dtick=20),
                xaxis_title="Protocol", yaxis_title="Reconstruction Rate (%)",
                font={'size': fontsize_text}
            )
            figs.append(fig)
        return figs

    @app.callback(
        Output('utility-benchmark-low', 'figure'),
        Output('utility-benchmark-mid', 'figure'),
        Output('utility-benchmark-high', 'figure'),
        Output('metric', 'data'),
        Input('utility-metric-selector', 'value'),
        Input('ldp-custom-store', 'data'),
        Input('compute-button-custom', 'n_clicks'),
        State('protocols-checklist-usecase', 'value')
    )
    def update_utility_figures(selected_metric, ldp_data, n_clicks, all_protocols):
        if selected_metric is None:
            selected_metric = "MSE"

        empty_figs = [go.Figure(), go.Figure(), go.Figure()]
        if not ldp_data or not n_clicks:
            return (*empty_figs, selected_metric)

        epsilons = ldp_data["epsilons"]
        indices = list(range(len(epsilons)))
        labels = ["Low ε", "Medium ε", "High ε"]

        original_distribution = np.array(ldp_data["original"])
        utility_figs = []
        for idx, label in zip(indices, labels):
            fig = go.Figure()
            for protocol in all_protocols:
                if protocol not in ldp_data["results"]:
                    continue
                noisy = np.array(ldp_data["results"][protocol]["noisy_distributions"][idx])
                score = utility_func[selected_metric](original_distribution, noisy)
                fig.add_trace(go.Bar(x=[protocol], y=[score], name=protocol))
            fig.update_layout(
                title=f"Utility Loss for {label} = {epsilons[idx]:.2f}",
                xaxis_title="Protocol",
                yaxis_title=selected_metric,
                font={'size': fontsize_text}
            )
            utility_figs.append(fig)

        return (*utility_figs, selected_metric)
    
    @app.callback(
        Output('distribution-plot', 'figure'),
        Output('heatmap-original', 'figure'),
        Output('heatmap-noisy', 'figure'),
        Input('protocol-selector-distribution', 'value'),
        Input('distribution-epsilon', 'value'),
        Input('compute-button-custom', 'n_clicks'),
        State('ldp-custom-store', 'data'),
        State('attribute-checkboxes', 'value'),
        State('metric', 'data')
    )
    def update_distribution_heatmap(selected_protocol, epsilon_range, n_clicks, ldp_data, attributes, selected_metric):
        distribution_fig = go.Figure()
        original_heatmap = go.Figure()
        noisy_heatmap = go.Figure()
        epsilon_range_map = {"low": 0, "medium": 1, "high": 2}
        labels = ["Low ε", "Medium ε", "High ε"]

        if (ldp_data and epsilon_range and selected_protocol and selected_metric) is not None and n_clicks:
            attributes = convert_location_attribute(attributes)
            print(attributes)
            # Build the original distribution
            k_min, k_max = ldp_data.get("k_min", 0), ldp_data.get("k_max", 0)
            original_distribution = [[i, 0] for i in range(k_min, k_max + 1)]
            for (ind, value) in ldp_data["original"]:
                original_distribution[ind - k_min][1] = value
            original_distribution = np.array(original_distribution)

            # Build the noisy estimated distribution
            epsilons = ldp_data["epsilons"]
            idx = epsilon_range_map[epsilon_range]
            noisy_vals = np.array(ldp_data['results'][selected_protocol]['noisy_distributions'][idx])

            distribution_fig.add_trace(go.Bar(
                x=list(original_distribution[:, 0].astype(str)),
                y=list(original_distribution[:, 1]),
                name="Real"
            ))
            distribution_fig.add_trace(go.Bar(
                x=list(noisy_vals[:, 0].astype(str)),
                y=list(noisy_vals[:, 1]),
                name="Estimated"
            ))
            distribution_fig.update_layout(
                title=(
                    f"Real vs Estimated Distribution for <b>{labels[idx]}</b> = {epsilons[idx]:.2f} with "
                    f"<b>{selected_metric}</b> = {utility_func[selected_metric](original_distribution, noisy_vals):.2f}"
                ),
                xaxis_title=str(attributes),
                yaxis_title="Count",
                font={'size': fontsize_text}
            )

            ### Heatmaps (only if location data) ###
            if ldp_data.get('is_location_data'):
                grid_size = 40
                k = grid_size * grid_size

                # Original heatmap
                matrix = np.zeros((grid_size, grid_size), dtype=int)
                for val, count in original_distribution:
                    val = int(val)
                    if 0 <= val < k:
                        matrix[val // grid_size, val % grid_size] += int(count)
                original_heatmap.add_trace(go.Heatmap(
                    z=matrix,
                    x=[str(i) for i in range(grid_size)],
                    y=[str(i) for i in range(grid_size)],
                    colorscale="YlGnBu"
                ))
                original_heatmap.update_layout(
                    title="Original Grid Heatmap",
                    xaxis_title="Y (col)",
                    yaxis_title="X (row)",
                    font={'size': fontsize_text}
                )

                # Estimated heatmaps
                matrix = np.zeros((grid_size, grid_size), dtype=int)
                for val, count in noisy_vals:
                    val = int(val)
                    if 0 <= val < k:
                        matrix[val // grid_size, val % grid_size] += int(count)
                noisy_heatmap.add_trace(go.Heatmap(
                    z=matrix,
                    x=[str(i) for i in range(grid_size)],
                    y=[str(i) for i in range(grid_size)],
                    colorscale="YlGnBu"
                ))
                noisy_heatmap.update_layout(
                    title=f"Estimated Heatmap for {labels[idx]} = {epsilons[idx]:.2f}",
                    xaxis_title="Y (col)",
                    yaxis_title="X (row)",
                    font={'size': fontsize_text}
                )
        return distribution_fig, original_heatmap, noisy_heatmap