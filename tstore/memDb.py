import sqlite3
class Database:
    def __init__(self, dbfilepath : str) -> None:
        self.dbFilePath = dbfilepath

    def connectToDb(self):
        self.db = sqlite3.connect(self.dbFilePath, check_same_thread=False)
        self.cursor = self.db.cursor()
        res = self.cursor.execute("SELECT name FROM sqlite_master")
        tables = res.fetchone()
        if tables == None:
            self.createCameraTable()

    def createCameraTable(self):
        self.cursor.execute("CREATE TABLE cameras( id INTEGER PRIMARY KEY , address TEXT NOT NUll, port INTEGER NOT NUll, model text NOT NULL )")

    def createPresetTable(self, cameraid : int):
        sqlCmd = f"CREATE TABLE preset_{cameraid}(id INTEGER PRIMARY KEY, position_start_x TEXT NOT NUll, position_start_y TEXT NOT NUll, position_end_x TEXT NOT NUll, position_end_y TEXT NOT NUll, zoom_start TEXT NOT NUll, zoom_end TEXT NOT NUll, speed TEXT NOT NUll)"
        self.cursor.execute(sqlCmd)

    def deletePresetTable(self, cameraid : int):
        sqlCmd = f"DROP TABLE preset_{cameraid}"
        self.cursor.execute(sqlCmd)

    def addCamera(self, model : str, address : str, port=80):
        res = self.cursor.execute("SELECT * FROM cameras WHERE address LIKE ?", (address,))
        results = res.fetchall()

        if len(results) != 0 :
            for item in results:
                camaddress = item[1]
                raise ValueError(f"Address {camaddress} already in use.")
            
        
        camData = (address, port, model)
        self.cursor.execute("INSERT INTO cameras(address, port, model) VALUES(?, ?, ?)", camData)
        self.db.commit()
        res = self.cursor.execute("SELECT * FROM cameras WHERE address LIKE ?", ( address,))
        id, caddr, cport, cmodel = res.fetchone()
        self.createPresetTable(id)

    def deleteCamera(self, id):
        #check to see if camera is defined
        if self.checkCameraExists(id):
            #if camera is defined remove camera and preset table
            self.cursor.execute("DELETE FROM cameras WHERE id=(?)", (id,))
            self.db.commit()
            self.deletePresetTable(id)
        else:
            raise ValueError(f"No camera defined for id : {id}")

    def checkCameraExists(self, id : int) -> bool : 
        #check to see if camera is defined
        res = self.cursor.execute("SELECT * FROM cameras WHERE id=(?)", (id,))
        results = res.fetchone()
        if results == None:
            return False
            # raise ValueError(f"No camera defined for id : {id}")
        else:
            return True

    def getCameras(self) -> list:
        res = self.cursor.execute("SELECT * FROM cameras")
        results = res.fetchall()
        return results

    def getCamera(self, camera_id : int):
        res = self.cursor.execute("SELECT * FROM cameras WHERE id=(?)", (camera_id,))
        results = res.fetchone()
        if results == None:
            raise ValueError(f"No camera defined with ID {camera_id}")
        else:
            return results

    def createPreset(self, camera_id : int, position_start_x : str, position_start_y : str, position_end_x : str, position_end_y : str, zoom_start : str, zoom_end : str, speed : str):
        if not self.checkCameraExists(camera_id):
            raise ValueError(f"No camera defined for id: {camera_id}")
        preset_data = (position_start_x, position_start_y, position_end_x, position_end_y, zoom_start, zoom_end, speed)
        sql_statement = f"INSERT INTO preset_{camera_id} (position_start_x, position_start_y, position_end_x, position_end_y, zoom_start, zoom_end, speed) VALUES ( ? , ? , ? , ? , ? , ? , ?)"
        self.cursor.execute(sql_statement, preset_data)
        self.db.commit()

    def deletePreset(self, camera_id : int, preset_id : int):
        if self.checkPresetExists(camera_id, preset_id):
            sql_statment = f"DELETE FROM preset_{camera_id} WHERE id=(?)"
            self.cursor.execute(sql_statment, (preset_id,))
            self.db.commit()
        else:
            raise ValueError(f"preset #{preset_id} does not exist for camera #{camera_id}")

    def checkPresetExists(self, camera_id : int, preset_id : int) -> bool:
        if self.checkCameraExists(camera_id):
            sql_statment = f"SELECT * FROM preset_{camera_id} WHERE id=(?)"
            res = self.cursor.execute(sql_statment, (preset_id,))
            result = res.fetchall()
            if len(result) == 0:
                return False # no preset for camera
            else:
                return True 
        else: 
            raise ValueError(f"No camera defined for id : {camera_id}")

    def listPresets(self, camera_id : int) -> list:
        if self.checkCameraExists(camera_id):
            sql_statment = f"SELECT * FROM preset_{camera_id}"
            res = self.cursor.execute(sql_statment)
            results = res.fetchall()
            return results
        else:
            raise ValueError(f"Camera #{camera_id} does not exist.")

    def getPreset(self, camera_id : int, preset_id : int):
        if self.checkPresetExists(camera_id, preset_id):
            sql_statment = f"SELECT * FROM preset_{camera_id} where id={preset_id}"
            res = self.cursor.execute(sql_statment)
            results = res.fetchone()
            return results
        else:
            raise ValueError(f"Preset: {preset_id} does not exist for camera: {camera_id}.")


if  __name__ == "__main__":
    db = Database("test.db")
    db.connectToDb()
