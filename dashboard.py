import dash
from dash import dcc, html, Input, Output, State, dash_table
import pandas as pd
import plotly.express as px
import io
import base64

# Initialize the Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "IMDB Movies Dashboard"

# Initialize a global variable for the uploaded DataFrame
uploaded_df = None

# App Layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
])

# Landing Page Layout
landing_page = html.Div([
    html.Div([
        html.Img(
            src='assets\logo.jpeg',  # Add IMDb logo here if available
            style={'height': '100px', 'margin': 'auto', 'display': 'block'}
        )
    ]),
    html.H1("IMDB Movies Dashboard", style={'textAlign': 'center', 'color': '#4CAF50'}),
    html.P(
        "This dashboard helps analyze IMDb’s Top 1000 movies with insights from univariate and bivariate analyses.",
        style={'textAlign': 'center', 'fontSize': '16px', 'margin': '20px'}
    ),
    dcc.Upload(
        id='upload-data',
        children=html.Div(['Drag and Drop or ', html.A('Select Files')]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px',
            'backgroundColor': '#f0f8ff'
        },
        multiple=False
    ),
    html.Div(id='upload-status', style={'textAlign': 'center', 'margin': '20px'}),
    html.Div(id='data-table-container'),
    html.Div([
        dcc.Link('Univariate Analysis', href='/univariate', style={'marginRight': '20px'}),
        dcc.Link('Bivariate Analysis', href='/bivariate'),
    ], style={'textAlign': 'center', 'marginTop': '20px'})
])

# File Upload Callback
@app.callback(
    Output('data-table-container', 'children'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def update_table(contents, filename):
    global uploaded_df
    if contents:
        # Decode the uploaded content
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))

        # Update the global dataframe
        uploaded_df = df

        # Display the first 10 rows of the uploaded data
        return dash_table.DataTable(
            columns=[{"name": col, "id": col} for col in df.columns],
            data=df.head(10).to_dict('records'),
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left'},
            page_size=10
        )
    return html.Div("Please upload a CSV file to display the data.", style={'color': 'red'})

# Univariate Analysis Layout
univariate_page = html.Div([
    html.H1("Univariate Analysis", style={'textAlign': 'center', 'color': '#4CAF50'}),
    dcc.Dropdown(
        id='univariate-dropdown',
        placeholder="Select a Column",
        style={'width': '50%', 'margin': 'auto', 'marginTop': '20px'}
    ),
    dcc.Graph(id='univariate-plot'),
    dcc.Link('Go to Landing Page', href='/'),
])

@app.callback(
    Output('univariate-dropdown', 'options'),
    Input('url', 'pathname')
)
def update_univariate_dropdown(pathname):
    if pathname == '/univariate' and uploaded_df is not None:
        # Populate the dropdown with numerical columns from the uploaded dataset
        options = [{'label': col, 'value': col} for col in uploaded_df.select_dtypes(include='number').columns]
        return options
    return []

@app.callback(
    Output('univariate-plot', 'figure'),
    Input('univariate-dropdown', 'value')
)
def update_univariate_plot(column):
    if column and uploaded_df is not None:
        # Generate a histogram for the selected column
        fig = px.histogram(uploaded_df, x=column, title=f"Distribution of {column}")
        return fig
    return {}

# Bivariate Analysis Layout
bivariate_page = html.Div([
    html.H1("Bivariate Analysis", style={'textAlign': 'center', 'color': '#4CAF50'}),
    html.Div([
        html.Div([
            dcc.Dropdown(
                id='bivariate-x',
                placeholder="Select X-Axis Column",
                style={
                    'width': '90%',
                    'margin': '0 auto',
                    'padding': '5px'
                }
            )
        ], style={'width': '45%', 'display': 'inline-block', 'textAlign': 'center'}),
        html.Div([
            dcc.Dropdown(
                id='bivariate-y',
                placeholder="Select Y-Axis Column",
                style={
                    'width': '90%',
                    'margin': '0 auto',
                    'padding': '5px'
                }
            )
        ], style={'width': '45%', 'display': 'inline-block', 'textAlign': 'center'}),
    ], style={'width': '100%', 'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center'}),
    dcc.Graph(id='bivariate-plot', style={'marginTop': '20px'}),
    dcc.Link('Go to Landing Page', href='/', style={'display': 'block', 'textAlign': 'center', 'marginTop': '20px'})
])


@app.callback(
    [Output('bivariate-x', 'options'),
     Output('bivariate-y', 'options')],
    Input('url', 'pathname')
)
def update_bivariate_dropdowns(pathname):
    if pathname == '/bivariate' and uploaded_df is not None:
        # Populate both dropdowns with numerical columns from the uploaded dataset
        options = [{'label': col, 'value': col} for col in uploaded_df.select_dtypes(include='number').columns]
        return options, options
    return [], []

@app.callback(
    Output('bivariate-plot', 'figure'),
    [Input('bivariate-x', 'value'), Input('bivariate-y', 'value')]
)
def update_bivariate_plot(x_col, y_col):
    if x_col and y_col and uploaded_df is not None:
        # Generate a scatter plot for the selected columns
        fig = px.scatter(uploaded_df, x=x_col, y=y_col, title=f"{x_col} vs {y_col}")
        return fig
    return {}

# Routing logic
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == '/univariate':
        return univariate_page
    elif pathname == '/bivariate':
        return bivariate_page
    else:
        return landing_page

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
