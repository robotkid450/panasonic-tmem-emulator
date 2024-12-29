from panasonicAW import ptzHead
from panasonicAW import ipcBase
import multiprocessing
import logging

class ProcessHeadWorker(ptzHead.Camera):
    def __init__(self, cmd_queue : multiprocessing.Queue, resp_queue:multiprocessing.Queue,
                 address, model = 'default', protocol='http'):
        # logging.basicConfig(level=logging.DEBUG, filename="worker-{address}.log".format(address=address), filemode='w')
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger(__name__ + "ProcessHeadWorker")
        self.logger.info("Initializing ProcessHeadWorker")
        self.cmd_queue = cmd_queue
        self.resp_queue = resp_queue
        self.run = True
        ptzHead.Camera.__init__(self, address, model, protocol)
        self.logger.info("ProcessHeadWorker initialized for {addr}".format(addr=self.address))
        self.runloop()


    def runloop(self):
        self.logger.info("Starting ProcessHeadWorker main loop")
        self.logger.debug("loop run : {}".format(self.run))
        self.run = True
        while self.run:
            self.process_queue()
            if not self.run:
                break
        self.logger.info("Exiting ProcessHeadWorker main loop")


    def process_queue(self):
        if not self.cmd_queue.empty():
            self.logger.debug("Queue not empty.")
            ipc_command = self.cmd_queue.get()
            self.logger.debug("IPC command: %s", ipc_command.command)
            self.process_command(ipc_command)
        else:
            pass

    def process_command(self, ipc_message):
        self.logger.debug("processing command")
        self.logger.debug("command: {cmd}".format(cmd=ipc_message.command))
        match ipc_message.command:
            case "stop main loop":
                self.logger.info("Stopping Main Loop")
                resp = ipcBase.IPCResponse(response="Stopping Main Loop")
                self.resp_queue.put(resp)
                self.run = False
                self.cmd_queue.close()
                self.resp_queue.close()
            case "ping":
                self.logger.info("Ping | Pong")
                resp = ipcBase.IPCResponse("pong", {"address": self.address})
                self.resp_queue.put(resp)

            case "position query":
                self.logger.info("running Position query")
                pos = ptzHead.Camera.position_query(self)
                resp = ipcBase.IPCResponse("Position query", {"position": pos})
                self.resp_queue.put(resp)

            case "position set abs":
                self.logger.info("running Position set abs")
                self.logger.debug(ipc_message.data)
                pos_x = ipc_message.data["position"][0]
                pos_y = ipc_message.data["position"][1]
                self.logger.debug("Position x: {}, y: {}".format(pos_x, pos_y))

                ptzHead.Camera.position_set_absolute(self, pos_x, pos_y)

            case "position move speed":
                pass

            case "zoom query":
                pass


            case "zoom set abs":
                pass

            case "zoom move speed":
                pass