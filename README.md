# Metrace - cpu/memory tracing for process trees

Metrace makes it easy to get a nice interactive html plot of the cpu/memory usage of a whole process tree.

![metrace report](https://raw.githubusercontent.com/sloev/metrace/master/docs/report.png =200x)

## Install

Metrace depends on `Plotly` and `Psutil`, both will be installed with metrace using pip:

```
$ pip install metrace
```

## Client usage (optional)

Metrace lets you annotate specific parts of your code with scopes and these will become part of your final plot output and end up look like this:

![metrace trace annotation](https://raw.githubusercontent.com/sloev/metrace/master/docs/trace_annotation.png)

Metrace gives you a context manager `trace` you can wrap code blocks with:

```
$ cat foobar.py

from metrace import trace

with trace('creating 1000 objects'):
    l = []
    for i in range(1000):
        l.append(object())
```

To collect these traces you run your script with metrace as usual:

```
$ metrace run python foobar.py
```

## Commandline Usage

After installation you will have the **metrace** command available.

It has two subcommands:

### run

```
$ metrace run python foobar.py
```

Runs a process and collects cpu/memory metrics for both the process and its children seperately.

Metrace outputs the metrics in a json file in current working directory named like: `metrace_1568385178098218.json` with the number being milliseconds since epoch.

### plot

```
$ metrace plot
# or
# to not open the html report automatically:
$ metrace plot --autoopen=no
# or
# to specify input/output files
$ metrace plot -i metrace_1568385178098218.json -o metrace_report.html
```

Plots cpu/memory usage for a given, or latest found, `metrace json file`.

Output is a html file where you can download the images, zoom in and hover to inspect the different traces.


## Samples

Docs folder contains a sample of a [metrace json file](./docs/metrace_1568385178098218.json) and a [metrace html report](./docs/metrace_report.html)