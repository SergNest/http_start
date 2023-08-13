from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import mimetypes
import pathlib
import socket
import json
import os
from datetime import datetime
from threading import Thread

class HttpHandler(BaseHTTPRequestHandler):
   
    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        data_parse = urllib.parse.unquote_plus(data.decode())
        self.run_client_soket(data_parse)
        print(data_parse)
        self.send_response(302)
        self.send_header('Location', '/message')
        self.end_headers()
        
        
    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/':
            self.send_html_file('index.html')
        elif pr_url.path == '/message':
            self.send_html_file('message.html')
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file('error.html', 404)

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

    def run_client_soket(self, send_data):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server = UDP_IP, UDP_PORT
        data = send_data.encode()
        sock.sendto(data, server)
        sock.close()

def run():
    srv_server = Thread(target=run_server)
    srv_soket = Thread(target=run_soket)
    srv_server.start()
    srv_soket.start()

UDP_IP = '127.0.0.1'
UDP_PORT = 5000

def run_server(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ('', 3000)
    http = server_class(server_address, handler_class)
    
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()

def run_soket():
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server = (UDP_IP, UDP_PORT)
    sock.bind(server)
    # sock.listen(2)
    if not os.path.exists('storage'):
        os.makedirs('storage')
    try:
        while True:
            data, address = sock.recvfrom(1024)
            
            try:
                parsed_data = urllib.parse.parse_qs(data.decode())
                
                username = parsed_data.get('username', [''])[0]
                message = parsed_data.get('message', [''])[0]
                
                if username and message:
                    received_data = {
                        'username': username,
                        'message': message
                    }
                
                timestamp = str(datetime.now())
                
                data_to_save = {timestamp: received_data}
                
                if os.path.exists('storage/data.json'):
                    with open('storage/data.json', 'r') as file:
                        existing_data = json.load(file)
                else:
                    existing_data = {}

                existing_data.update(data_to_save)

                with open('storage/data.json', 'w') as file:
                    json.dump(existing_data, file, indent=2)
            
                print(f"Received and saved data from {address}")
        
            except json.JSONDecodeError:
                print(f"Failed to decode JSON data from {address}")
            
    except KeyboardInterrupt:
        print(f'Destroy server')
    finally:
        sock.close()

if __name__ == '__main__':
    run()
   