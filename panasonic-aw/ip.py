import requests

class camera:
    def __init__(self, address):
        self.address = address

    def sendCommand(self, command):
        command_to_send = 'http://' + self.address + '/cgi-bin/aw_ptz?cmd=' + command +"&res=1"
        print(command_to_send)
        #requests.get(command_to_send)


if __name__ == '__main__':
    c = camera('1.1.1.1')
    c.sendCommand('test')