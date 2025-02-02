import logging
import sqlite3

__version__ = "2.1.6"
log = logging.getLogger(__name__)

class Database:


    def __init__(self, db_file_path : str) -> None:
        self.cursor = None
        self.db = None
        self.dbFilePath = db_file_path

    def connect_to_db(self):
        log.info("Connecting to DB")
        self.db = sqlite3.connect(self.dbFilePath, check_same_thread=False)
        self.cursor = self.db.cursor()
        res = self.cursor.execute("SELECT name FROM sqlite_master")
        tables = res.fetchone()
        if tables is None:
            log.info("No tables found")
            log.info("Creating tables")
            self.camera_table_create()
            self.emulator_data_table_create()
            self.emulator_data_version_set()
        self.emulator_data_version_set()

    def emulator_data_table_create(self):
        log.info("Creating emulator data table")
        self.cursor.execute("CREATE TABLE emulator_data(data_key TEXT, data_value TEXT)")

    def emulator_data_table_insert(self, data_key : str, data_value : str):
        log.info("Inserting data into emulator data table {key} : {data}".format(key=data_key, data=data_value))
        self.cursor.execute("INSERT INTO emulator_data VALUES (?, ?)", (data_key, data_value))
        self.db.commit()

    def emulator_data_table_update(self, data_key : str, data_value : str):
        log.info("Updating data into emulator data table {key} : {data}".format(key=data_key, data=data_value))
        self.cursor.execute("UPDATE emulator_data SET data_value = ? WHERE data_key = ?", (str(data_value), str(data_key)))
        self.db.commit()

    def emulator_data_table_delete(self, data_key : str):
        log.info("Deleting data from emulator data table {key}".format(key=data_key))
        self.cursor.execute("DELETE FROM emulator_data WHERE data_key = ?", (data_key,))
        self.db.commit()

    def emulator_data_table_query(self, data_key : str):
        log.info("Querying data from emulator data table {key}".format(key=data_key))
        data = self.cursor.execute("SELECT * FROM emulator_data WHERE data_key = ?", (data_key,))
        return data.fetchone()

    def emulator_data_version_get(self):
        version = self.emulator_data_table_query("version")
        log.info("Getting version data from emulator data table : {version}".format(version=version))
        return version

    def emulator_data_version_set(self):
        log.info("Setting version data from emulator data table : {version}".format(version=__version__))
        db_version = self.emulator_data_version_get()
        if db_version is None:
            self.emulator_data_table_insert(data_key="version", data_value=__version__)
        else:
            self.emulator_data_table_update(data_key="version", data_value=__version__)

    def camera_table_create(self):
        log.info("Creating camera table")
        self.cursor.execute("CREATE TABLE cameras( id INTEGER PRIMARY KEY , address TEXT NOT NUll, port INTEGER NOT NUll, model TEXT NOT NULL )")

    def preset_table_create(self, camera_id : int):
        log.info("Creating preset table for camera {camera_id}".format(camera_id=camera_id))
        sql_cmd = f"CREATE TABLE preset_{camera_id}(id INTEGER PRIMARY KEY, position_start_x INT, position_start_y INT, position_end_x INT, position_end_y INT, zoom_start INT, zoom_end INT, speed INT)"
        self.cursor.execute(sql_cmd)

    def preset_table_delete(self, camera_id : int):
        log.info("Deleting preset table for camera {camera_id}".format(camera_id=camera_id))
        sql_cmd = f"DROP TABLE preset_{camera_id}"
        self.cursor.execute(sql_cmd)

    def camera_add(self, model : str, address : str, port=80):
        log.info("Adding camera {model} to preset table at address {addr}:{port}".format(
            model=model, addr=address, port=port))
        res = self.cursor.execute("SELECT * FROM cameras WHERE address LIKE ?", (address,))
        results = res.fetchall()

        if len(results) != 0 :
            for item in results:
                cam_address = item[1]
                error_message = "Address {cam_address} already in use.".format(cam_address=cam_address)
                log.error(error_message)
                raise ValueError(error_message)

        cam_data = (address, port, model)
        self.cursor.execute("INSERT INTO cameras (address, port, model) VALUES(?, ?, ?)", cam_data)
        self.db.commit()
        res = self.cursor.execute("SELECT * FROM cameras WHERE address LIKE ?", ( address,))
        camera_id, caddr, camera_port, cmodel = res.fetchone()
        self.preset_table_create(camera_id)
        log.info("Camera {camera_id} added to preset table".format(camera_id=camera_id))

    def camera_delete(self, camera_id):
        log.info("Deleting camera {camera_id}".format(camera_id=camera_id))
        #check to see if camera is defined
        if self.camera_exists(camera_id):
            #if camera is defined remove camera and preset table
            self.cursor.execute("DELETE FROM cameras WHERE id=(?)", (camera_id,))
            self.db.commit()
            self.preset_table_delete(camera_id)
        else:
            error_message = "Camera {camera_id} does not exist.".format(camera_id=camera_id)
            log.error(error_message)
            raise ValueError(error_message)
        log.info("Camera {camera_id} deleted from preset table".format(camera_id=camera_id))

    def camera_exists(self, camera_id : int) -> bool :
        log.info("Checking if camera {camera_id} exists".format(camera_id=camera_id))
        #check to see if camera is defined
        res = self.cursor.execute("SELECT * FROM cameras WHERE id=(?)", (camera_id,))
        results = res.fetchone()
        if results is None:
            log.info("Camera {camera_id} does not exist".format(camera_id=camera_id))
            return False
            # raise ValueError(f"No camera defined for id : {id}")
        else:
            log.info("Camera {camera_id} exists".format(camera_id=camera_id))
            return True

    def camera_list(self) -> list:
        log.info("Listing all cameras")
        res = self.cursor.execute("SELECT * FROM cameras")
        results = res.fetchall()
        log.debug(results)
        return results

    def camera_get(self, camera_id : int):
        res = self.cursor.execute("SELECT * FROM cameras WHERE id=(?)", (camera_id,))
        results = res.fetchone()
        if results is None:
            raise ValueError(f"No camera defined with ID {camera_id}")
        else:
            log.debug(results)
            return results

    def preset_create(self, camera_id : int, position_start_x : str, position_start_y : str, position_end_x : str,
                      position_end_y : str, zoom_start : str, zoom_end : str, speed : int, preset_id : int = None):
        log.info("Creating preset {pre_id} for camera {camera_id}".format(camera_id=camera_id, pre_id=preset_id))
        if not self.camera_exists(camera_id):
            error_message = "Camera {camera_id} does not exist.".format(camera_id=camera_id)
            log.error(error_message)
            raise ValueError(error_message)
        
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

    def preset_update(self, camera_id : int, preset_id : int, position_start_x : str, position_start_y : str,
                      position_end_x : str, position_end_y : str, zoom_start : str, zoom_end : str, speed : int):
        if self.camera_exists(camera_id):
            if self.preset_exists(camera_id, preset_id):
                sql_statement = f" UPDATE preset_{camera_id} SET position_start_x = \'{position_start_x}\', position_start_y = \'{position_start_y}\', position_end_x = \'{position_end_x}\', position_end_y = \'{position_end_y}\', zoom_start = \'{zoom_start}\', zoom_end = \'{zoom_end}\', speed = \'{speed}\' WHERE id = \'{preset_id}\'"
                self.cursor.execute(sql_statement, )
            else:
                sql_statement = f"INSERT INTO preset_{camera_id} (position_start_x, position_start_y, position_end_x, position_end_y, zoom_start, zoom_end, speed) VALUES ( ? , ? , ? , ? , ? , ? , ?)"
            
            self.db.commit()
        else:
            error_message = f"ERROR: No camera defined for id: {camera_id}"
            log.error(error_message)
            raise ValueError(error_message)
        

    def preset_delete(self, camera_id : int, preset_id : int):
        log.info(f"Deleteing preset {preset_id} from camera {camera_id}".format(
            preset_id=preset_id, camera_id=camera_id))
        if self.preset_exists(camera_id, preset_id):
            sql_statement = f"DELETE FROM preset_{camera_id} WHERE id=(?)"
            self.cursor.execute(sql_statement, (preset_id,))
            self.db.commit()
        else:
            error_message = f"preset #{preset_id} does not exist for camera #{camera_id}"
            log.error(error_message)
            raise ValueError(error_message)

    def preset_exists(self, camera_id : int, preset_id : int) -> bool:
        log.info("Checking if preset {preset_id} exists for camera {camera_id}".format(
            preset_id=preset_id, camera_id=camera_id))
        if self.camera_exists(camera_id):
            sql_statement = f"SELECT * FROM preset_{camera_id} WHERE id=(?)"
            res = self.cursor.execute(sql_statement, (preset_id,))
            result = res.fetchall()
            if len(result) == 0:
                return False # no preset for camera
            else:
                return True 
        else:
            error_message = f"No camera defined for id : {camera_id}"
            log.error(error_message)
            raise ValueError(error_message)

    def preset_list(self, camera_id : int) -> list:
        log.info("Listing all presets")
        if self.camera_exists(camera_id):
            sql_statement = f"SELECT * FROM preset_{camera_id}"
            res = self.cursor.execute(sql_statement)
            results = res.fetchall()
            log.debug(results)
            return results
        else:
            error_message = f"Camera #{camera_id} does not exist."
            log.error(error_message)
            raise ValueError(error_message)

    def preset_get(self, camera_id : int, preset_id : int):
        log.info("Getting preset {preset_id} from camera {camera_id}".format(preset_id=preset_id, camera_id=camera_id))
        if self.preset_exists(camera_id, preset_id):
            sql_statement = f"SELECT * FROM preset_{camera_id} where id={preset_id}"
            res = self.cursor.execute(sql_statement)
            results = res.fetchone()
            log.debug(results)
            return results
        else:
            error_message = f"Preset: {preset_id} does not exist for camera: {camera_id}."
            log.error(error_message)
            raise ValueError(error_message)


if  __name__ == "__main__":
    db = Database("test.db")
    db.connect_to_db()
