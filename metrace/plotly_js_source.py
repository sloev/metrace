import os

with open(os.path.join(os.path.dirname(__file__), "plotly_latest.min.js")) as f:
    plotly_js_string = f.read()
