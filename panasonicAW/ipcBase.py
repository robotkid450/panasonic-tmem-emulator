class IPCCmd:
    def __init__(self, command :str = None, data = dict):
        self.command = command
        self.data = data

class IPCResponse:
    def __init__(self, response :str = None, data = dict):
        self.response = response
        self.data = data

class IPCException(Exception):
    def __init__(self, response :str = None, data = dict):
        pass