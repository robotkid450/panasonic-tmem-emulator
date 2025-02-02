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

class Worker:
    def __init__(self, ipc_queue):
        self.ipc_queue = ipc_queue
        self.running = True

    def run_loop(self):
        while self.running:
            self.process_queue()

    def shutdown(self):
        resp = IPCResponse("stopped")
        self.ipc_queue.put(resp)
        self.ipc_queue.task_done()
        self.running = False

    def process_queue(self):
        ipc_cmd = self.ipc_queue.get()
        if ipc_cmd.command == "stop":
            self.shutdown()
        elif ipc_cmd.command == "ping":
            ipc_cmd.data_1 = "pong"
            self.ipc_queue.put(ipc_cmd)


