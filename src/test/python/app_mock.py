#!/usr/bin/env python3

import http.server
import logging
import os
import platform
import socketserver
import sys
import time
import urllib.request
from urllib.request import Request, urlopen

def make_handler(appId, version, url):
    """
    Factory method that creates a handler class.
    """

    class Handler(http.server.SimpleHTTPRequestHandler):

        def handle_ping(self):
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()

            marathonId = os.getenv("MARATHON_APP_ID", "NO_MARATHON_APP_ID_SET")
            msg = "Pong {}".format(marathonId)

            self.wfile.write(bytes(msg, "UTF-8"))
            return


        def check_health(self):
            logging.debug("Query %s for health", url)
            url_req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urlopen(url_req) as response:
                res = response.read()
                status = response.status
                logging.debug("Current health is %s, %s", res, status)

                self.send_response(status)
                self.send_header('Content-type','text/html')
                self.end_headers()

                self.wfile.write(res)

            logging.debug("Done processing health request.")
            return


        def do_GET(self):
            try:
                logging.debug("Got GET request")
                if self.path == '/ping':
                    return self.handle_ping()
                else:
                    return self.check_health()
            except:
                logging.exception('Could not handle GET request')
                raise


        def do_POST(self):
            try:
                logging.debug("Got POST request")
                return self.check_health()
            except:
                logging.exception('Could not handle GET request')
                raise


    return Handler


if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s: %(message)s',
        level=logging.DEBUG)
    logging.info(platform.python_version())
    logging.debug(sys.argv)

    port = int(sys.argv[1])
    appId = sys.argv[2]
    version = sys.argv[3]
    url = "{}/{}".format(sys.argv[4], port)
    # url = sys.argv[4]
    taskId = os.getenv("MESOS_TASK_ID", "<UNKNOWN>")

    httpd = socketserver.TCPServer(("", port), make_handler(appId, version, url))
    msg = "AppMock[{0} {1}]: {2} has taken the stage at port {3}. Will query {4} for health status.".format(appId, version, taskId, port, url)
    print(msg)
    logging.debug(msg)
    httpd.serve_forever()


