import RPi.GPIO as GPIO

from http.server import BaseHTTPRequestHandler, HTTPServer



GPIO.setmode(GPIO.BCM)

GPIO.setup(20, GPIO.OUT)
GPIO.setup(21, GPIO.OUT)
GPIO.setup(26, GPIO.OUT)
GPIO.setup(16, GPIO.OUT)

GPIO.output(21,True)
GPIO.output(20,True)
GPIO.output(26,True)
GPIO.output(16,True)



Request = None



class RequestHandler_httpd(BaseHTTPRequestHandler):

  def do_GET(self):
      global Request

      messagetosend = bytes('Hellow Word',"utf")

      self.send_response(200)

      self.send_header('Content-Type', 'text/plain')

      self.send_header('Content-Length', len(messagetosend))

      self.end_headers()

      self.wfile.write(messagetosend)

      Request = self.requestline

      Request = Request[5 : int(len(Request)-9)]

      print(Request)

      if Request == 'on1':
        GPIO.output(21,False)

      if Request == 'off1':
        GPIO.output(21,True)
        
      if Request == 'on2':
        GPIO.output(20,False)

      if Request == 'off2':
        GPIO.output(20,True)
        
      if Request == 'on3':
        GPIO.output(26,False)

      if Request == 'off3':
        GPIO.output(26,True)
        
      if Request == 'on4':
        GPIO.output(16,False)

      if Request == 'off4':
        GPIO.output(16,True)

      return




server_address_httpd = ('192.168.0.128',8080)

httpd = HTTPServer(server_address_httpd, RequestHandler_httpd)

print('Starting server')

httpd.serve_forever()

GPIO.cleanup()