import urllib.parse
import pathlib
import mimetypes
import json
import socket
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
from threading import Thread

class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/':
            self.send_html_file('index.html')
        elif pr_url.path == '/contact':
            self.send_html_file('message.html')
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file('error.html', 404)

    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        data_parse = urllib.parse.unquote_plus(data.decode())
        run_socket_client(data_parse)
        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())


def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ('', 8000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


def run_socket_server(port):
    print("Socket server activated")
    host = socket.gethostname()
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((host, port))
    try:
        while True:
            data, address = server.recvfrom(1024)
            print(data, address)
            message_dict_data = message_dict(data.decode())
            save_storage(message_dict_data)
    except KeyboardInterrupt:
        print("Socket server destroyed")
    finally:
        server.close()


def run_socket_client(message):
    print("Client activated")
    host = socket.gethostname()
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server = host, 5000
    encoded_message = message.encode()
    client.sendto(encoded_message, server)
    client.close()


def message_dict(data_parse):
    data_dict = {str(datetime.now()): {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}}
    return data_dict


def save_storage(data_dict):
    with open('storage/data.json', 'r+') as f:
        storage_json = json.load(f)
        storage_json.update(data_dict)
        f.seek(0)
        json.dump(storage_json, f, indent=4)


if __name__ == '__main__':
    th1 = Thread(target=run)
    th2 = Thread(target=run_socket_server, args=(5000, ))
    th1.start()
    th2.start()
