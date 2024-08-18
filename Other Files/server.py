

from http.server import BaseHTTPRequestHandler, HTTPServer



class RequestHandler_httpd(BaseHTTPRequestHandler):

  def do_GET(self):

    messagetosend = bytes('Hellow world',"utf")

    self.send_response(200)

    self.send_header('Content-Type', 'text/plain')

    self.send_header('Content-Length', len(messagetosend))

    self.end_headers()

    self.wfile.write(messagetosend)

    print(self.requestline)

    return





server_address_httpd = ('192.168.0.128',8080)

httpd = HTTPServer(server_address_httpd, RequestHandler_httpd)

print('Starting server')

httpd.serve_forever()