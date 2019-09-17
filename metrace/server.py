from http.server import SimpleHTTPRequestHandler
import sys
import base64
from os import environ
import socketserver
from multiprocessing import Process
import atexit
import logging
import threading


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True


def run_forever(q, password, port):
    class MetraceHandler(SimpleHTTPRequestHandler):
        """ Main class to present webpages and authentication. """

        def do_POST(self):
            """ Present frontpage with user authentication. """
            auth = self.headers.get("Authorization", "")
            if auth == "Basic " + password:
                content_len = int(self.headers.get("content-length", 0))
                post_body = self.rfile.read(content_len).decode("utf-8")
                q.put(post_body)
            return "ok"

    server = ThreadedTCPServer(("localhost", port), MetraceHandler)
    logging.debug("starting http server")
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    def terminate():
        logging.debug("shutting down server")
        server.shutdown()
        server.server_close()
        logging.debug("waiting for server thread")
        server_thread.join()
        logging.debug("server is shutdown")

    return terminate
