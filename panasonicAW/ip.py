import requests
import time

class camera:
    def __init__(self, address):
        self.version = "1.0.1"
        self.speedTable = self.__genSpeedTable()
        self.address = address
        self.time_of_last_command = 0
        self.__command_prefix = '%23'

        self.__power_states = [ 0, 1, 'f', 'n']
        self.rangelimitHex = {"pan":(0x2D09, 0xD2f5), "tilt": (0x5555, 0x8E38) }

    def __genSpeedTable(self):
        speedTable = {}
        for x in range(30):
            speedTable[x] = (str(hex(x))[2:].zfill(2), "0")
        for x in range(30):
            speedTable[x+30] = (str(hex(x))[2:].zfill(2), "2")
        return speedTable

    def __timeMillis(self):
        milliseconds = int(round(time.time() * 1000))
        return milliseconds


    def __handleCamError(self, responce):
        print("ERROR: Camera head reported an error.")
        print(responce.text)
        return 1

    def __sendCommand(self, command):
        #sends command to camera

        #fist check if command is being set to close to another
        current_time = self.__timeMillis()
        time_dif = current_time - self.time_of_last_command
        if self.time_of_last_command == 0:
            pass
        else:
            if time_dif < 130 :
                # print("ERROR: Command sent to fast. Please wait at least 130ms between commands.")
                raise TimeoutError("ERROR: Command sent to fast. Please wait at least 130ms between commands.")
        #if enough time has elapsed then parse and send command
        #parse command
        command_to_send = 'http://' + self.address + '/cgi-bin/aw_ptz?cmd=' + command +"&res=1"
        # print(command_to_send)
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

    def __hexToInt(self, value): #converts hexvalut
        if type(vaule) != int:
            vaule = int(value, 16)
        
        return value

    #def __rangeChceckHex(self, value):
        #if 

    def __presetCheckPadding(self, preset):
        preset = str(preset)
        if len(preset) == 1:
            preset = "0" + preset
        
        return preset
        

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
            raise("ERROR: Error retriving power status.")
    
    def setPower(self, state):
        if state not in self.__power_states:
            raise ValueError("ERROR: Invalid state requested")
        else:
            resp = self.__sendCommand(self.__command_prefix + "O" + str(state))

    def setPosABS(self, x, y):
        resp = self.__sendCommand(self.__command_prefix + "APC" + str(x).upper() + str(y).upper())
        return resp
    
    def setPosABSSpeed(self, x, y, speed):
        resp = self.__sendCommand(self.__command_prefix + "APS" + str(x).upper() + str(y).upper() + str(self.speedTable[speed][0]).upper() + str(self.speedTable[speed][1]).upper())
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
    
    def setZoomABS(self, zoom):
        resp = self.__sendCommand(self.__command_prefix + "AXZ" + str(zoom).upper())

    def moveStop(self):
        return self.setPanTileSpeed('50', '50')

    def presetPlay(self, preset):
        preset = self.__presetCheckPadding(preset)
        resp = self.__sendCommand(self.__command_prefix + "R" + str(preset))
        return resp
    
    def presetRegister(self, preset):
        preset = self.__presetCheckPadding(preset)
        resp = self.__sendCommand(self.__command_prefix + "M" + str(preset))
        return resp

    def presetDelete(self, preset):
        preset = self.__presetCheckPadding(preset)
        resp = self.__sendCommand(self.__command_prefix + "C" + str(preset))
        return resp

    def presetQuery(self):
        resp = self.__sendCommand(self.__command_prefix + "S")
        preset = int(resp.text[1:]) #strip data prefix and convert from string to int
        return preset

    def presetSpeedSet(self, speed):
        resp = self.__sendCommand(self.__command_prefix + "UPVS" + str(speed))
        return resp

    def presetSpeedquery(self):
        resp = self.__sendCommand(self.__command_prefix + "UPVS")
        speed = int(resp.text[4:]) #strip data prefix and convert from string to int
        return speed

    def queryPosition(self):
        resp = self.__sendCommand(self.__command_prefix + "APC")
        RAW_pan = resp.text[3:-4]
        RAW_tilt = resp.text[7:]
        pan = self.__intToHex(RAW_pan)
        tilt = self.__intToHex(RAW_tilt)

        pos = (pan, tilt)

        return pos

    def queryZoom(self):
        resp = self.__sendCommand(self.__command_prefix + "GZ")
        return resp.text[2:]

    def testith(self, value):
        a = self.__intToHex(value)
        print(a)

        
        



if __name__ == '__main__':

    cam_address = "192.168.1.150"

    c = camera(cam_address)
    #print(c.setPosABS(8000, 8000))
    #time.sleep(0.14)
    c.queryPosition()
    time.sleep(0.14)