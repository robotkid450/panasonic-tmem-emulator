# from panasonicAW import ptzHead
import multiprocessing
from multiprocessing.spawn import freeze_support

import queueworker

class IPCCmd:
    def __init__(self, command :str = None, data = dict):
        self.command = command
        self.data = data

class IPCResponse:
    def __init__(self, response :str = None, data = dict):
        self.response = response
        self.data = data



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

