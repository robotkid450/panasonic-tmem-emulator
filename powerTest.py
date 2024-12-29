from multiprocessing.spawn import freeze_support
from panasonicAW import ptzHead
from panasonicAW import ipcBase
import multiprocessing
import logging
import time
logging.basicConfig(level=logging.DEBUG)
# head_logger = logging.getLogger('PanasonicAW')
multiprocessing.logToConsole = True
logger=logging.getLogger(__name__)




def ping():
    ipc = ipcBase.IPCCmd(command="ping")
    h_c_q.put(ipc)

def kill():
    ipc = ipcBase.IPCCmd(command="Stop Main Loop")
    h_c_q.put(ipc)

if __name__ == "__main__":
    h_c_q = multiprocessing.Queue()
    h_r_q = multiprocessing.Queue()
    h = ptzHead.ThreadedHead
    multiprocessing.Process(target=h, args=(h_c_q, h_r_q, "192.168.1.150", "AW-HE40"), daemon=True).start()

    freeze_support()
    run = True
    # ping()
    # h_q.get()
    while run is True:
        logger.info("starting cmd loop")
        if h_r_q.empty():
            ui = input("enter cmd: ")
            match ui:
                case "ping":
                    logger.info("ping")
                    ping()

                case "kill":
                    kill()

                case "posq":
                    logger.info("posq")
                    ipc = ipcBase.IPCCmd(command="Position query")
                    h_c_q.put(ipc)

        logger.info("responce queue length: {}".format(h_r_q.qsize()))
        if not h_r_q.empty():
            ipcResp = h_r_q.get()
            logger.info("ipc: %s", ipcResp)
            # logger.info("cmd : {data}".format(data=ipcResp.command))
            logger.info("resp : {resp}".format(resp=ipcResp.response))
            logger.info("resp data : {data}".format(data=ipcResp.data))


        time.sleep(0.1)


