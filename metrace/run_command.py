from functools import lru_cache

from multiprocessing.connection import Listener, Client
from os import environ, getpid
from contextlib import contextmanager
import time
import atexit
import http.client
import json
from multiprocessing import Queue
import subprocess
import sys
from queue import Empty as QueueIsEmpty
import psutil
import logging
from socket import socket
import random
import string
from datetime import datetime

from metrace.server import run_forever


def post(data, tries=2):
    client = getattr(post, "client", None)
    if not client:
        port = int(environ["METRACE_PORT"])
        password = environ["METRACE_PASSWORD"]
        client = http.client.HTTPConnection("localhost", port)
        setattr(post, "client", client)
    try:
        client.request(
            "POST",
            "/",
            json.dumps(data),
            headers={"Authorization": "Basic " + password},
        )
        logging.debug("post success")
    except:
        setattr(post, "client", None)
        if tries:
            return post(data, tries - 1)
        else:
            logging.debug("post failed")
            return None


__EPOCH = datetime(1970, 1, 1)


def get_epoch():
    return (datetime.utcnow() - __EPOCH).total_seconds()


@contextmanager
def trace(name):
    pid = str(getpid())
    post(
        {
            "type": "trace",
            "utc_epoch": get_epoch(),
            "properties": {"name": name, "type": "begin", "pid": pid},
        }
    )
    yield
    post(
        {
            "type": "trace",
            "utc_epoch": get_epoch(),
            "properties": {"name": name, "type": "end", "pid": pid},
        }
    )


def find_available_port():
    with socket() as s:
        s.bind(("", 0))
        port = s.getsockname()[1]
    return port


def generate_password():
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(32))


def gather_info_tree_string(root_pid):
    p = psutil.Process(root_pid)
    processes = [p] + p.children(recursive=True)
    struct = {}
    for p in processes:
        pid = p.pid
        struct[pid] = {
            "cpu": p.cpu_percent(interval=0.001),
            "memory_bytes": p.memory_info()[0],
        }
    return json.dumps(
        {"type": "metrics", "utc_epoch": get_epoch(), "properties": struct}
    )


@contextmanager
def get_file_writer():
    with open(f"metrace_{int(time.time()*1000000)}.json", "w") as f:

        def write(s):
            f.write(s + "\n")
            f.flush()

        yield write


def run_command(command_line, interval_in_seconds=0.5):
    port = find_available_port()
    password = generate_password()
    q = Queue()
    terminate_server = run_forever(q, password, port)
    env = environ.copy()
    env.update({"METRACE_PORT": str(port), "METRACE_PASSWORD": password})
    command_process = subprocess.Popen(command_line, env=env)
    command_pid = command_process.pid

    last_sample_time = time.time()
    try:
        with get_file_writer() as write:
            info = gather_info_tree_string(command_pid)
            write(info)
            while True:
                try:
                    exit_code = command_process.wait(0)
                    exit(exit_code)
                except subprocess.TimeoutExpired:
                    pass
                try:
                    trace = q.get(False)
                    write(trace)
                except QueueIsEmpty:
                    pass
                now = time.time()
                if last_sample_time + interval_in_seconds < now:
                    info = gather_info_tree_string(command_pid)
                    write(info)
                    last_sample_time = now + interval_in_seconds

    except SystemExit:
        pass
    except KeyboardInterrupt:
        pass
    except:
        logging.exception("Error")
        command_process.kill()
    finally:
        logging.debug("terminating server")
        terminate_server()
        logging.debug("done")
