import logging
import multiprocessing
from panasonicAW import ProcessHeadWorker
from panasonicAW import ipcBase
# from panasonicAW import ptzHead
class Driver:
    def __init__(self, address, model = 'default', protocol='http'):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.logger.info("Initializing ProcessHeadDriver")
        self.cmd_queue = multiprocessing.Queue()
        self.resp_queue = multiprocessing.Queue()
        self.address = address
        self.model = model
        self.protocol = protocol
        head_process = multiprocessing.Process(target=ProcessHeadWorker.Worker,
            args=(self.cmd_queue, self.resp_queue, self.address, self.model, self.protocol), daemon=True)

        head_process.start()
        self.logger.info("ThreadedHeadDriver initialized for {addr}".format(addr=self.address))

    def _wait_for_response(self):
        while self.resp_queue.qsize() == 0:
            pass

        ipc_resp = self.resp_queue.get()
        self.logger.info("Received response: {r} with data: {d}".format(r=ipc_resp.response, d=ipc_resp.data))
        resp_obj = (ipc_resp.response, ipc_resp.data)
        return resp_obj

    def _create_and_send_command(self, command : str, data : dict = None):
        ipc_m = self.create_cmd(command,  data)
        self.cmd_queue.put(ipc_m)
        return self._wait_for_response()

    @staticmethod
    def create_cmd(command:str, data:dict = None):
        return ipcBase.IPCCmd(command=command, data=data)


    def ping(self):
        self.logger.info("Sending ping")
        return self._create_and_send_command("ping")

    def stop(self):
        self.logger.info("Sending stop")
        return self._create_and_send_command("stop_main_loop")

    # def send_raw(self, data):
    #     self.logger.info("Sending raw: {}".format(data))
    #     return self._create_and_send_command("raw", data)

    def power_set(self, state: int):
        self.logger.info("Setting power state to {}".format(state))
        return self._create_and_send_command("power_set", {"state": state})

    def power_query(self):
        self.logger.info("Querying power state")
        return self._create_and_send_command("power_query")

    def position_set_absolute(self, pos_x, pos_y):
        self.logger.info("Setting absolute position to x: {x}, y: {y}".format(x=pos_x, y=pos_y))
        data_to_send = {"x": pos_x, "y": pos_y}
        return self._create_and_send_command("position_set_abs", data_to_send)

    def position_set_absolute_hex(self, x: str, y: str):
        self.logger.info("Setting absolute position to hex: {x}, {y}".format(x=x, y=y))
        data_to_send = {"x": x, "y": y}
        return self._create_and_send_command("position_set_absolute_hex", data_to_send)

    def position_set_absolute_with_speed(self, x: int, y: int, speed: int):
        self.logger.info(
            "Setting absolute position to x: {x}, y: {y} with speed {s}".format(x=x, y=y, s=speed))
        data_to_send = {"x": x, "y": y, "speed": speed}
        return self._create_and_send_command("position_set_absolute_with_speed", data_to_send)

    def position_set_absolute_with_speed_hex(self, x: str, y: str, speed: int):
        self.logger.info(
            "Setting absolute position to x: {x}, y: {y} with speed {s}".format(x=x, y=y, s=speed))
        data_to_send = {"x": x, "y": y, "speed": speed}
        return self._create_and_send_command("position_set_absolute_with_speed_hex", data_to_send)

    def pan_set_speed(self, speed: int):
        self.logger.info("Setting pan speed to {s}".format(s=speed))
        data_to_send = {"pan_speed" : speed, "tilt_speed" : None}
        return self._create_and_send_command("pan_tilt_set_speed", data_to_send)

    def tilt_set_speed(self, speed: int):
        self.logger.info("Setting tilt speed to {s}".format(s=speed))
        data_to_send = {"pan_speed" : None, "tilt_speed" : speed}
        return self._create_and_send_command("pan_tilt_set_speed", data_to_send)

    def pan_tilt_set_speed(self, pan_speed: int, tilt_speed: int):
        self.logger.info("Setting pan:tilt speed to {}:{}".format(pan_speed, tilt_speed))
        data_to_send = {"pan_speed" : pan_speed, "tilt_speed" : tilt_speed}
        return self._create_and_send_command("pan_tilt_set_speed", data_to_send)

    def pan_tilt_stop(self):
        self.logger.info("Stopping pan tilt")
        data_to_send = {"pan_speed": 50, "tilt_speed": 50}
        return self._create_and_send_command("pan_tilt_set_speed", data_to_send)

    def position_query(self):
        self.logger.info("Querying position")
        return self._create_and_send_command("position_query")
        pass

    def zoom_set_absolute(self, zoom: int):
        pass

    def zoom_set_absolute_hex(self, zoom: str):
        pass

    def zoom_speed(self, speed: int):
        pass

    def zoom_stop(self):
        pass

    def zoom_query_hex(self):
        pass

    def zoom_query(self):
        pass

    def preset_play(self, preset: int):
        pass

    def preset_register(self, preset: int):
        pass

    def preset_delete(self, preset: int):
        pass

    def preset_query(self):
        pass

    def preset_speed_set(self, speed):
        pass

    def preset_speed_query(self):
        pass

if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    # driver_logger = logging.getLogger(__name__+"driver")
    logging.basicConfig(level=logging.DEBUG)
    d = Driver(address='192.168.1.150', model='AW-HE40', protocol='http')