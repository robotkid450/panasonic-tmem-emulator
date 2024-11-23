import requests
import time
from panasonicAW import cameraModels
__version__ = "1.0.1"

class Camera:

    def __init__(self, address, model ="default", protocol = "http"):
        self.cam_config = cameraModels.CAMERA_MODELS[model]
        self.speed_table = self.__gen_speed_table()
        self.address = address
        self.time_of_last_command = 0
        self.__command_prefix = '%23'

        self.__command_string = "{protocol}://{address}/cgi-bin/aw_ptz?cmd=%23{cmd}&res=1".format(protocol=protocol, address=self.address, cmd="{cmd}")

        self.__power_states = [ 0, 1, 'f', 'n']
        self.pan_min, self.pan_max = self.cam_config["pan"]['angles']

        self.pan_speed_bounds = self.cam_config["pan"]['speed_bounds']
        self.pan_speed_max = self.cam_config["pan"]['speed_max']
        self.tilt_min, self.tilt_max = self.cam_config["tilt"]['angles']
        self.tilt_speed_bounds = self.cam_config["tilt"]['speed_bounds']
        self.command_delay = self.cam_config["command_delay"]
        self.zoom_min_head = self.cam_config["zoom"]["position_bounds"][0]
        self.zoom_max_head = self.cam_config["zoom"]["position_bounds"][1]
        self.zoom_min = 0
        self.zoom_max = 2800
        try:
            self.pan_min_head, self.pan_max_head = self.cam_config["pan"]['angles_head']
            self.tilt_min_head, self.tilt_max_head = self.cam_config["tilt"]['angles_head']
            self.tuning = True
        except KeyError:
            self.tuning = False

    @staticmethod
    def __gen_speed_table():
        speed_able = {}
        for x in range(1, 31):
            speed_able[x] = (str(hex(x))[2:].zfill(2), "0")
        for x in range(31):
            speed_able[x+30] = str(hex(x))[2:].zfill(2), "1"
        for x in range(31):
            speed_able[x+60] = (str(hex(x))[2:].zfill(2), "2")
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
        # command_to_send = 'http://' + self.address + '/cgi-bin/aw_ptz?cmd=' + command +"&res=1"
        command_to_send = self.__command_string.format(cmd=command)
        #send command to camera
        response = requests.get(command_to_send)
        #update timestamp for last command
        self.time_of_last_command = current_time
        return response

    @staticmethod
    def int_to_hex(value, pad=4):
        if type(value) == str:
            value = int(value, 16)

        value = hex(value)

        value = str(value)        

        value_pad = value[2:].zfill(pad)
        return value_pad

    @staticmethod
    def hex_to_int(value): #converts hex to int
        if type(value) != int:
            value = int(value, 16)
        
        return value
    @staticmethod
    def range_conversion(num, in_min, in_max, out_min, out_max):
        output_number = out_min + (num - in_min) / (in_max - in_min) * (out_max - out_min)
        return int(output_number)

    @staticmethod
    def range_check(value, minimum, maximum):
        if value < minimum or value > maximum:
            raise ValueError("Range out of range")

    def int_to_head(self, value : int, human_minimum : int,
                    human_maximum : int, head_minimum : int, head_maximum : int, padding : int):
        self.range_check(value, human_minimum,human_maximum)
        result = self.range_conversion(value, human_minimum, human_maximum, head_minimum, head_maximum)
        result = self.int_to_hex(result, padding)
        return result

    def check_tuning(self):
        if not self.tuning:
            raise ValueError("ERROR: Selected model has not been tuned.")

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
            resp = self.__send_command("O" + str(state))
            return resp

    def power_query(self):
        resp = self.__send_command("O")
        print(resp)
        if resp.text == 'p1':
            return 1
        elif resp.text == 'p3':
            return 3
        elif resp.text == 'p0':
            return 0
        else:
            print(resp.text)
            # raise "ERROR: Error retrieving power status."

    def position_set_absolute(self, x : int, y : int):
        self.check_tuning()
        x = self.int_to_head(x,self.pan_min, self.pan_max, self.pan_min_head, self.pan_max_head,4)
        y = self.int_to_head(y, self.tilt_min, self.tilt_max, self.tilt_min_head, self.tilt_max_head,4)

        resp = self.__send_command("APC" + x.upper() + y.upper())

        return resp

    def position_set_absolute_hex(self, x : str, y : str):
        resp = self.__send_command("APC" + str(x).upper() + str(y).upper())
        return resp

    def position_set_absolute_with_speed(self, x : int, y : int, speed : int):
        self.check_tuning()
        x = self.int_to_head(x, self.pan_min, self.pan_max, self.pan_min_head, self.pan_max_head, 4)
        y = self.int_to_head(y, self.tilt_min, self.tilt_max, self.tilt_min_head, self.tilt_max_head, 4)

        if speed not in self.speed_table:
            raise ValueError("ERROR: Invalid speed requested")
        resp = self.__send_command("APS" + x.upper() + y.upper()
            + str(self.speed_table[speed][0]).upper() + str(self.speed_table[speed][1]).upper())

        return resp

    def position_set_absolute_with_speed_hex(self, x : str, y : str, speed : int):
        resp = self.__send_command("APS" + str(x).upper() + str(y).upper()
            + str(self.speed_table[speed][0]).upper() + str(self.speed_table[speed][1]).upper())

        return resp

    def pan_set_speed(self, speed : int):
        self.range_check(speed, self.pan_speed_bounds[0], self.pan_speed_bounds[1])
        speed = str(speed).zfill(2)
        resp = self.__send_command("P" + speed)
        return resp
    
    def tilt_set_speed(self, speed : int):
        self.range_check(speed, self.tilt_speed_bounds[0], self.tilt_speed_bounds[1])
        speed = str(speed).zfill(2)
        resp = self.__send_command("T" + speed)
        return resp
    
    def pan_tilt_set_speed(self, pan_speed: int, tilt_speed : int):
        self.range_check(pan_speed, self.pan_speed_bounds[0], self.pan_speed_bounds[1])
        self.range_check(tilt_speed, self.tilt_speed_bounds[0], self.tilt_speed_bounds[1])
        pan_speed = str(pan_speed).zfill(2)
        tilt_speed = str(pan_speed).zfill(2)
        resp = self.__send_command("PTS" + pan_speed + tilt_speed)
        return resp

    def pan_tilt_stop(self):
        return self.pan_tilt_set_speed(50, 50)

    def position_query_hex(self):
        resp = self.__send_command("APC")
        raw_pan = resp.text[3:-4]
        raw_tilt = resp.text[7:]
        pos = (raw_pan.upper(), raw_tilt.upper())
        return pos

    def position_query(self):
        resp = self.__send_command("APC")
        raw_pan = resp.text[3:-4]
        raw_tilt = resp.text[7:]
        pan = self.hex_to_int(raw_pan)
        pan = self.range_conversion(pan, self.pan_min_head, self.pan_max_head, self.pan_min, self.pan_max)
        tilt = self.hex_to_int(raw_tilt)
        tilt = self.range_conversion(tilt, self.tilt_min_head, self.tilt_max_head, self.tilt_min, self.tilt_max)
        pos = (pan, tilt)
        return pos

    def zoom_set_absolute (self, zoom : int):
        zoom = self.int_to_head(zoom, self.zoom_min, self.zoom_max, self.zoom_min_head, self.zoom_max_head,3)
        print(zoom)
        resp = self.__send_command("AXZ" + zoom.upper())
        return resp

    def zoom_set_absolute_hex (self, zoom : int):
        resp = self.__send_command("AXZ" + str(zoom).upper())
        return resp

    def zoom_speed(self, speed :int ):
        self.range_check(speed, 1, 99)
        speed = str(speed).zfill(2).upper()
        resp = self.__send_command("Z" + speed)
        return resp

    def zoom_stop(self):
        resp = self.zoom_speed(50)
        return resp

    def zoom_query_hex(self):
        resp = self.__send_command("GZ")
        return resp.text[2:]

    def zoom_query(self):
        resp = self.__send_command("GZ")
        zoom = resp.text[2:]
        zoom = self.hex_to_int(zoom)
        zoom = self.range_conversion(zoom, self.zoom_min_head, self.zoom_max_head, self.zoom_min, self.zoom_max)
        return zoom

    def preset_play(self, preset : int):
        preset = self.__preset_check_padding(preset)
        resp = self.__send_command("R" + str(preset))
        return resp
    
    def preset_register(self, preset: int):
        preset = self.__preset_check_padding(preset)
        resp = self.__send_command("M" + str(preset))
        return resp

    def preset_delete(self, preset : int):
        preset = self.__preset_check_padding(preset)
        resp = self.__send_command("C" + str(preset))
        return resp

    def preset_query(self):
        resp = self.__send_command("S")
        preset = int(resp.text[1:]) #strip data prefix and convert from string to int
        return preset

    def preset_speed_set(self, speed):
        resp = self.__send_command("UPVS" + str(speed))
        return resp

    def preset_speed_query(self):
        resp = self.__send_command("UPVS")
        speed = int(resp.text[4:]) #strip data prefix and convert from string to int
        return speed
