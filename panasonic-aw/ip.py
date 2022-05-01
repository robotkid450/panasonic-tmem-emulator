import requests
import time

class camera:
    def __init__(self, address):
        self.address = address
        self.time_of_last_command = 0

    def __timeMillis(self):
        milliseconds = int(round(time.time() * 1000))
        return milliseconds


    def __handleCamError(self, responce):
        if devEnv == True:
            return 0
        print("ERROR: Camera head reported an error.")
        print(responce.text)
        return 1

    def __sendCommand(self, command):
        current_time = self.__timeMillis()
        time_dif = current_time - self.time_of_last_command
        print("last commad: %s" % self.time_of_last_command)
        print("current command: %s" % current_time)
        print("time Difference: %s" % time_dif)
        
        if self.time_of_last_command == 0:
            pass
        else:

            if time_dif < 130 :
                print("ERROR: Command sent to fast. Please wait at least 130ms between commands.")
                return -2
        command_to_send = 'http://' + self.address + '/cgi-bin/aw_ptz?cmd=' + command +"&res=1"
        print(command_to_send)
        response = requests.get(command_to_send)
        self.time_of_last_command = current_time
        if response != 200:
            err = self.__handleCamError(response)
            return err
        else:
            return 0 

    def sendRaw(self, command):
        err = self.__sendCommand(command)
        if err != 0:
            print(err)

    #def


if __name__ == '__main__':

    devEnv=True

    if devEnv == True:
        cam_address = "localhost:8000"
    else:
        cam_address = "192.168.0.10"

    c = camera(cam_address)
    c.sendRaw('test')
    c.sendRaw('a')