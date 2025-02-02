import requests
import time
import logging
from panasonicAW import cameraModels
from panasonicAW import CameraExceptions



__version__ = "1.0.5"



# logging.basicConfig(level=logging.DEBUG)


class Camera:

    def __init__(self, address, model ="default", protocol = "http"):
        self.logger = logging.getLogger(__name__)
        self.cam_config = cameraModels.CAMERA_MODELS[model]
        self.speed_table = self.__gen_speed_table()
        self.address = address
        self.time_of_last_command = 0
        self.update_speed = 0.3
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

    def __gen_speed_table(self):
        self.logger.debug("Generating speed table")
        speed_table = {}
        for x in range(0, 30):
            speed_table[x] = (str(hex(x))[2:].zfill(2), "0")
        for x in range(31):
            speed_table[x+30] = str(hex(x))[2:].zfill(2), "1"
        for x in range(30):
            speed_table[x+60] = (str(hex(x))[2:].zfill(2), "2")
        self.logger.debug("Speed table generated")
        self.logger.debug(speed_table)
        return speed_table
    @staticmethod
    def _time_millis():
        milliseconds = int(round(time.time() * 1000))
        return milliseconds

    def __handle_cam_error(self, response):
        camera_response_text = response.text
        error_code = camera_response_text[0:3]
        error_message = camera_response_text[4:]
        if error_code == "eR1":
            self.logger.error("Camera Error: %s, %s", error_code, error_message)
            raise CameraExceptions.CameraCommandUnsupportedException(error_message)
        if error_code == "eR2":
            self.logger.error("Camera Error: %s, %s", error_code, error_message)
            raise CameraExceptions.CameraBusyException(error_message)
        if error_code == "eR3":
            self.logger.error("Camera Error: %s, %s", error_code, error_message)
            raise CameraExceptions.CameraOutSideSupportedRangeException(error_message)
        return response

    def __send_command(self, command):
        #sends command to camera

        #fist check if command is being set to close to another
        current_time = self._time_millis()
        time_dif = current_time - self.time_of_last_command
        if self.time_of_last_command == 0:
            pass
        else:
            if time_dif < 130 :
                raise TimeoutError("ERROR: Command sent to fast. Please wait at least 130ms between commands.")
        #if enough time has elapsed then parse and send command
        #parse command
        # command_to_send = 'http://' + self.address + '/cgi-bin/aw_ptz?cmd=' + command +"&res=1"
        command_to_send = self.__command_string.format(cmd=command)
        #send command to camera
        response = requests.get(command_to_send)
        #update timestamp for last command
        self.time_of_last_command = current_time
        self.logger.debug(command_to_send)
        self.__handle_cam_error(response)
        return response

    def int_to_hex(self, value, pad=4):
        self.logger.debug("Converting %s to hex", value)
        # self.logger.debug(type(value))
        if type(value) == str:
            value = int(value)

        value = hex(value)

        value = str(value)        

        value_pad = value[2:].zfill(pad)
        # self.logger.debug(value_pad)
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
        self.logger.debug("Sending command: %s to %s", command, self.address)
        response= self.__send_command(command)
        return response

    def power_set(self, state):
        self.logger.info("Setting power state: %s to %s", state, self.address)
        if state not in self.__power_states:
            raise ValueError("ERROR: Invalid power state requested")
        else:
            resp = self.__send_command("O" + str(state))
            return resp

    def power_query(self):
        self.logger.info("Power query")
        resp = self.__send_command("O")
        self.logger.info("power value : {0}".format(resp.text))
        if resp.text == 'p1':
            return 1
        elif resp.text == 'p3':
            return 3
        elif resp.text == 'p0':
            return 0
        else:
            raise ValueError("ERROR: Error retrieving power status.")

    def position_set_absolute(self, x : int, y : int):
        self.logger.info("Setting absolute position for %s to %s:%s", self.address, x, y)
        self.check_tuning()
        # x = self.int_to_head(x,self.pan_min, self.pan_max, self.pan_min_head, self.pan_max_head,4)
        # y = self.int_to_head(y, self.tilt_min, self.tilt_max, self.tilt_min_head, self.tilt_max_head,4)
        x = self.int_to_hex(x)
        y = self.int_to_hex(y)

        resp = self.__send_command("APC" + x.upper() + y.upper())

        return resp

    def position_set_absolute_hex(self, x : str, y : str):
        self.logger.info("Setting absolute position hex for %s to %s:%s", self.address, x, y)
        resp = self.__send_command("APC" + str(x).upper() + str(y).upper())
        return resp

    def position_set_absolute_with_speed(self, x : int, y : int, speed : int):
        self.logger.info("Setting absolute position with speed for %s to %s:%s with speed %s",
                     self.address, x, y, speed)
        self.check_tuning()
        # x = self.int_to_head(x, self.pan_min, self.pan_max, self.pan_min_head, self.pan_max_head, 4)
        # y = self.int_to_head(y, self.tilt_min, self.tilt_max, self.tilt_min_head, self.tilt_max_head, 4)

        x = self.int_to_hex(x)
        y = self.int_to_hex(y)

        if speed not in self.speed_table:
            raise ValueError("ERROR: Invalid speed requested")
        resp = self.__send_command("APS" + x.upper() + y.upper()
            + str(self.speed_table[speed][0]).upper() + str(self.speed_table[speed][1]).upper())

        return resp

    def position_set_absolute_with_speed_hex(self, x : str, y : str, speed : int):
        self.logger.info("Setting absolute position with speed hex for %s to %s:%s with speed %s",
                     self.address, x, y, speed)
        resp = self.__send_command("APS" + str(x).upper() + str(y).upper()
            + str(self.speed_table[speed][0]).upper() + str(self.speed_table[speed][1]).upper())

        return resp

    def pan_set_speed(self, speed : int):
        self.logger.info("Setting pan speed for %s to %s", self.address, speed)
        self.range_check(speed, self.pan_speed_bounds[0], self.pan_speed_bounds[1])
        speed = str(speed).zfill(2)
        resp = self.__send_command("P" + speed)
        return resp
    
    def tilt_set_speed(self, speed : int):
        self.logger.info("Setting tilt speed for %s to %s", self.address, speed)
        self.range_check(speed, self.tilt_speed_bounds[0], self.tilt_speed_bounds[1])
        speed = str(speed).zfill(2)
        resp = self.__send_command("T" + speed)
        return resp
    
    def pan_tilt_set_speed(self, pan_speed: int, tilt_speed : int):
        self.logger.info("Setting pan tilt speed for %s to %s:%s", self.address, pan_speed, tilt_speed)
        self.range_check(pan_speed, self.pan_speed_bounds[0], self.pan_speed_bounds[1])
        self.range_check(tilt_speed, self.tilt_speed_bounds[0], self.tilt_speed_bounds[1])
        pan_speed = str(pan_speed).zfill(2)
        tilt_speed = str(pan_speed).zfill(2)
        resp = self.__send_command("PTS" + pan_speed + tilt_speed)
        return resp

    def pan_tilt_stop(self):
        self.logger.info("Stopping pan tilt for %s", self.address)
        return self.pan_tilt_set_speed(50, 50)

    def position_query_hex(self):
        self.logger.info("Querying hex position")
        resp = self.__send_command("APC")
        raw_pan = resp.text[3:-4]
        raw_tilt = resp.text[7:]
        pos = (raw_pan.upper(), raw_tilt.upper())
        self.logger.info("Hex position: %s", pos)
        return pos

    def position_query(self):
        self.logger.info("Querying position")
        resp = self.__send_command("APC")
        raw_pan = resp.text[3:-4]
        raw_tilt = resp.text[7:]
        pan = self.hex_to_int(raw_pan)
        tilt = self.hex_to_int(raw_tilt)
        pos = (pan, tilt)
        self.logger.info("Position: %s", pos)
        return pos

    def zoom_set_absolute (self, zoom : int):
        self.logger.info("Setting absolute zoom for %s to %s", self.address, zoom)
        zoom = self.int_to_head(zoom, self.zoom_min, self.zoom_max, self.zoom_min_head, self.zoom_max_head,3)
        resp = self.__send_command("AXZ" + zoom.upper())
        return resp

    def zoom_set_absolute_hex (self, zoom : str):
        self.logger.info("Setting absolute zoom hex for %s to %s", self.address, zoom)
        resp = self.__send_command("AXZ" + str(zoom).upper())
        return resp

    def zoom_speed(self, speed :int ):
        self.logger.info("Setting zoom speed for %s to %s", self.address, speed)
        self.range_check(speed, 1, 99)
        speed = str(speed).zfill(2).upper()
        resp = self.__send_command("Z" + speed)
        return resp

    def zoom_stop(self):
        self.logger.info("Stopping zoom for %s", self.address)
        resp = self.zoom_speed(50)
        return resp

    def zoom_query_hex(self):
        self.logger.info("Querying hex zoom for %s", self.address)
        resp = self.__send_command("GZ")
        zoom = resp.text[2:]
        self.logger.info("Hex zoom: %s for %s", zoom, self.address)
        return zoom

    def zoom_query(self):
        self.logger.info("Querying zoom for %s", self.address)
        resp = self.__send_command("GZ")
        zoom = resp.text[2:]
        zoom = self.hex_to_int(zoom)
        zoom = self.range_conversion(zoom, self.zoom_min_head, self.zoom_max_head, self.zoom_min, self.zoom_max)
        self.logger.info("Zoom: %s for %s", zoom, self.address)
        return zoom

    def preset_play(self, preset : int):
        self.logger.info("Playing  preset %s from %s", preset, self.address)
        preset = self.__preset_check_padding(preset)
        resp = self.__send_command("R" + str(preset))
        return resp
    
    def preset_register(self, preset: int):
        self.logger.info("registering  preset %s from %s", preset, self.address)
        preset = self.__preset_check_padding(preset)
        resp = self.__send_command("M" + str(preset))
        return resp

    def preset_delete(self, preset : int):
        self.logger.info("deleting preset %s from %s", preset, self.address)
        preset = self.__preset_check_padding(preset)
        resp = self.__send_command("C" + str(preset))
        return resp

    def preset_query(self):
        self.logger.info("querying preset for %s", self.address)
        resp = self.__send_command("S")
        preset = int(resp.text[1:]) #strip data prefix and convert from string to int
        self.logger.info("Preset: %s for %s", preset, self.address)
        return preset

    def preset_speed_set(self, speed):
        self.logger.info("Setting preset recall speed for %s to %s", self.address, speed)
        resp = self.__send_command("UPVS" + str(speed))
        return resp

    def preset_speed_query(self):
        self.logger.info("querying preset recall speed for %s", self.address)
        resp = self.__send_command("UPVS")
        speed = int(resp.text[4:]) #strip data prefix and convert from string to int
        return speed






if __name__ == "__main__":
    pass

    