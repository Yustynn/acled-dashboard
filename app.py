import dash
from dash.dependencies import Event, Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

import pandas as pd
import re

df = pd.read_csv('filtered_acled.csv')
by_event = df.groupby(['EVENT_TYPE', 'YEAR']).FATALITIES.sum()
events = df.EVENT_TYPE.unique()
years = df.YEAR.unique()

app = dash.Dash()
app.config['suppress_callback_exceptions']=True

cf_bubble = dcc.Graph(
    id='cf-bubble',
    style={'height': '700px'},
    figure=dict(
        data=[
            go.Scatter(
                x=[year for event in events for year in years],
                y=[len(df[(df.EVENT_TYPE == event) & (df.YEAR == year)]) for event in events for year in years],
                name='looool',
                text=[
                    'Event: {}<br>Fatalities: {}'.format(
                        event,
                        fatalities
                    ) for event in events for fatalities in by_event[event]
                ],
                mode='markers',
                marker=dict(
                    size=[fatalities for event in events for fatalities in by_event[event]],
                    sizeref= 2*by_event.max()/(50**2),
                    sizemode='area',
                    color=[idx for idx, event in enumerate(events) for year in years],
                    sizemin=5
                ),
            )
        ],
        colors='Set1',
        layout=go.Layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            title='Number of Fatalities by Size of Bubble',
            xaxis={'title': 'Year'},
            yaxis={'title': 'Number of Events'},
            hovermode='closest'
        )
    )
)


layout = html.Div(
    cf_bubble
)

app.layout = html.Div([
    html.H1(
        'Visualizations of Violent Events in Africa',
        style={'text-align': 'center'}
    ),
    html.Div([
        dcc.Interval(id='refresh', interval=200),
        html.Div(id='content', className="container"),
        html.Div(
            [
                dcc.Graph(
                    id='fatal-time',
                    style={'height': '350px'}
                ),
                dcc.Graph(
                    id='event-years',
                    style={'height': '350px'}
                ),
            ],
            style={'width': '39%', 'display': 'inline-block'}
        )],
        style={'display': 'flex'}
    )
])

def extract_event_year(hover_data):
    p = re.compile('\s(.+)<')
    point = hover_data['points'][0]
    hover_text = point['text']

    event = p.search(hover_text).groups()[0]
    year = point['x']

    return event, year

@app.callback(
    Output('content', 'children'),
    events=[Event('refresh', 'interval')])
def display_layout():
    return layout

@app.callback(
    Output('event-years', 'figure'),
    [Input('cf-bubble', 'hoverData')],
)
def update_event_years(hover_data):
    event, year = extract_event_year(hover_data)
    across_years = by_event[by_event.index.get_level_values('EVENT_TYPE') == event]

    return dict(
        data=[
            go.Bar(
                x=across_years.index.get_level_values('YEAR'),
                y=across_years.tolist()
            )
        ],
        layout=go.Layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            title='Fatalities from<br>{} over the Years'.format(event),
            xaxis={'title': 'Cumulative Fatalities'},
            yaxis={'title': 'Time'},
            hovermode='closest'
        )
    )

@app.callback(
    Output('fatal-time', 'figure'),
    [Input('cf-bubble', 'hoverData')],
)
def update_event_years(hover_data):
    event, year = extract_event_year(hover_data)

    fatalities = df[
        (df.YEAR == year) & (df.EVENT_TYPE == event)
    ][['EVENT_DATE', 'FATALITIES']]

    fatalities.EVENT_DATE = pd.to_datetime(fatalities.EVENT_DATE)

    fatalities = fatalities.set_index('EVENT_DATE').resample('M').sum()

    return dict(
        data=[
            go.Scatter(
                x=fatalities.index,
                y=fatalities.cumsum().FATALITIES.values,
                line=dict(color='rgb(127, 166, 238)'),
                fill='tonexty'
            )
        ],
        layout=go.Layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            title='Cumulative Distribution of Fatalities from <br>{} over {}'.format(event, year),
            xaxis={'title': 'Fatalities'},
            yaxis={'title': 'Year'},
            hovermode='closest'
        )
   )


# app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})

if __name__ == '__main__':
    app.run_server(debug=True)
