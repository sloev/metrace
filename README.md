# Metrace - cpu/memory tracing for process trees

Metrace makes it easy to get a nice interactive html plot of the cpu/memory usage of a whole process tree.

## Install

Metrace depends on `Plotly` and `Psutil`, both will be installed with metrace using pip:

```
$ pip install metrace
```

## Client usage (optional)

Metrace lets you annotate specific parts of your code with scopes and these will become part of your final plot output.



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

