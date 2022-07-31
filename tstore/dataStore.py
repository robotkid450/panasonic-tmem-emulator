import pickle
from tstore import tmem

class dataStore:
    def __init__(self, spath) -> None:
        self.spath = spath
        self.tmems = []
        self.tmems_loaded = False
    
    def savePickle(self):
        with open((self.spath) , 'wb') as f:
            pickle.dump(self.tmems, f, pickle.HIGHEST_PROTOCOL)

        f.close()

    def loadPickle(self):
        try:
            with open((self.spath), 'rb') as f:
                self.tmems = pickle.load(f)
            f.close()
        except FileNotFoundError:
            self.createFile()
            self.loadPickle()

        self.tmems_loaded = True

    def createFile(self):
        with open(self.spath, 'ab') as f:
            print("file created at: " + self.spath)
            self.savePickle()
        f.close()
        
        

    def addTmem(self, tmem: tmem):
        if self.tmems_loaded == False:
            self.loadPickle()
        
        tmemId = len(self.tmems)
        tmemItem = tmem
        tmemItem.id = tmemId

        self.tmems.append(tmemItem)

    def removeTmem(self, id):
        del(self.tmems[id])
    
    def getTmemIds(self) -> list:
        ids = []
        for item in self.tmems:
            ids.append(item.id)
        
        return ids

