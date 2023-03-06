import http.server
import os
import socketserver
import threading

import http.server
import socketserver

PORT = 28960
DIRECTORY = "httpserver_dir"

# os.environ['PYTHONMALLOC'] = 'malloc'

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)


class WebServerThread(threading.Thread):
    def run(self):

        with socketserver.TCPServer(("192.168.1.92", PORT), Handler) as httpd:
            print("serving at port", PORT)
            print(f"Serving from directory: {DIRECTORY}")
            httpd.serve_forever()

server_thread = WebServerThread()
server_thread.start()
