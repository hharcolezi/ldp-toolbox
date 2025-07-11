import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import numpy as np
import plotly.graph_objects as go

# Example protocol imports
from ldp_toolbox.protocols.frequency.grr import GeneralizedRandomizedResponse
from ldp_toolbox.protocols.frequency.ue import UnaryEncoding
from ldp_toolbox.protocols.frequency.lh import LocalHashing
from ldp_toolbox.protocols.frequency.he import HistogramEncoding
from ldp_toolbox.protocols.frequency.ss import SubsetSelection

from ldp_toolbox.toolbox.pages.style import p_style, p_titleStyle, p_textStyle, p_inputStyle, p_labelStyle, fontsize_text, fontsize_title, p_labelStyle_inline
# --------------------------
# 1) Color Scales & Markers
# --------------------------
color_scales = {
    'GRR': [[0, '#E63946'], [1, '#FFB3BA']],  # Vibrant Red -> Light Pink
    'BLH': [[0, '#FF7F50'], [1, '#FFD4C4']],  # Coral -> Peach
    'OLH': [[0, '#4CAF50'], [1, '#C8E6C9']],  # Lime Green -> Mint
    'SUE': [[0, '#1E88E5'], [1, '#BBDEFB']],  # Deep Blue -> Light Blue
    'OUE': [[0, '#9C27B0'], [1, '#E1BEE7']],  # Purple -> Lavender
    'SS':  [[0, '#FF4081'], [1, '#FFC1D5']],  # Hot Pink -> Baby Pink
    'SHE': [[0, '#00BCD4'], [1, '#B2EBF2']],  # Cyan -> Light Cyan
    'THE': [[0, '#FFC107'], [1, '#FFECB3']],  # Gold -> Pale Yellow
}

symbol_map = {
    'GRR': 'circle',
    'BLH': 'triangle-up',
    'OLH': 'square',
    'SUE': 'diamond',
    'OUE': 'cross',
    'SS':  'star',
    'SHE': 'x',
    'THE': 'pentagon'
}

# --------------------------
# 2) Helper function
# --------------------------
def conditional_format(values):
    """
    If min(values) < 0.01 => use scientific notation on that axis.
    """
    if values and min(values) < 0.01:
        return dict(tickformat=".2e", exponentformat="e", showexponent="all")
    else:
        return {}

# --------------------------
# Protocol Map
# --------------------------
protocol_map = {
    'GRR': lambda k, e, n: GeneralizedRandomizedResponse(k, e),
    'BLH': lambda k, e, n: LocalHashing(k, e, optimal=False),
    'OLH': lambda k, e, n: LocalHashing(k, e, optimal=True),
    'SUE': lambda k, e, n: UnaryEncoding(k, e, optimal=False),
    'OUE': lambda k, e, n: UnaryEncoding(k, e, optimal=True),
    'SS':  lambda k, e, n: SubsetSelection(k, e),
    'SHE': lambda k, e, n: HistogramEncoding(k, e, thresholding=False),
    'THE': lambda k, e, n: HistogramEncoding(k, e, thresholding=True),
}

ALL_PROTOCOLS = list(protocol_map.keys())

# --------------------------
# LAYOUT
# --------------------------

controls_card = dbc.Card([
    dbc.CardHeader("LDP Protocol Configuration" , style=p_titleStyle),
    dbc.CardBody([
        dbc.Row([
            dbc.Col(html.Label("Select Protocol(s):", style=p_textStyle), width="auto"),
            dbc.Col(
                dbc.Button("Select All", id="select-all-button", n_clicks=0, color="secondary"),
                width="auto",
                className="ms-auto"
            ),
        ], className="g-0 align-items-center mb-2"),

        # Protocol Checklist
        dcc.Checklist(
            id='protocols-checklist',
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
            value=['GRR', 'OLH', 'OUE', 'SS', 'THE'],  # default
            labelStyle=p_labelStyle,
            style = p_style,
            inputStyle={
                    "width": str(fontsize_text)+"px",      # checkbox box width
                    "height": str(fontsize_text)+"px",     # checkbox box height
                    "margin-right": "10px"
                }
        ),

        html.Br(),
        html.Div([
                    html.Label("Domain Size (k):", style={'marginRight': '10px', 'whiteSpace': 'nowrap'}),
                    dcc.Input(id='domain-size', type='number', value=10, min=2, step=1),
                ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '10px', 'fontSize':str(fontsize_text)+'px'}),
        html.Br(),
        html.Div([
                    html.Label("Number of Users (n):", style={'marginRight': '10px', 'whiteSpace': 'nowrap'}),
                    dcc.Input(id='num-users', type='number', value=10000, min=1, step=1),
                ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '10px', 'fontSize':str(fontsize_text)+'px'}),
        html.Br(),
        html.Label("ε Range:", style=p_textStyle),
        dcc.RangeSlider(
            id='epsilon-range',
            min=0.1, max=20., step=0.1, value=[0.5, 10],
            marks={i: {'label' : str(i), 'style': {'font-size': str(fontsize_text)+'px'}} for i in range(0, 21, 2)},
            tooltip={"placement": "bottom", "always_visible": True}
        ),
        html.Br(),

        # Step input for epsilon
        html.Label("ε Step:", style={'marginRight': '10px', 'whiteSpace': 'nowrap', 'font-size': str(fontsize_text)+'px'}),
        dcc.Input(id='epsilon-step', type='number', value=0.5, step=0.1, min=0.1, style=p_textStyle),

        html.Br(), html.Br(),
        dbc.Button("Compute", id="compute-button", n_clicks=0, color="primary", style=p_textStyle),

        dcc.Loading(
            type='default',
            children=[html.Div(id="compute-status", className="mt-2 text-success")]
        ),
    ])
])

# Toggles for y-axis scale in ASR vs. ε, MSE vs. ε
scale_options = [
    {'label': 'Linear ', 'value': 'linear'},
    {'label': 'Log ', 'value': 'log'}
]

scale_card = dbc.Card([
    dbc.CardHeader("Plot Axis Scale", style=p_titleStyle),
    dbc.CardBody([
        html.Label("ASR vs. ε Y-scale:", style=p_textStyle),
        dcc.RadioItems(id='asr-scale', options=scale_options, value='linear', inline=True,
                       labelStyle=p_labelStyle_inline),
        html.Br(),
        
        html.Label("MSE vs. ε Y-scale:", style=p_textStyle),
        dcc.RadioItems(id='mse-scale', options=scale_options, value='log', inline=True,
                       labelStyle=p_labelStyle_inline),
        html.Hr(),

        html.Label("MSE vs. ASR X-scale:", style=p_textStyle),
        dcc.RadioItems(id='mse-asr-x-scale', options=scale_options, value='linear', inline=True,
                       labelStyle=p_labelStyle_inline),
        html.Br(),

        html.Label("MSE vs. ASR Y-scale:", style=p_textStyle),
        dcc.RadioItems(id='mse-asr-y-scale', options=scale_options, value='log', inline=True,
                       labelStyle=p_labelStyle_inline),
    ])
])


plots_card = dbc.Card([
    dbc.CardHeader("Trade-Off Visualizations", style=p_titleStyle),
    dbc.CardBody([
        dcc.Loading(
            type="default",
            children=[
                dcc.Graph(id='asr-epsilon-plot'),
                dcc.Graph(id='mse-epsilon-plot'),
                dcc.Graph(id='mse-asr-plot')
            ]
        )
    ])
])

# Hidden store to cache results
cache_store = dcc.Store(id='ldp-data-store')

layout = dbc.Container([
    # Two columns of controls: Main config (left) + Axis scale toggles (middle), then the plots (right)
    dbc.Row([
        dbc.Col([controls_card, html.Br(), scale_card], width=4),
        dbc.Col(plots_card, width=8)
    ]),
    cache_store
], fluid=True)


# =========================================================== #
def register_callbacks(app):
    # --------------------------
    # 1) "Select All" Callback
    # --------------------------
    @app.callback(
        Output('protocols-checklist', 'value'),
        Input('select-all-button', 'n_clicks'),
        State('protocols-checklist', 'value')
    )
    def toggle_select_all(n_clicks, current_values):
        if n_clicks == 0:
            raise dash.exceptions.PreventUpdate
        if set(current_values) == set(ALL_PROTOCOLS):
            return []
        else:
            return ALL_PROTOCOLS


    # --------------------------
    # 2) Compute Callback
    # --------------------------
    @app.callback(
        Output('ldp-data-store', 'data'),
        Output('compute-status', 'children'),  # spinner is attached here
        Input('compute-button', 'n_clicks'),
        State('protocols-checklist', 'value'),
        State('domain-size', 'value'),
        State('num-users', 'value'),
        State('epsilon-range', 'value'),
        State('epsilon-step', 'value')
    )
    def compute_ldp_results(n_clicks, protocols, k, n, epsilon_range, epsilon_step):
        if n_clicks == 0:
            raise dash.exceptions.PreventUpdate

        if not protocols:
            return {}, "No protocols selected."

        k = int(k)
        n = int(n)
        eps_min, eps_max = epsilon_range

        # Generate eps values with user-specified step
        epsilons = np.arange(eps_min, eps_max + (epsilon_step * 0.01), epsilon_step)

        results = {}
        for prot in protocols:
            if prot not in protocol_map:
                continue

            mse_vals = []
            asr_vals = []
            for eps in epsilons:
                p = protocol_map[prot](k, eps, n)
                mse_vals.append(p.get_mse(n=n))
                asr_vals.append(p.get_asr()*100) # Convert to percentage

            results[prot] = {
                "epsilons": epsilons.tolist(),
                "mse": mse_vals,
                "asr": asr_vals
            }

        return results, "Computation done!"


    # --------------------------
    # 3) Plotting Callback
    # --------------------------
    @app.callback(
        [
            Output('asr-epsilon-plot', 'figure'),
            Output('mse-epsilon-plot', 'figure'),
            Output('mse-asr-plot', 'figure')
        ],
        [
            Input('ldp-data-store', 'data'),
            Input('asr-scale', 'value'),
            Input('mse-scale', 'value'),
            Input('mse-asr-x-scale', 'value'),
            Input('mse-asr-y-scale', 'value')
        ]
    )
    def update_plots(ldp_data, asr_scale, mse_scale, mse_asr_x_scale, mse_asr_y_scale):
        """
        1) ASR vs. ε  --> single-color markers, user can set Y-scale (linear/log)
        2) MSE vs. ε  --> single-color markers, user can set Y-scale (linear/log)
        3) MSE vs. ASR --> gradient color by eps, user can set X-scale (linear/log) AND Y-scale (linear/log)
        """
        if not ldp_data:
            return go.Figure(), go.Figure(), go.Figure()

        all_mse = []
        all_asr = []

        # Create empty figs
        asr_epsilon_fig = go.Figure()
        mse_epsilon_fig = go.Figure()
        mse_asr_fig = go.Figure()

        for prot, prot_data in ldp_data.items():
            epsilons = np.array(prot_data["epsilons"])
            mse_values = prot_data["mse"]
            asr_values = prot_data["asr"]

            all_mse.extend(mse_values)
            all_asr.extend(asr_values)

            my_colorscale = color_scales.get(prot, [[0, 'black'], [1, 'lightgray']])
            my_symbol = symbol_map.get(prot, 'circle')
            dark_color = my_colorscale[0][1]  # the "dark" color

            # 1) ASR vs. ε - single-color markers
            asr_epsilon_fig.add_trace(go.Scatter(
                x=epsilons,
                y=asr_values,
                mode='lines+markers',
                name=prot,
                marker=dict(
                    size=6,
                    color=dark_color,  # single color, no gradient
                    symbol=my_symbol,
                    showscale=False
                ),
                line=dict(width=2, color=dark_color)
            ))

            # 2) MSE vs. ε - single-color markers
            mse_epsilon_fig.add_trace(go.Scatter(
                x=epsilons,
                y=mse_values,
                mode='lines+markers',
                name=prot,
                marker=dict(
                    size=6,
                    color=dark_color,  # single color, no gradient
                    symbol=my_symbol,
                    showscale=False
                ),
                line=dict(width=2, color=dark_color)
            ))

            # 3) MSE vs. ASR - keep gradient color
            # (Dark color = smaller ε, light color = larger ε)
            mse_asr_fig.add_trace(go.Scatter(
                x=asr_values,
                y=mse_values,
                mode='lines+markers',
                name=prot,
                marker=dict(
                    size=6,
                    color=epsilons,        # gradient from small -> large
                    colorscale=my_colorscale,
                    symbol=my_symbol,
                    showscale=False
                ),
                line=dict(width=2, color=dark_color)
            ))

        # Axis formatting
        asr_format = conditional_format(all_asr)
        mse_format = conditional_format(all_mse)

        # 1) ASR vs. ε
        asr_epsilon_fig.update_layout(
            title="Attackability vs. ε",
            xaxis=dict(title='Privacy Budget (ε)', tickmode='linear'),
            yaxis=dict(title='Reconstruction Rate (%)',
                    type=asr_scale,  # user toggle
                    **asr_format),
            legend={'font': {'size': fontsize_text}},
            font={'size': fontsize_text}
        )

        # 2) MSE vs. ε
        mse_epsilon_fig.update_layout(
            title="Utility loss vs. ε",
            xaxis=dict(title='Privacy Budget (ε)', tickmode='linear'),
            yaxis=dict(title='Mean Squared Error (MSE)',
                    type=mse_scale,  # user toggle
                    **mse_format),
            legend={'font': {'size': fontsize_text}},
            font={'size': fontsize_text}
        )

        # 3) MSE vs. ASR (now with separate toggles for x and y)
        mse_asr_fig.update_layout(
            title="Utility vs. Attackability",
            xaxis=dict(
                title='Reconstruction Rate (%)',
                type=mse_asr_x_scale,  # new user toggle for X scale
                **asr_format
            ),
            yaxis=dict(
                title='Mean Square Error (MSE)',
                type=mse_asr_y_scale,  # user toggle for Y scale
                **mse_format
            ),
            legend={'font': {'size': fontsize_text}},
            font={'size': fontsize_text}
        )

        # Annotation about color meaning
        mse_asr_fig.add_annotation(
            x=0.,
            y=1.08,
            xref="paper",
            yref="paper",
            text="",
            showarrow=False,
            font=dict(size=20)
        )

        return asr_epsilon_fig, mse_epsilon_fig, mse_asr_fig
