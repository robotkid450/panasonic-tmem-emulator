import requests
import time

__version__ = "1.0.1"

class Camera:


    def __init__(self, address):
        self.speed_table = self.__gen_speed_table()
        self.address = address
        self.time_of_last_command = 0
        self.__command_prefix = '%23'

        self.__power_states = [ 0, 1, 'f', 'n']
        self.range_limit_hex = {"pan":(0x2D09, 0xD2f5), "tilt": (0x5555, 0x8E38) }

    @staticmethod
    def __gen_speed_table():
        speed_able = {}
        for x in range(30):
            speed_able[x] = (str(hex(x))[2:].zfill(2), "0")
        for x in range(30):
            speed_able[x+30] = (str(hex(x))[2:].zfill(2), "2")
        return speed_able
    @staticmethod
    def __time_millis():
        milliseconds = int(round(time.time() * 1000))
        return milliseconds

    @NotImplementedError
    def __handle_cam_error(self, response):
        print("ERROR: Camera head reported an error.")
        print(response.text)
        return 1

    def __send_command(self, command):
        #sends command to camera

        #fist check if command is being set to close to another
        current_time = self.__time_millis()
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

    @staticmethod
    def __int_to_hex(value, pad=4):
        if type(value) == str:
            value = int(value, 16)

        value = hex(value)

        value = str(value)        

        value_pad = value[2:].zfill(4)
        return value_pad

    @staticmethod
    def __hex_to_int(value): #converts hex to int
        if type(value) != int:
            value = int(value, 16)
        
        return value

    #def __range_check_hex(self, value):
        #if 

    @staticmethod
    def __preset_check_padding( preset):
        preset = str(preset)
        if len(preset) == 1:
            preset = "0" + preset
        
        return preset

    def send_raw(self, command):
        err = self.__send_command(command)
        if err != 0:
            print(err)


    def power_set(self, state):
        if state not in self.__power_states:
            raise ValueError("ERROR: Invalid state requested")
        else:
            resp = self.__send_command(self.__command_prefix + "O" + str(state))

    def position_set_absolute(self, x, y):
        resp = self.__send_command(self.__command_prefix + "APC" + str(x).upper() + str(y).upper())
        return resp
    
    def position_set_absolute_with_speed(self, x, y, speed):
        resp = self.__send_command(self.__command_prefix + "APS" + str(x).upper() + str(y).upper() + str(self.speed_table[speed][0]).upper() + str(self.speed_table[speed][1]).upper())
        return resp

    def pan_set_speed(self, speed):
        resp = self.__send_command(self.__command_prefix + "P" + str(speed))
        return resp
    
    def tilt_set_speed(self, speed):
        resp = self.__send_command(self.__command_prefix + "T" + str(speed))
        return resp
    
    def pan_tilt_set_speed(self, pan_speed, tilt_speed):
        resp = self.__send_command(self.__command_prefix + "PTS" + str(pan_speed) + str(tilt_speed))
        return resp
    
    def zoom_set_absolute (self, zoom):
        resp = self.__send_command(self.__command_prefix + "AXZ" + str(zoom).upper())


    def pan_tilt_stop(self):
        return self.pan_tilt_set_speed('50', '50')


    def preset_play(self, preset):
        preset = self.__preset_check_padding(preset)
        resp = self.__send_command(self.__command_prefix + "R" + str(preset))
        return resp
    
    def preset_register(self, preset):
        preset = self.__preset_check_padding(preset)
        resp = self.__send_command(self.__command_prefix + "M" + str(preset))
        return resp

    def preset_delete(self, preset):
        preset = self.__preset_check_padding(preset)
        resp = self.__send_command(self.__command_prefix + "C" + str(preset))
        return resp

    def preset_query(self):
        resp = self.__send_command(self.__command_prefix + "S")
        preset = int(resp.text[1:]) #strip data prefix and convert from string to int
        return preset

    def preset_speed_set(self, speed):
        resp = self.__send_command(self.__command_prefix + "UPVS" + str(speed))
        return resp

    def preset_speed_query(self):
        resp = self.__send_command(self.__command_prefix + "UPVS")
        speed = int(resp.text[4:]) #strip data prefix and convert from string to int
        return speed


    def power_query(self):
        resp = self.__send_command(self.__command_prefix + "O")
        print(resp)
        if resp.text == 'p1':
            return 1
        elif resp.text == 'p3':
            return 3
        elif resp.text == 'p0':
            return 0
        else:
            raise "ERROR: Error retrieving power status."

    def position_query(self):
        resp = self.__send_command(self.__command_prefix + "APC")
        raw_pan = resp.text[3:-4]
        raw_tilt = resp.text[7:]
        pan = self.__int_to_hex(raw_pan)
        tilt = self.__int_to_hex(raw_tilt)
        pos = (pan, tilt)
        return pos

    def zoom_query(self):
        resp = self.__send_command(self.__command_prefix + "GZ")
        return resp.text[2:]


    def test_int_to_hex(self, value):
        a = self.__int_to_hex(value)
        print(a)


if __name__ == '__main__':

    cam_address = "192.168.1.150"

    c = Camera(cam_address)
    #print(c.setPosABS(8000, 8000))
    #time.sleep(0.14)
    c.position_query()
    time.sleep(0.14)