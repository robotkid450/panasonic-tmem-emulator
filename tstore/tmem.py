from random import randrange

class tmem:
    def __init__(self) -> None:
        self.id = -1
        self.pos_start = ("", "")
        self.pos_end = ("", "")
        self.zoom_start = ""
        self.zoom_end = ""
        self.focus_start = ""
        self.focus_end = ""
        self.runtime = 0
    
    def setPosStart(self, pos) -> None:
        self.pos_start = pos

    def setPosEnd(self, pos) -> None:
        self.pos_end = pos
    
    def setZoomStart(self, zoom) -> None:
        self.zoom_start = zoom

    def setZoomEnd(self, zoom) -> None:
        self.zoom_end = zoom

    def setFocusStart(self, focus) -> None:
        self.focus_start = focus

    def setFocusStart(self, focus) -> None:
        self.focus_start = focus

    def setId(self, id) -> None:
        self.id = id

    def setRunTime(self, runTime:int) -> None:
        self.runtime = runTime

    def getPosStart(self) -> tuple:
        return self.pos_start
    
    def getPosEnd(self) -> tuple:
        return self.pos_end

    def getZoomStart(self) -> str:
        return self.zoom_start

    def getZoomEnd(self) -> str:
        return self.zoom_end

    def getFocusStart(self) -> str:
        return self.focus_start

    def getFocusEnd(self) -> str:
        return self.focus_end

    def getId(self) -> int:
        return self.id

    def getRunTime(self) -> int:
        return self.runtime

    def debugFillTmem(self):
        self.pos_start = self.debugRandPos()
        self.pos_end = self.debugRandPos()
        self.focus_start = self.debugRandZF()
        self.focus_end = self.debugRandZF()
        self.zoom_start = self.debugRandZF()
        self.runtime = self.debugRandRT()

    def debugRandPos(self)-> tuple:
        pan = randrange(-175, 175)
        tilt = randrange(-100, 100)
        return (str(pan), str(tilt))
    
    def debugRandZF(self) -> str:
        zoom = randrange(0, 100)
        return str(zoom)

    def debugRandRT(self) -> int:
        time = randrange(0, 120)
        return time
