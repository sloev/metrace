import plotly.graph_objects as go
from plotly import offline
from datetime import timedelta, datetime
from collections import defaultdict
import json
import time
import os
import glob
from metrace import plotly_js_source
import webbrowser


def utc_epoch_to_local_datetime(utc_epoch):
    offset = datetime.fromtimestamp(utc_epoch) - datetime.utcfromtimestamp(utc_epoch)
    utc = datetime.utcfromtimestamp(utc_epoch)
    return utc + offset


def interpolate(target_x, ref_x, ref_y):
    x0 = y0 = x1 = y1 = 0
    for x, y in zip(ref_x, ref_y):
        if target_x > x:
            x0 = x
            y0 = y
        if target_x < x and x0:
            x1 = x
            y1 = y
            break
    if not x0:
        return None

    rate = (y1 - y0) / (x1 - x0)
    target_y = ((target_x - x0) * rate) + y0
    return target_y


def format_bytes(size, field):
    if field != "memory_bytes":
        return 1, "%"
    # 2**10 = 1024
    power = 2 ** 10
    n = 0
    power_labels = {0: "B", 1: "KB", 2: "MB", 3: "GB", 4: "TB"}
    while size > power:
        size /= power
        n += 1
    return max(power ** n, 1), power_labels[n]


def generate_figure(json_data, field, title):

    color_pallette_traces = [
        "rgba(255, 215, 180, 120)",
        "rgba(230, 25, 75, 120)",
        "rgba(60, 180, 75, 120)",
        "rgba(255, 225, 25, 120)",
        "rgba(0, 130, 200, 120)",
        "rgba(245, 130, 48, 120)",
        "rgba(145, 30, 180, 120)",
        "rgba(70, 240, 240, 120)",
        "rgba(170, 110, 40, 120)",
        "rgba(240, 50, 230, 120)",
        "rgba(255, 250, 200, 120)",
        "rgba(170, 255, 195, 120)",
        "rgba(210, 245, 60, 120)",
        "rgba(250, 190, 190, 120)",
        "rgba(0, 128, 128, 120)",
        "rgba(230, 190, 255, 120)",
    ]
    color_pallette_pid = [
        "rgb(158,1,66)",
        "rgb(213,62,79)",
        "rgb(244,109,67)",
        "rgb(253,174,97)",
        "rgb(254,224,139)",
        "rgb(230,245,152)",
        "rgb(171,221,164)",
        "rgb(102,194,165)",
        "rgb(50,136,189)",
        "rgb(94,79,162)",
    ]
    color_pop_index = 0 if field == "memory_bytes" else -1
    consumption_over_time = defaultdict(lambda: defaultdict(list))
    hover_text = "Memory" if field == "memory_bytes" else "CPU"

    for row in json_data:
        if row["type"] == "metrics":
            utc_epoch = row["utc_epoch"]

            for pid, metrics in row["properties"].items():
                consumption_over_time[pid]["x"].append(utc_epoch)
                consumption_over_time[pid]["y"].append(metrics[field])

    max_used = 0
    min_used = 0
    traces = []
    for pid, data in consumption_over_time.items():
        try:
            c = color_pallette_pid.pop(color_pop_index)
        except:
            print("Not enough colors for processes")
            break

        m = max(data["y"])

        max_used = max(m, max_used)
        min_used = min(m, min_used)
        divider, unit = format_bytes(m, field)
        traces.append(
            go.Scatter(
                x=[utc_epoch_to_local_datetime(utc_epoch) for utc_epoch in data["x"]],
                y=data["y"],
                name=f"pid: {pid}",
                mode="lines+markers",
                line={"color": c},
                text=["{:.2f}{}".format(y / divider, unit) for y in data["y"]],
                hovertemplate=hover_text + " : %{text}",
            )
        )
    max_used = int(max_used * 1.1)
    trace_radius = max_used / 20
    min_used = int(min_used - trace_radius)
    divider, unit = format_bytes(max_used, field)
    if not max_used:
        ticks = [0.0, 1.0]
        tick_text = []
    else:
        ticks = [x for x in range(0, max_used, int(max_used / 10.0))]
    tick_text = ["{:.2f}{}".format(x / divider, unit) for x in ticks]

    annotations = defaultdict(lambda: defaultdict(list))

    for row in json_data:
        if row["type"] == "trace":
            properties = row["properties"]
            pid = properties["pid"]
            ref_x = consumption_over_time[pid]["x"]
            ref_y = consumption_over_time[pid]["y"]
            target_x = row["utc_epoch"]
            target_y = interpolate(target_x, ref_x, ref_y)

            target_x = utc_epoch_to_local_datetime(target_x)
            name = properties["name"]
            annotations[pid][name].append(dict(x=target_x, y=target_y, **properties))

    info_traces = []
    for pid in annotations:
        for name, array in annotations[pid].items():
            tmp = None
            x = [None]
            y_low = [None]
            y_high = [None]
            for d in array:
                if d["type"] == "begin":
                    tmp = d
                elif d["type"] == "end" and tmp:
                    if d["y"] is None:
                        tmp = None
                        continue
                    items = [
                        {"x": datetime.utcfromtimestamp(x / 1000.0), "y": y}
                        for x, y in zip(
                            consumption_over_time[pid]["x"],
                            consumption_over_time[pid]["y"],
                        )
                    ]

                    in_between = [
                        item for item in items if tmp["x"] < item["x"] < d["x"]
                    ]

                    x.extend(
                        [tmp["x"] - timedelta(seconds=0.000001), tmp["x"]]
                        + [e["x"] for e in in_between]
                        + [d["x"], d["x"] + timedelta(seconds=0.000001)]
                    )
                    y_low.extend(
                        [tmp["y"], tmp["y"] - trace_radius]
                        + [e["y"] - trace_radius for e in in_between]
                        + [d["y"] - trace_radius, d["y"]]
                    )
                    y_high.extend(
                        [tmp["y"], tmp["y"] + trace_radius]
                        + [e["y"] + trace_radius for e in in_between]
                        + [d["y"] + trace_radius, d["y"]]
                    )
                    tmp = None
            try:
                c = color_pallette_traces.pop(color_pop_index)
            except:
                print("not enough colors for traces, max 12")
                break

            info_traces.append(
                go.Scatter(
                    name=f"trace: {name}",
                    x=x + x[::-1],
                    y=y_high + y_low[::-1],
                    fillcolor=c,
                    fill="tozeroy",
                    text=[name] * len(x) * 2,
                    line=dict(color="rgba(255,255,255,0)"),
                    hovertemplate="trace: %{text}",
                )
            )

    layout = go.Layout(
        plot_bgcolor="rgba(240,240,240,10)",
        title=title,
        yaxis=go.layout.YAxis(
            range=[min_used, max_used], tickvals=ticks, ticktext=tick_text
        ),
        width=800,
        height=400,
    )

    fig = go.Figure(info_traces + traces, layout)

    return fig


def generate_html_report(trace_filename=None, output_filename=None, autoopen=True):
    current_date_string = datetime.now().isoformat()
    cwd = os.getcwd()
    if output_filename is None:
        output_filename = os.path.join(cwd, "metrace_report.html")

    if trace_filename is None:
        latest_trace = sorted(glob.glob(f"{cwd}/metrace_*.json"))[-1]
        trace_filename = os.path.join(cwd, latest_trace)

    json_data = []

    with open(trace_filename) as f:
        for l in f.readlines():
            json_data.append(json.loads(l))

    json_data = sorted(json_data, key=lambda x: x["utc_epoch"])

    mem_fig = generate_figure(json_data, "memory_bytes", "Memory Consumption")
    cpu_fig = generate_figure(json_data, "cpu", "CPU Consumption")

    mem_div = offline.plot(mem_fig, include_plotlyjs=False, output_type="div")
    cpu_div = offline.plot(cpu_fig, include_plotlyjs=False, output_type="div")
    html_begin = f"""
        <head>
        <meta charset="utf-8" />
        <title>Metrace Report</title></head>
        <body>
        <h1>Metrace report generated at {current_date_string}</h1>
        <br/>
    """

    html_end = f"""
        {mem_div}
        <br/>
        {cpu_div}
        </body>
        </html>
    """
    with open(output_filename, "w") as f:
        f.write(html_begin)
        f.write(plotly_js_source.plotly_js_string)
        f.write(html_end)
    if autoopen:
        webbrowser.open(f"file://{output_filename}")


if __name__ == "__main__":
    generate_html_report()
