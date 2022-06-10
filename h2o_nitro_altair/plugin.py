# Copyright 2022 H2O.ai, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Optional
import json
from altair import Chart
from h2o_nitro import box, Box, Plugin, Script

# Javascript function for embedding the Altair plot.
# Here, we export one function called embed(), which we can later invoke from our Python box().
_embed_js = '''
exports.embed = (context, element, data) => {
    const spec = JSON.parse(data.spec), opt = JSON.parse(data.opt);
    vegaEmbed(element, spec, opt);
};
'''

# Ref: https://github.com/vega/vega-embed#directly-in-the-browser
# Versions obtained by inspecting chart.to_html()
# TODO: automate this based on currently installed version
VEGA_JS_PATH = 'https://cdn.jsdelivr.net/npm/vega@5'
VEGA_LITE_JS_PATH = 'https://cdn.jsdelivr.net/npm/vega-lite@4.17.0'
VEGA_EMBED_JS_PATH = 'https://cdn.jsdelivr.net/npm/vega-embed@6/build/vega-embed.js'


def altair_plugin(
        vega_js_path=VEGA_JS_PATH,
        vega_lite_js_path=VEGA_LITE_JS_PATH,
        vega_embed_js_path=VEGA_EMBED_JS_PATH,
):
    """
    Creates a Nitro plugin.
    :param vega_js_path: URL pointing to the Vega Javascript library.
    :param vega_lite_js_path: URL pointing to the Vega-Lite Javascript library.
    :param vega_embed_js_path: URL pointing to the vega-embed Javascript library.
    :return: A plugin
    """
    return Plugin(
        name='altair',
        scripts=[
            # Install the dependencies
            Script(source=vega_js_path),
            Script(source=vega_lite_js_path),
            Script(source=vega_embed_js_path),
            # Install our custom vega-embed Javascript.
            Script(source=_embed_js, type='inline'),
        ],
    )


_default_embed_opts = dict(
    mode='vega-lite',
    # Hide all actions except export to PNG/SVG
    actions=dict(
        source=False,
        compiled=False,
        editor=False,
    ),
)


def altair_box(chart: Chart, options: Optional[dict] = None) -> Box:
    """
    Creates a Nitro box from a Altair Chart.
    :param chart: An Altair Chart
    :param options: Vega embed options. See https://github.com/vega/vega-embed#options
    :return: A box
    """
    # Render the box using our custom embed() function defined in the "altair" plugin.
    return box(
        mode='plugin:altair.embed',
        data=dict(
            spec=chart.to_json(),
            opt=json.dumps(_default_embed_opts if options is None else {**_default_embed_opts, **options}),
        ),
        ignore=True,
    )
