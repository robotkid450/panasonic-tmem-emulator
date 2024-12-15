import logging
import sqlite3

__version__ = "2.1.4"
logging.getLogger(__name__)

class Database:


    def __init__(self, db_file_path : str) -> None:
        self.cursor = None
        self.db = None
        self.dbFilePath = db_file_path

    def connect_to_db(self):
        self.db = sqlite3.connect(self.dbFilePath, check_same_thread=False)
        self.cursor = self.db.cursor()
        res = self.cursor.execute("SELECT name FROM sqlite_master")
        tables = res.fetchone()
        if tables is None:
            self.camera_table_create()
            self.emulator_data_table_create()
            self.emulator_data_version_set()
        self.emulator_data_version_set()

    def emulator_data_table_create(self):
        self.cursor.execute("CREATE TABLE emulator_data(data_key TEXT, data_value TEXT)")

    def emulator_data_table_insert(self, data_key : str, data_value : str):
        self.cursor.execute("INSERT INTO emulator_data VALUES (?, ?)", (data_key, data_value))
        self.db.commit()

    def emulator_data_table_update(self, data_key : str, data_value : str):
        self.cursor.execute("UPDATE emulator_data SET data_value = ? WHERE data_key = ?", (str(data_value), str(data_key)))
        self.db.commit()

    def emulator_data_table_delete(self, data_key : str):
        self.cursor.execute("DELETE FROM emulator_data WHERE data_key = ?", (data_key,))
        self.db.commit()

    def emulator_data_table_query(self, data_key : str):
        data = self.cursor.execute("SELECT * FROM emulator_data WHERE data_key = ?", (data_key,))
        return data.fetchone()

    def emulator_data_version_get(self):
        version = self.emulator_data_table_query("version")
        return version

    def emulator_data_version_set(self):
        db_version = self.emulator_data_version_get()
        if db_version is None:
            self.emulator_data_table_insert(data_key="version", data_value=__version__)
        else:
            self.emulator_data_table_update(data_key="version", data_value=__version__)

    def camera_table_create(self):
        self.cursor.execute("CREATE TABLE cameras( id INTEGER PRIMARY KEY , address TEXT NOT NUll, port INTEGER NOT NUll, model TEXT NOT NULL )")

    def preset_table_create(self, camera_id : int):
        sql_cmd = f"CREATE TABLE preset_{camera_id}(id INTEGER PRIMARY KEY, position_start_x INT, position_start_y INT, position_end_x INT, position_end_y INT, zoom_start INT, zoom_end INT, speed INT)"
        self.cursor.execute(sql_cmd)

    def preset_table_delete(self, camera_id : int):
        sql_cmd = f"DROP TABLE preset_{camera_id}"
        self.cursor.execute(sql_cmd)

    def camera_add(self, model : str, address : str, port=80):
        res = self.cursor.execute("SELECT * FROM cameras WHERE address LIKE ?", (address,))
        results = res.fetchall()

        if len(results) != 0 :
            for item in results:
                cam_address = item[1]
                raise ValueError(f"Address {cam_address} already in use.")

        cam_data = (address, port, model)
        self.cursor.execute("INSERT INTO cameras (address, port, model) VALUES(?, ?, ?)", cam_data)
        self.db.commit()
        res = self.cursor.execute("SELECT * FROM cameras WHERE address LIKE ?", ( address,))
        camera_id, caddr, camera_port, cmodel = res.fetchone()
        self.preset_table_create(camera_id)

    def camera_delete(self, camera_id):
        #check to see if camera is defined
        if self.camera_exists(camera_id):
            #if camera is defined remove camera and preset table
            self.cursor.execute("DELETE FROM cameras WHERE id=(?)", (camera_id,))
            self.db.commit()
            self.preset_table_delete(camera_id)
        else:
            raise ValueError(f"No camera defined for id : {camera_id}")

    def camera_exists(self, camera_id : int) -> bool :
        #check to see if camera is defined
        res = self.cursor.execute("SELECT * FROM cameras WHERE id=(?)", (camera_id,))
        results = res.fetchone()
        if results is None:
            return False
            # raise ValueError(f"No camera defined for id : {id}")
        else:
            return True

    def camera_list(self) -> list:
        res = self.cursor.execute("SELECT * FROM cameras")
        results = res.fetchall()
        return results

    def camera_get(self, camera_id : int):
        res = self.cursor.execute("SELECT * FROM cameras WHERE id=(?)", (camera_id,))
        results = res.fetchone()
        if results is None:
            raise ValueError(f"No camera defined with ID {camera_id}")
        else:
            return results

    def preset_create(self, camera_id : int, position_start_x : int, position_start_y : int, position_end_x : int, position_end_y : int, zoom_start : int, zoom_end : int, speed : int, preset_id : int = None):
        if not self.camera_exists(camera_id):
            raise ValueError(f"No camera defined for id: {camera_id}")
        
        if preset_id is None:
            preset_data = (position_start_x, position_start_y, position_end_x, position_end_y, zoom_start, zoom_end, speed)
            sql_statement = f"INSERT INTO preset_{camera_id} (position_start_x, position_start_y, position_end_x, position_end_y, zoom_start, zoom_end, speed) VALUES ( ? , ? , ? , ? , ? , ? , ?)"
        elif preset_id is not None:
            preset_data = (preset_id, position_start_x, position_start_y, position_end_x, position_end_y, zoom_start, zoom_end, speed)
            sql_statement = f"INSERT INTO preset_{camera_id} (id, position_start_x, position_start_y, position_end_x, position_end_y, zoom_start, zoom_end, speed) VALUES ( ? , ? , ? , ? , ? , ? , ? , ?)"
        else:
            raise ValueError("Invalid preset data")
        self.cursor.execute(sql_statement, preset_data)
        self.db.commit()

    def preset_update(self, camera_id : int, preset_id : int, position_start_x : int, position_start_y : int, position_end_x : int, position_end_y : int, zoom_start : int, zoom_end : int, speed : int):
        if self.camera_exists(camera_id):
            if self.preset_exists(camera_id, preset_id):
                sql_statement = f" UPDATE preset_{camera_id} SET position_start_x = \'{position_start_x}\', position_start_y = \'{position_start_y}\', position_end_x = \'{position_end_x}\', position_end_y = \'{position_end_y}\', zoom_start = \'{zoom_start}\', zoom_end = \'{zoom_end}\', speed = \'{speed}\' WHERE id = \'{preset_id}\'"
                self.cursor.execute(sql_statement, )
            else:
                sql_statement = f"INSERT INTO preset_{camera_id} (position_start_x, position_start_y, position_end_x, position_end_y, zoom_start, zoom_end, speed) VALUES ( ? , ? , ? , ? , ? , ? , ?)"
            
            self.db.commit()
        else:
            raise ValueError(f"ERROR: No camera defined for id: {camera_id}")
        

    def preset_delete(self, camera_id : int, preset_id : int):
        if self.preset_exists(camera_id, preset_id):
            sql_statement = f"DELETE FROM preset_{camera_id} WHERE id=(?)"
            self.cursor.execute(sql_statement, (preset_id,))
            self.db.commit()
        else:
            raise ValueError(f"preset #{preset_id} does not exist for camera #{camera_id}")

    def preset_exists(self, camera_id : int, preset_id : int) -> bool:
        if self.camera_exists(camera_id):
            sql_statement = f"SELECT * FROM preset_{camera_id} WHERE id=(?)"
            res = self.cursor.execute(sql_statement, (preset_id,))
            result = res.fetchall()
            if len(result) == 0:
                return False # no preset for camera
            else:
                return True 
        else: 
            raise ValueError(f"No camera defined for id : {camera_id}")

    def preset_list(self, camera_id : int) -> list:
        if self.camera_exists(camera_id):
            sql_statement = f"SELECT * FROM preset_{camera_id}"
            res = self.cursor.execute(sql_statement)
            results = res.fetchall()
            return results
        else:
            raise ValueError(f"Camera #{camera_id} does not exist.")

    def preset_get(self, camera_id : int, preset_id : int):
        if self.preset_exists(camera_id, preset_id):
            sql_statement = f"SELECT * FROM preset_{camera_id} where id={preset_id}"
            res = self.cursor.execute(sql_statement)
            results = res.fetchone()
            logging.debug(results)
            return results
        else:
            raise ValueError(f"Preset: {preset_id} does not exist for camera: {camera_id}.")


if  __name__ == "__main__":
    db = Database("test.db")
    db.connect_to_db()
