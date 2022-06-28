# Run this example easily with "nitro run URL".
# Get the nitro CLI: https://nitro.h2o.ai/cli/
#
# Like Nitro? Please star us on Github: https://github.com/h2oai/nitro
#
# ===
# About: How to use Altair in Nitro apps
# Author: Prithvi Prabhu <prithvi.prabhu@gmail.com>
# License: Apache-2.0
# Source: https://github.com/h2oai/nitro-matplotlib/examples
# Keywords: [visualization]
#
# Setup:
# FILE requirements.txt EOF
# altair
# vega_datasets
# Flask>=2
# simple-websocket>=0.5
# h2o-nitro[web]
# h2o-nitro-altair
# EOF
# RUN python -m pip install -r requirements.txt
# ENV FLASK_APP altair_basic.py
# ENV FLASK_ENV development
# START python -m flask run
# ===

import altair as alt
from altair import datum
from vega_datasets import data
import simple_websocket
from flask import Flask, request, send_from_directory

# ----- Nitro app -----

from h2o_nitro import View
from h2o_nitro_web import web_directory
from h2o_nitro_altair import altair_plugin, altair_box


# Entry point
def main(view: View):
    # Show plots one by one.
    view('## Ridgeline Plot', altair_box(make_altair_ridgeline()))
    view('## Choropleth', altair_box(make_altair_choropleth()))
    view('## Parallel Coordinates', altair_box(make_altair_parallel_coords()))
    view('## Streamgraph', altair_box(make_altair_streamgraph()))
    view('## Dot Dash Plot', altair_box(make_dot_dash_plot()))


# Nitro instance
nitro = View(
    main,
    title='Nitro + altair',
    caption='A minimal example',
    plugins=[altair_plugin()],  # Include the altair plugin
)


# ----- Altair visualization routines -----

def make_altair_ridgeline():
    # Source: https://altair-viz.github.io/gallery/ridgeline_plot.html

    source = data.seattle_weather.url

    step = 20
    overlap = 1

    chart = alt.Chart(source, height=step).transform_timeunit(
        Month='month(date)'
    ).transform_joinaggregate(
        mean_temp='mean(temp_max)', groupby=['Month']
    ).transform_bin(
        ['bin_max', 'bin_min'], 'temp_max'
    ).transform_aggregate(
        value='count()', groupby=['Month', 'mean_temp', 'bin_min', 'bin_max']
    ).transform_impute(
        impute='value', groupby=['Month', 'mean_temp'], key='bin_min', value=0
    ).mark_area(
        interpolate='monotone',
        fillOpacity=0.8,
        stroke='lightgray',
        strokeWidth=0.5
    ).encode(
        alt.X('bin_min:Q', bin='binned', title='Maximum Daily Temperature (C)'),
        alt.Y(
            'value:Q',
            scale=alt.Scale(range=[step, -step * overlap]),
            axis=None
        ),
        alt.Fill(
            'mean_temp:Q',
            legend=None,
            scale=alt.Scale(domain=[30, 5], scheme='redyellowblue')
        )
    ).facet(
        row=alt.Row(
            'Month:T',
            title=None,
            header=alt.Header(labelAngle=0, labelAlign='right', format='%B')
        )
    ).properties(
        title='Seattle Weather',
        bounds='flush'
    ).configure_facet(
        spacing=0
    ).configure_view(
        stroke=None
    ).configure_title(
        anchor='end'
    )

    return chart


def make_altair_choropleth():
    # Source: https://altair-viz.github.io/gallery/choropleth.html

    counties = alt.topo_feature(data.us_10m.url, 'counties')
    source = data.unemployment.url

    chart = alt.Chart(counties).mark_geoshape().encode(
        color='rate:Q'
    ).transform_lookup(
        lookup='id',
        from_=alt.LookupData(source, 'id', ['rate'])
    ).project(
        type='albersUsa'
    ).properties(
        width=500,
        height=300
    )

    return chart


def make_altair_parallel_coords():
    # Source: https://altair-viz.github.io/gallery/normed_parallel_coordinates.html

    source = data.iris()

    chart = alt.Chart(source).transform_window(
        index='count()'
    ).transform_fold(
        ['petalLength', 'petalWidth', 'sepalLength', 'sepalWidth']
    ).transform_joinaggregate(
        min='min(value)',
        max='max(value)',
        groupby=['key']
    ).transform_calculate(
        minmax_value=(datum.value - datum.min) / (datum.max - datum.min),
        mid=(datum.min + datum.max) / 2
    ).mark_line().encode(
        x='key:N',
        y='minmax_value:Q',
        color='species:N',
        detail='index:N',
        opacity=alt.value(0.5)
    ).properties(width=500)

    return chart


def make_altair_streamgraph():
    # Source: https://altair-viz.github.io/gallery/streamgraph.html

    source = data.unemployment_across_industries.url

    chart = alt.Chart(source).mark_area().encode(
        alt.X('yearmonth(date):T',
              axis=alt.Axis(format='%Y', domain=False, tickSize=0)
              ),
        alt.Y('sum(count):Q', stack='center', axis=None),
        alt.Color('series:N',
                  scale=alt.Scale(scheme='category20b')
                  )
    ).interactive()

    return chart


def make_dot_dash_plot():
    # Source: https://altair-viz.github.io/gallery/dot_dash_plot.html

    source = data.cars()

    # Configure the options common to all layers
    brush = alt.selection(type='interval')
    base = alt.Chart(source).add_selection(brush)

    # Configure the points
    points = base.mark_point().encode(
        x=alt.X('Miles_per_Gallon', title=''),
        y=alt.Y('Horsepower', title=''),
        color=alt.condition(brush, 'Origin', alt.value('grey'))
    )

    # Configure the ticks
    tick_axis = alt.Axis(labels=False, domain=False, ticks=False)

    x_ticks = base.mark_tick().encode(
        alt.X('Miles_per_Gallon', axis=tick_axis),
        alt.Y('Origin', title='', axis=tick_axis),
        color=alt.condition(brush, 'Origin', alt.value('lightgrey'))
    )

    y_ticks = base.mark_tick().encode(
        alt.X('Origin', title='', axis=tick_axis),
        alt.Y('Horsepower', axis=tick_axis),
        color=alt.condition(brush, 'Origin', alt.value('lightgrey'))
    )

    # Build the chart
    chart = y_ticks | (points & x_ticks)

    return chart


# ----- Flask boilerplate -----

app = Flask(__name__, static_folder=web_directory, static_url_path='')


@app.route('/')
def home_page():
    return send_from_directory(web_directory, 'index.html')


@app.route('/nitro', websocket=True)
def socket():
    ws = simple_websocket.Server(request.environ)
    try:
        nitro.serve(ws.send, ws.receive)
    except simple_websocket.ConnectionClosed:
        pass
    return ''


if __name__ == '__main__':
    app.run()
