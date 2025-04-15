import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import plotly.express as px
from dash import no_update
import datetime as dt

# Create app with custom stylesheet
app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
server = app.server

# Clear the layout and do not display exception till callback gets executed
app.config.suppress_callback_exceptions = True

# Read the wildfire data into pandas dataframe
df = pd.read_csv(
    r'https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-DV0101EN-SkillsNetwork/Data%20Files/Historical_Wildfires.csv'
)

# Extract year and month from the date column
df['Month'] = pd.to_datetime(df['Date']).dt.month_name()  # used for the names of the months
df['Year'] = pd.to_datetime(df['Date']).dt.year

# Define colors for dark theme
colors = {
    'background': '#121212',
    'secondary_background': '#1e1e1e',
    'card_background': '#252525',
    'text': '#FFFFFF',
    'secondary_text': '#AAAAAA',
    'accent': '#ff7b00',
    'border': '#333333',
}

# Custom CSS for dark theme components
external_stylesheets = []

# Add custom CSS to fix dropdown styling
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            /* Dark dropdown styles */
            .Select-control, .Select-menu-outer, .Select-menu, .Select-option, .Select-value {
                background-color: #252525 !important;
                color: white !important;
                border-color: #333333 !important;
            }
            .Select-arrow {
                border-color: #ff7b00 transparent transparent !important;
            }
            .Select-arrow-zone:hover > .Select-arrow {
                border-top-color: #ff7b00 !important;
            }
            .Select-control:hover {
                box-shadow: 0 0 0 1px #ff7b00 !important;
                border-color: #ff7b00 !important;
            }
            .Select.is-focused > .Select-control {
                background-color: #1e1e1e !important;
                border-color: #ff7b00 !important;
                box-shadow: 0 0 0 1px #ff7b00 !important;
            }
            .Select.is-open > .Select-control {
                background-color: #1e1e1e !important;
                border-color: #ff7b00 !important;
            }
            .Select-option.is-focused {
                background-color: #333333 !important;
            }
            .Select-option.is-selected {
                background-color: #ff7b00 !important;
                color: white !important;
            }
            .Select-option:hover {
                background-color: #333333 !important;
            }
            .Select-value-label {
                color: white !important;
            }
            .Select-placeholder, .Select--single > .Select-control .Select-value {
                color: #AAAAAA !important;
            }
            
            /* Radio button enhancements */
            .radio-items input[type="radio"] {
                accent-color: #ff7b00;
            }
            .radio-item-container {
                display: inline-block;
                margin-right: 12px;
                margin-bottom: 8px;
                padding: 8px 15px;
                background-color: #252525;
                border-radius: 20px;
                cursor: pointer;
                transition: all 0.3s;
            }
            .radio-item-container:hover {
                background-color: #333333;
            }
            .radio-item-container.selected {
                background-color: #ff7b00;
                color: white;
            }

            /* Chart container styles */
            .chart-container {
                height: 100%;
                width: 100%;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Layout Section of Dash
app.layout = html.Div(
    style={
        'backgroundColor': colors['background'],
        'color': colors['text'],
        'fontFamily': 'Helvetica, Arial, sans-serif',
        'padding': '20px',
        'minHeight': '100vh',
    },
    children=[
        # Header
        html.Div(
            style={
                'textAlign': 'center',
                'padding': '20px 0',
                'marginBottom': '20px',
                'borderBottom': f'1px solid {colors["border"]}',
            },
            children=[
                html.H1(
                    'Australia Wildfire Dashboard',
                    style={
                        'textAlign': 'center',
                        'color': colors['accent'],
                        'fontSize': '32px',
                        'fontWeight': 'bold',
                        'marginBottom': '0',
                    }
                ),
                html.P(
                    'Visualizing historical wildfire data across Australia',
                    style={
                        'color': colors['secondary_text'],
                        'marginTop': '5px',
                    }
                ),
            ]
        ),
        
        # Controls section
        html.Div(
            style={
                'display': 'flex',
                'flexWrap': 'wrap',
                'justifyContent': 'space-between',
                'alignItems': 'center',
                'padding': '20px',
                'backgroundColor': colors['secondary_background'],
                'borderRadius': '10px',
                'marginBottom': '20px',
                'boxShadow': '0 4px 6px rgba(0,0,0,0.1)',
            },
            children=[
                # Region selection
                html.Div(
                    style={
                        'flex': '1',
                        'minWidth': '300px',
                        'marginRight': '20px',
                        'marginBottom': '10px',
                    },
                    children=[
                        html.H3(
                            'Select Region:',
                            style={
                                'marginBottom': '10px',
                                'fontSize': '18px',
                                'fontWeight': 'normal',
                                'color': colors['text'],
                            }
                        ),
                        dcc.RadioItems(
                            id='region',
                            options=[
                                {"label": "New South Wales", "value": "NSW"},
                                {"label": "Northern Territory", "value": "NT"},
                                {"label": "Queensland", "value": "QL"},
                                {"label": "South Australia", "value": "SA"},
                                {"label": "Tasmania", "value": "TA"},
                                {"label": "Victoria", "value": "VI"},
                                {"label": "Western Australia", "value": "WA"},
                            ],
                            value="NSW",
                            inline=True,
                            className='radio-items',
                            labelStyle={
                                'display': 'inline-block',
                                'marginRight': '12px',
                                'marginBottom': '8px',
                                'fontSize': '15px',
                                'padding': '8px 15px',
                                'backgroundColor': colors['card_background'],
                                'borderRadius': '20px',
                                'cursor': 'pointer',
                                'transition': 'all 0.3s',
                            },
                            inputStyle={
                                "marginRight": "5px"
                            },
                        ),
                    ]
                ),
                
                # Year selection
                html.Div(
                    style={
                        'flex': '1',
                        'minWidth': '220px',
                    },
                    children=[
                        html.H3(
                            'Select Year:',
                            style={
                                'marginBottom': '10px',
                                'fontSize': '18px',
                                'fontWeight': 'normal',
                                'color': colors['text'],
                            }
                        ),
                        dcc.Dropdown(
                            id='year',
                            options=[{'label': str(year), 'value': year} for year in sorted(df.Year.unique())],
                            value=2005,
                            clearable=False,
                            style={
                                'color': colors['text'],
                            },
                        ),
                    ]
                ),
            ]
        ),
        
        # Graphs section
        html.Div(
            style={
                'display': 'flex',
                'flexWrap': 'wrap',
                'justifyContent': 'space-between',
                'gap': '20px',
            },
            children=[
                html.Div(
                    id='plot1',
                    style={
                        'flex': '1',
                        'minWidth': '400px',
                        'height': '450px',  # Set a fixed height for consistent pie chart
                        'backgroundColor': colors['card_background'],
                        'borderRadius': '10px',
                        'padding': '15px',
                        'boxShadow': '0 4px 6px rgba(0,0,0,0.1)',
                    }
                ),
                html.Div(
                    id='plot2',
                    style={
                        'flex': '1',
                        'minWidth': '400px',
                        'height': '450px',  # Match height with plot1 for consistency
                        'backgroundColor': colors['card_background'],
                        'borderRadius': '10px',
                        'padding': '15px',
                        'boxShadow': '0 4px 6px rgba(0,0,0,0.1)',
                    }
                ),
            ]
        ),
        
        # Footer
        html.Div(
            style={
                'textAlign': 'center',
                'padding': '20px 0',
                'marginTop': '30px',
                'borderTop': f'1px solid {colors["border"]}',
                'color': colors['secondary_text'],
                'fontSize': '14px',
            },
            children=[
                html.P('Australia Wildfire Data Analysis Dashboard')
            ]
        ),
    ]
)

# Callback function
@app.callback(
    [Output(component_id='plot1', component_property='children'),
     Output(component_id='plot2', component_property='children')],
    [Input(component_id='region', component_property='value'),
     Input(component_id='year', component_property='value')]
)
def reg_year_display(input_region, input_year):
    # Data
    region_data = df[df['Region'] == input_region]
    y_r_data = region_data[region_data['Year'] == input_year]
    
    # Plot one - Monthly Average Estimated Fire Area
    est_data = y_r_data.groupby('Month')['Estimated_fire_area'].mean().reset_index()
    
    # Sort months in correct order for better visualization
    month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                  'July', 'August', 'September', 'October', 'November', 'December']
    est_data['Month'] = pd.Categorical(est_data['Month'], categories=month_order, ordered=True)
    est_data = est_data.sort_values('Month')
    
    fig1 = px.pie(
        est_data,
        values='Estimated_fire_area',
        names='Month',
        title="{} : Monthly Average Estimated Fire Area in year {}".format(input_region, input_year),
        color_discrete_sequence=px.colors.sequential.Inferno,
        template="plotly_dark",
        hole=0.4,  # Adding a hole to make it a donut chart for better readability
    )
    
    fig1.update_layout(
        paper_bgcolor=colors['card_background'],
        plot_bgcolor=colors['card_background'],
        font=dict(color=colors['text']),
        title_font=dict(color=colors['text'], size=16),
        margin=dict(t=50, b=20, l=20, r=20),
        legend=dict(
            font=dict(color=colors['text'], size=12),
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5
        ),
        height=400,  # Fixed height for consistency
        autosize=True,  # Allow responsiveness
        uniformtext_minsize=10,  # Minimum text size
        uniformtext_mode='hide',  # Hide text if too small
    )
    
    # Add improved text annotations
    fig1.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hoverinfo='label+percent+value',
        textfont=dict(size=12),
        insidetextorientation='radial'
    )

    # Plot two - Monthly Average Count of Pixels for Presumed Vegetation Fires
    veg_data = y_r_data.groupby('Month')['Count'].mean().reset_index()
    
    # Sort months in correct order
    veg_data['Month'] = pd.Categorical(veg_data['Month'], categories=month_order, ordered=True)
    veg_data = veg_data.sort_values('Month')
    
    fig2 = px.bar(
        veg_data,
        x='Month',
        y='Count',
        title='{} : Average Count of Pixels for Presumed Vegetation Fires in year {}'.format(input_region, input_year),
        color_discrete_sequence=[colors['accent']],
        template="plotly_dark"
    )
    
    fig2.update_layout(
        paper_bgcolor=colors['card_background'],
        plot_bgcolor=colors['card_background'],
        font=dict(color=colors['text']),
        title_font=dict(color=colors['text'], size=16),
        margin=dict(t=50, b=20, l=20, r=20),
        xaxis=dict(
            title_font=dict(color=colors['text']),
            tickfont=dict(color=colors['text']),
            gridcolor=colors['border'],
            tickangle=45,  # Angle the month labels for better readability
        ),
        yaxis=dict(
            title_font=dict(color=colors['text']),
            tickfont=dict(color=colors['text']),
            gridcolor=colors['border'],
        ),
        height=400,  # Fixed height for consistency
        autosize=True,  # Allow responsiveness
    )
    
    # Make it more responsive by ensuring the layout is efficient when resized
    return [
        html.Div([
            dcc.Graph(
                figure=fig1, 
                config={'displayModeBar': False, 'responsive': True},
                style={'height': '100%', 'width': '100%'},
                className='chart-container'
            )
        ], style={'height': '100%', 'width': '100%'}),
        
        html.Div([
            dcc.Graph(
                figure=fig2, 
                config={'displayModeBar': False, 'responsive': True},
                style={'height': '100%', 'width': '100%'},
                className='chart-container'
            )
        ], style={'height': '100%', 'width': '100%'})
    ]

if __name__ == '__main__':
    app.run()
