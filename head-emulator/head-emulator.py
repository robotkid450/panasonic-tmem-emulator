from http.server import BaseHTTPRequestHandler, HTTPServer

hostName = "localhost"
serverPort = 8000



class Head():
    def __init__(self) -> None:
        self.power = 0
        self.installPosition = "0"
        self.smartPictureFlip = "0"
        self.smartPictureFlipAngle = "3C"
        self.pos = ("8000", "8000")
        self.zoom = "555"
        self.focus = "555"
        self.focusMode = "0"
        self.iris = "01"
        self.irisMode = "0"
        self.preset = "00"
        self.presetSpeed = "250"

    def powerSet(self, value):
        self.power = value
        return self.power

    def powerQuery(self):
        return self.power
    
    def installPosSet(self, value):
        self.installPosition = value
        return self.installPosition
    
    def installPosQuery(self):
        return self.installPosition

    def smartPicFlipSet(self, value):
        self.smartPictureFlip = value
        return self.smartPictureFlip
    
    def smartPicFlipQuery(self):
        return self.smartPictureFlip
    
    def smartPicFlipAngleSet(self, value):
        self.smartPictureFlipAngle = value
        return self.smartPictureFlipAngle

    def posSet(self, pan, tilt):
        self.pos = (pan, tilt)
        return self.pos
    
    def posQuery(self):
        return self.pos

        


class Server(BaseHTTPRequestHandler):
    
    def do_GET(self):

        pathSplit = self.path.split('/')
        pathSplit.pop(0) # disregaurd empty first item
        print(pathSplit)
        if pathSplit[0] != "cgi-bin":
            self.send_bad_url()
            # return -1
        else:
            cmdSplit = pathSplit[1].split("?")
            
            if cmdSplit[0] != "aw_ptz":
                self.send_bad_url()
                
            else:
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()


        # self.send_response(200)
        # self.send_header("Content-type", "text/html")
        # self.end_headers()
        # self.wfile.write(bytes("<html><head><title>https://pythonbasics.org</title></head>", "utf-8"))
        # self.wfile.write(bytes("<p>Request: %s</p>" % self.path, "utf-8"))
        # self.wfile.write(bytes("<body>", "utf-8"))
        # self.wfile.write(bytes("<p>This is an example web server.</p>", "utf-8"))
        # self.wfile.write(bytes("</body></html>", "utf-8"))
        
        # print(self.path)
        # print(self.path.split('/'))
        # print(self.requestline)
        exit()
        pass
        

    def send_bad_url(self):
        self.send_response(404)
        self.send_header("Content-type", "text/html")
        self.end_headers()


if __name__ =="__main__" :
    webServer = HTTPServer((hostName, serverPort), Server)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")