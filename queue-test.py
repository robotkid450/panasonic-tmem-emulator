# from panasonicAW import ptzHead
import multiprocessing
from multiprocessing.spawn import freeze_support

import queueworker

class IPCCmd:
    def __init__(self, command :str = None, data_1 = None, data_2 = None, data_3 = None, data_4 = None,
                 data_5 = None, data_6 = None):
        self.command = command
        self.data_1 = data_1
        self.data_2 = data_2
        self.data_3 = data_3
        self.data_4 = data_4
        self.data_5 = data_5
        self.data_6 = data_6

class IPCResponse:
    def __init__(self, command :str = None, data_1 = None, data_2 = None, data_3 = None,data_4 = None,
                 data_5 = None, data_6 = None):
        self.command = command
        self.data_1 = data_1
        self.data_2 = data_2
        self.data_3 = data_3
        self.data_4 = data_4
        self.data_5 = data_5
        self.data_6 = data_6


if __name__ == "__main__":

    head_queue = multiprocessing.Queue()
    test = queueworker.Worker
    # head = ptzHead.ThreadedHead(head_queue, "192.168.1.150")

    multiprocessing.Process(target=test, args=(head_queue,)).start()
    freeze_support()
    input()

    head_queue.put(IPCCmd("ping"))
    head_queue.put(IPCCmd("ping"))
    head_queue.put(IPCCmd("ping"))
    print(head_queue.qsize())
    input()
    head_queue.put(IPCCmd("ping"))
    print(head_queue.qsize())
    input()
    while head_queue.qsize() > 0:
        print(head_queue.qsize())
        print(head_queue.get().command)
    head_queue.put(IPCCmd("stop"))
    print(head_queue.get().command)

