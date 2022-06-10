# Altair plugin for H2O Nitro

This plugin lets you use [Altair](https://altair-viz.github.io/index.html) visualizations in
[Nitro](https://github.com/h2oai/nitro) apps.

## Demo

![Demo](demo.gif)

[View source](examples/altair_basic.py).

## Install

```
pip install h2o-nitro-altair
```

## Usage

1. Import the plugin:

```py 
from h2o_nitro_altair import altair_plugin, altair_box
```

2. Register the plugin:

```py 
nitro = View(main, title='My App', caption='v1.0', plugins=[altair_plugin()])
```

3. Use the plugin:

```py 
# Make a chart:
chart = alt.Chart(data.cars()).mark_point().encode(
    x='Horsepower',
    y='Miles_per_Gallon',
    color='Origin',
).interactive()

# Display the chart:
view(altair_box(chart))
```

## Advanced Usage

You can pass [Vega Embed Options](https://github.com/vega/vega-embed#options) to `altair_box()` for
more control:

```py
altair_box(chart, options=dict(renderer='svg', scaleFactor=2))
```

## Change Log

- v0.1.1 - Jun 09, 2022
    - Fixed
        - Don't return value from plots.
- v0.1.0 - May 25, 2022
    - Initial Version
