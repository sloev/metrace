import argparse
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir[: current_dir.rfind(os.path.sep)])


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected.")


def cli():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="subparser")

    run_command_parser = subparsers.add_parser("run")
    run_command_parser.add_argument("command", nargs=1, help="Command to run")
    run_command_parser.add_argument(
        "command_args", nargs=argparse.REMAINDER, help="arguments to the commandline"
    )

    plot_parser = subparsers.add_parser("plot")
    plot_parser.add_argument(
        "--autoopen",
        type=str2bool,
        nargs="?",
        const=True,
        default=True,
        help="Open report in default browser (default: yes)",
    )
    plot_parser.add_argument(
        "-i",
        "--trace_filename",
        type=str,
        default=None,
        help="Trace filename to plot (default: latest in dir)",
    )
    plot_parser.add_argument(
        "-o",
        "--output_filename",
        type=str,
        default=None,
        help="Output filename (default:  metrace_report.html in dir)",
    )
    kwargs = vars(parser.parse_args())
    subparser = kwargs.pop("subparser")

    if not subparser:
        parser.print_help()
        exit(0)

    if subparser == "run":
        from metrace.run_command import run_command

        command_line = kwargs["command"] + kwargs["command_args"]
        run_command(command_line)
    elif subparser == "plot":
        from metrace.plot_command import generate_html_report

        generate_html_report(**kwargs)


if __name__ == "__main__":
    cli()
