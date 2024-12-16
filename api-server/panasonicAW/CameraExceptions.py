class CameraCommandUnsupportedException(BaseException): #eR1
    def __init__(self, command):
        self.command = command
        super().__init__()

    def __str__(self):
        return "Malformed or unsupported camera command: {0}".format(self.command)

class CameraBusyException(BaseException): #eR2
    def __init__(self, command):
        self.command = command
        super().__init__()

    def __str__(self):
        return "Camera powered off or busy for command: {0}".format(self.command)

class CameraOutSideSupportedRangeException(BaseException): #eR3
    def __init__(self, command):
        self.command = command
        super().__init__()

    def __str__(self):
        return "Supplied value out of range for command: {0}".format(self.command)
