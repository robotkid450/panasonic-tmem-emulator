import requests
import time

class camera:
    def __init__(self, address):
        self.address = address
        self.time_of_last_command = 0
        self.__command_prefix = '%23'

        self.__power_states = [ 0, 1, 'f', 'n']

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
        #sends command to camera

        #fist check if command is being set to clost to another
        current_time = self.__timeMillis()
        time_dif = current_time - self.time_of_last_command
        if self.time_of_last_command == 0:
            pass
        else:
            if time_dif < 130 :
                print("ERROR: Command sent to fast. Please wait at least 130ms between commands.")
                return -2
        #if enough time has elapsed then parse and send command
        #parse command
        command_to_send = 'http://' + self.address + '/cgi-bin/aw_ptz?cmd=' + command +"&res=1"
        print(command_to_send)
        #send command to camera
        response = requests.get(command_to_send)
        #update timestamp for last command
        self.time_of_last_command = current_time
        return response

    def __intToHex(self, value, pad=4):

        if type(value) == str:
            value = int(value, 16)

        value = hex(value)

        value = str(value)        

        value_pad = value[2:].zfill(4)
        return value_pad
        

    def sendRaw(self, command):
        err = self.__sendCommand(command)
        if err != 0:
            print(err)

    def queryPower(self):
        resp = self.__sendCommand(self.__command_prefix + "O")
        print(resp)
        if resp.text == 'p1':
            return 1
        elif resp.text == 'p3':
            return 3
        elif resp.text == 'p0':
            return 0
        else:
            print("ERROR: Error retriving power status.")
            return -1
    
    def setPower(self, state):
        if state not in self.__power_states:
            print("ERROR: Invalid state requested")
            return -1
        else:
            resp = self.__sendCommand(self.__command_prefix + "O" + str(state))

    def setPosABS(self, x, y):
        resp = self.__sendCommand(self.__command_prefix + "APC" + str(x) + str(y))
        return resp

    def setPanSpeed(self, speed):
        resp = self.__sendCommand(self.__command_prefix + "P" + str(speed))
        return resp
    
    def setTiltSpeed(self, speed):
        resp = self.__sendCommand(self.__command_prefix + "T" + str(speed))
        return resp
    
    def setPanTileSpeed(self, pan_speed, tilt_speed):
        resp = self.__sendCommand(self.__command_prefix + "PTS" + str(pan_speed) + str(tilt_speed))
        return resp

    def moveStop(self):
        return self.setPanTileSpeed('50', '50')

    def presetPlay(self, preset):
        pass

    def queryPosition(self):
        resp = self.__sendCommand(self.__command_prefix + "APC")
        print(resp)
        print(resp.text)
        RAW_pan = resp.text[3:-4]
        RAW_tilt = resp.text[7:]
        pan = self.__intToHex(RAW_pan)
        tilt = self.__intToHex(RAW_tilt)

        pos = (pan, tilt)

        return pos


    def testith(self, value):
        a = self.__intToHex(value)
        print(a)

        
        



if __name__ == '__main__':

    devEnv=False

    if devEnv == True:
        cam_address = "localhost:8000"
    else:
        cam_address = "192.168.0.10"

    c = camera(cam_address)
    #print(c.setPosABS(8000, 8000))
    #time.sleep(0.14)
    c.queryPosition()
    time.sleep(0.14)