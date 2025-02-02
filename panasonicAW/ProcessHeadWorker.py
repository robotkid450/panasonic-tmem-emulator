from panasonicAW import ptzHead
from panasonicAW import ipcBase
import multiprocessing
import logging
import time

from panasonicAW.CameraExceptions import CameraBusyException


class Worker(ptzHead.Camera):
    def __init__(self, cmd_queue : multiprocessing.Queue, resp_queue:multiprocessing.Queue,
                 address, model = 'default', protocol='http'):
        # logging.basicConfig(level=logging.DEBUG, filename="worker-{address}.log".format(address=address), filemode='w')
        logging.basicConfig(level=logging.DEBUG)
        self.worker_logger = logging.getLogger(__name__)
        self.worker_logger.info("Initializing ProcessHeadWorker")
        self.cmd_queue = cmd_queue
        self.resp_queue = resp_queue
        self.run = True
        # ptzHead.Camera.__init__(self, address, model, protocol)
        super().__init__(address, model, protocol)
        self.head_power = self.power_query()
        self.worker_logger.info("ProcessHeadWorker initialized for {addr}".format(addr=self.address))
        self.runloop()


    def _create_and_send_resp(self, command:str,  resp_data : dict = None):
        resp = ipcBase.IPCResponse(response=command, data=resp_data)
        self.resp_queue.put(resp)


    def runloop(self):
        self.worker_logger.info("Starting ProcessHeadWorker main loop")
        self.worker_logger.debug("loop run : {}".format(self.run))
        self.run = True
        time_difference = 0
        while self.run:
            previous_time_difference = time_difference
            time_difference = self._time_millis() - self.time_of_last_command
            if time_difference == previous_time_difference :
                pass
            elif time_difference < 150 :
                self.worker_logger.debug("waiting for camera to become ready for next command: {}".format(time_difference))
            else:
                self.process_queue()
                if not self.run:
                    break
        self.worker_logger.info("Exiting ProcessHeadWorker main loop")


    def process_queue(self):
        if not self.cmd_queue.empty():
            self.worker_logger.debug("Queue not empty.")
            ipc_command = self.cmd_queue.get()
            self.worker_logger.debug("IPC command: %s", ipc_command.command)
            self.process_command(ipc_command)
        else:
            pass

    def process_command(self, ipc_message):
        self.worker_logger.debug("processing command")
        self.worker_logger.debug("command: {cmd}".format(cmd=ipc_message.command))
        if self.head_power == 0:
            self._create_and_send_resp("ERROR", {"power_query": self.head_power})
        match ipc_message.command:
            case "stop_main_loop":
                self.worker_logger.info("Stopping Main Loop")
                self._create_and_send_resp("Stopping Main Loop")
                self.run = False
                self.cmd_queue.close()
                self.resp_queue.close()

            case "ping":
                self.worker_logger.info("Ping | Pong")
                resp_data = {"address": self.address}
                self._create_and_send_resp("pong", resp_data )

            case "power_set":
                self.worker_logger.info("Power Set")
                self.worker_logger.info("Setting Power to {}".format(ipc_message.data))
                try:
                    head_resp = self.power_set(ipc_message.data["state"])
                    self._create_and_send_resp("power_set", resp_data=head_resp)
                except TimeoutError as e:
                    data = {"EXCEPTION": e}
                    self._create_and_send_resp("power_set", resp_data=data)


            case "power_query":
                self.worker_logger.info("Power Query")
                head_resp = self.power_query()
                self._create_and_send_resp("power_query", resp_data=head_resp)

            case "position_query":
                self.worker_logger.info("running Position query")
                try:
                    pos= self.position_query()
                    self._create_and_send_resp("position_query", resp_data=pos)
                except Exception as e:
                    self._create_and_send_resp("position_query", resp_data={"exception" : e})

            case "position_set_abs":
                self.worker_logger.info("running Position set abs")
                self.worker_logger.debug(ipc_message.data)
                pos_x = ipc_message.data["x"]
                pos_y = ipc_message.data["y"]
                self.worker_logger.debug("Position x: {}, y: {}".format(pos_x, pos_y))
                try:
                    head_resp = self.position_set_absolute( pos_x, pos_y)
                    self._create_and_send_resp("position_set_abs", resp_data=head_resp)
                except Exception as e:
                    self._create_and_send_resp("position_set_abs", resp_data={"exception" : e})


            case "position_set_abs_hex":
                self.worker_logger.info("running Position set abs hex")
                self.worker_logger.debug(ipc_message.data)
                pos_x = ipc_message.data["x"]
                pos_y = ipc_message.data["y"]
                self.worker_logger.debug("Position x: {}, y: {}".format(pos_x, pos_y))
                head_resp = self.position_set_absolute_hex( pos_x, pos_y)
                self._create_and_send_resp("position_set_abs_hex", resp_data=head_resp)

            case "position_set_abs_speed":
                self.worker_logger.info("running Position set abs speed")
                self.worker_logger.debug(ipc_message.data)
                pos_x = ipc_message.data["x"]
                pos_y = ipc_message.data["y"]
                speed = ipc_message.data["speed"]
                self.worker_logger.debug("Position x: {}, y: {}, speed: {}".format(pos_x, pos_y, speed))
                head_resp = self.position_set_absolute_with_speed(pos_x, pos_y, speed)
                self._create_and_send_resp("position_set_abs_speed", resp_data=head_resp)

            case "position_set_abs_speed_hex":
                self.worker_logger.info("running Position set abs speed_hex")
                self.worker_logger.debug(ipc_message.data)
                pos_x = ipc_message.data["x"]
                pos_y = ipc_message.data["y"]
                speed = ipc_message.data["speed"]
                self.worker_logger.debug("Position_hex x: {}, y: {}, speed: {}".format(pos_x, pos_y, speed))
                head_resp = self.position_set_absolute_with_speed_hex(pos_x, pos_y, speed)
                self._create_and_send_resp("position_set_abs_speed_hex", resp_data=head_resp)

            case "pan_tilt_set_speed":
                self.worker_logger.info("pan tilt set speed")
                self.worker_logger.debug(ipc_message.data)
                pan_speed = ipc_message.data["pan_speed"]
                tilt_speed = ipc_message.data["tilt_speed"]
                self.worker_logger.debug("Pan Speed: {}".format(pan_speed))
                self.worker_logger.debug("Tilt Speed: {}".format(tilt_speed))
                if pan_speed is None:
                    head_resp = self.tilt_set_speed(tilt_speed)
                elif tilt_speed is None:
                    head_resp = self.pan_set_speed(pan_speed)
                else:
                    head_resp = self.pan_tilt_set_speed(pan_speed, tilt_speed)
                self._create_and_send_resp("pan_tilt_set_speed", resp_data=head_resp)


            case "zoom query":
                pass


            case "zoom set abs":
                pass

            case "zoom move speed":
                pass

if __name__ == "__main__":
    # h = ptzHead.Camera("asdf")
    pass