class IPCCmd:
    def __init__(self, command :str = None, data : dict = None):
        self.command = command.lower()
        self.data = data

class IPCResponse:
    def __init__(self, response :str = None, data :dict = None):
        self.response = response.lower()
        self.data = data

class IPCException(Exception):
    def __init__(self, response :str = None, data = dict):
        pass