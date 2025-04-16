import pandas as pd
import numpy as np
import plotly.graph_objs as go
from dash import Dash, dcc, html, Input, Output


df = pd.read_csv("Results_21Mar2022.csv")


indicators = ['mean_ghgs_ch4', 'mean_acid', 'mean_eut', 'mean_watscar', 'mean_bio']

# delete
df = df.dropna(subset=indicators + ['diet_group', 'sex'])

valid_diet_groups = ['fish', 'meat', 'meat50', 'meat100', 'vegan', 'veggie']
df = df[df['diet_group'].isin(valid_diet_groups)]

# group
df_grouped = df.groupby(['diet_group', 'sex'])[indicators].mean().reset_index()

# Min-Max
df_grouped[indicators] = df_grouped[indicators].apply(
    lambda x: (x - x.min()) / (x.max() - x.min()))

 
heatmap_df = df_grouped.groupby('diet_group')[indicators].mean().T


app = Dash(__name__)

app.layout = html.Div([
    html.H1("Diet and Environmental Impact Analysis", style={'textAlign': 'center'}),

    dcc.Graph(id='heatmap'),

    dcc.Graph(id='radar_chart')
])


@app.callback(
    Output('heatmap', 'figure'),
    Input('radar_chart', 'figure')  
)
def render_heatmap(_):
    heatmap_fig = go.Figure(data=go.Heatmap(
        z=heatmap_df.values,
        x=heatmap_df.columns,
        y=heatmap_df.index,
        colorscale='YlOrRd',
        zmin=0,
        zmax=1,
        text=np.round(heatmap_df.values, 2),
        hovertemplate='Diet: %{x}<br>Indicator: %{y}<br>Value: %{z:.2f}<extra></extra>',
        colorbar=dict(title='Normalized Value')
    ))

    heatmap_fig.update_layout(
        title={'text': '🌱 Environmental Impact Heatmap by Diet Group', 'x': 0.5},
        xaxis_title='Diet Group',
        yaxis_title='Environmental Indicators',
        clickmode='event+select',
        margin=dict(t=80, b=60)
    )

    return heatmap_fig


@app.callback(
    Output('radar_chart', 'figure'),
    Input('heatmap', 'clickData')
)
def update_radar(clickData):
   
    diet_group = clickData['points'][0]['x'] if clickData else 'meat'

    filtered_df = df_grouped[df_grouped['diet_group'] == diet_group]

    radar_data = []
    for sex in filtered_df['sex'].unique():
        df_sex = filtered_df[filtered_df['sex'] == sex]
        radar_data.append(go.Scatterpolar(
            r=df_sex[indicators].values.flatten(),
            theta=indicators,
            fill='toself',
            name=f'{sex}',
            line=dict(shape='spline')
        ))

    radar_fig = go.Figure(data=radar_data)
    radar_fig.update_layout(
        title={'text': f'Radar Chart: {diet_group}', 'x': 0.5},
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        showlegend=True,
        margin=dict(t=60, b=30)
    )

    return radar_fig

# run
if __name__ == '__main__':
    app.run(debug=True)
