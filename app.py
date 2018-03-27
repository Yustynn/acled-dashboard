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

    # data,
    # x=~YEAR,
    # y=~NUM_EVENTS,
    # type='scatter',
    # mode='markers',
    # color=~EVENT_TYPE,
    # colors= "Set1",
    # hoverinfo='text',
    # text=~glue('Event: {EVENT_TYPE}<br>No. of Fatalities: {FATALITIES}<br>Year: {YEAR}<br>Number of Events: {NUM_EVENTS}'),
    # hoverlabel=list(bgcolor='rgb(40,40,40)', font=list(color='rgb(200,200,200)')),
    # sizes = c(30, 1000),
    # size=~FATALITIES,
    # marker=list(
        # opacity=.8
    # )

cf_bubble = dcc.Graph(
    id='cf-bubble',
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
            xaxis={'title': 'Year'},
            yaxis={'title': 'Number of Events'},
            hovermode='closest'
        )
    )
)


layout = html.Div([
    html.Div(
        cf_bubble,
        style={'width': '59%', 'display': 'inline-block'}
    ),
    html.Div(
        [
            dcc.Graph(id='fatal-time'),
            dcc.Graph(id='event-years'),
        ],
        style={'width': '39%', 'display': 'inline-block'}
    )
])

# Barebones layout
app.layout = html.Div([
    dcc.Interval(id='refresh', interval=200),
    html.Div(id='content', className="container"),
    html.H1('HI', id='test')
])

# Update the `content` div with the `layout` object.
# When you save this file, `debug=True` will re-run
# this script, serving the new layout
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
    p = re.compile('\s(.+)<')
    hover_text = hover_data['points'][0]['text']
    event = p.search(hover_text).groups()[0]

    across_years = by_event[by_event.index.get_level_values('EVENT_TYPE') == event]

    return dict(
        data=[
            go.Bar(
                x=across_years.index.get_level_values('YEAR'),
                y=across_years.tolist()
            )
        ]
    )

app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})

if __name__ == '__main__':
    app.run_server(debug=True)
