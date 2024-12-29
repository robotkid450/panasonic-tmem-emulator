import logging
import multiprocessing
from panasonicAW import ProcessHeadWorker
from panasonicAW import ipcBase
class ProcessHeadDriver:
    def __init__(self, address, model = 'default', protocol='http'):
        self.logger = logging.getLogger(__name__ + "ProcessHeadDriver")
        self.logger.info("Initializing ProcessHeadDriver")
        self.cmd_queue = multiprocessing.Queue()
        self.resp_queue = multiprocessing.Queue()
        self.address = address
        self.model = model
        self.protocol = protocol
        head_process = multiprocessing.Process(target=ProcessHeadWorker.ProcessHeadWorker,
            args=(self.cmd_queue, self.resp_queue, self.address, self.model, self.protocol), daemon=True)

        head_process.start()
        self.logger.info("ThreadedHeadDriver initialized for {addr}".format(addr=self.address))

    def _wait_for_response(self):
        while self.resp_queue.qsize() == 0:
            pass

        ipc_resp = self.resp_queue.get()
        self.logger.info("Received response: {r} with data: {d}".format(r=ipc_resp.response, d=ipc_resp.data))
        resp = (ipc_resp.response, ipc_resp.data)
        return resp

    @staticmethod
    def create_cmd(command:str, data:dict = None):
        return ipcBase.IPCCmd(command=command, data=data)


    def ping(self):
        self.logger.info("Sending ping")
        ipc = self.create_cmd("ping")
        self.cmd_queue.put(ipc)
        self._wait_for_response()

    def send_raw(self, data):
        self.logger.info("Sending raw: {}".format(data))
        ipc = self.create_cmd("raw", {"raw": data})
        self.cmd_queue.put(ipc)
        return self._wait_for_response()

    def power_set(self, state: int):
        self.logger.info("Setting power state to {}".format(state))

        pass

    def power_query(self):
        self.logger.info("Querying power state")
        pass

    def position_set_absolute(self, pos_x, pos_y):
        self.logger.info("Setting absolute position to x: {x}, y: {y}".format(x=pos_x, y=pos_y))
        pass

    def position_set_absolute_hex(self, x: str, y: str):
        self.logger.info("Setting absolute position to hex: {x}, {y}".format(x=x, y=y))
        pass

    def position_set_absolute_with_speed(self, x: int, y: int, speed: int):
        self.logger.info(
            "Setting absolute position to x: {x}, y: {y} with speed {s}".format(x=x, y=y, s=speed))
        pass

    def position_set_absolute_with_speed_hex(self, x: str, y: str, speed: int):
        pass

    def pan_set_speed(self, speed: int):
        pass

    def tilt_set_speed(self, speed: int):
        pass

    def pan_tilt_set_speed(self, pan_speed: int, tilt_speed: int):
        pass

    def pan_tilt_stop(self):
        pass

    def position_query(self):
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