import asyncio
import os

from fastapi import FastAPI, status, HTTPException

from panasonicAW import ptzHead
from tstore import memDb


__version__ = "1.1s.1"

dataBaseFile = "emulator.db3"
apiHost = os.environ.get("API_HOST", "127.0.0.1")
apiPort = int(os.environ.get("API_PORT", 8005))


db = memDb.Database(dataBaseFile)
db.connect_to_db()

class TemporaryPreset:
    # def __init__(self, position_start_x : int = None, position_start_y : int = None, zoom_start : int = None,
    #   position_end_x : int = None, position_end_y : int = None, zoom_end : int = None, speed : int = None):
    def __init__(self, position_start_x = None, position_start_y = None, zoom_start = None,
        position_end_x = None, position_end_y = None, zoom_end = None, speed = None):

        self.position_start_x = position_start_x
        self.position_start_y = position_start_y
        self.zoom_start = zoom_start
        self.position_end_x = position_end_x
        self.position_end_y = position_end_y
        self.zoom_end = zoom_end
        self.speed = speed

    def clear_temp(self):
        self.position_start_x = None
        self.position_start_y = None
        self.zoom_start = None
        self.position_end_x = None
        self.position_end_y = None
        self.zoom_end = None
        self.speed = None

presetTempStorage = TemporaryPreset()

def get_camera_data(camera_id):
    camera = db.camera_get(camera_id)
    return camera

def local_get_preset(camera_id : int, preset_id : int):
    preset = db.preset_get(camera_id, preset_id)
    return preset

def get_cam_head(camera_id : int):
    cam_data = get_camera_data(camera_id)
    head = ptzHead.Camera(cam_data[1])
    return head
        

app = FastAPI()

@app.get("/api/test")
def test_func():
    return {"message": "test"}

@app.get("/api/camera/add")
def camera_add(model : str, address: str, port = 80):
    try:
        db.camera_add(model, address, port)
    except ValueError:
        return {"Message": f"Error camera already exists at {address}"}
    return {"SUCCESS": f"Camera at {address} added"}

@app.get("/api/camera/delete")
def camera_delete(camera_id : int):
    try:
        db.camera_delete(camera_id)
    except ValueError:
        return {"ERROR": f"No camera defined for id {camera_id}"}
    
    return {"SUCCESS": f"Camera {camera_id} deleted."}

@app.get("/api/camera/list")
def cameras_list():
    cams = db.camera_list()
    return {"CAMERAS" : cams}

@app.get("/api/camera/get")
def camera_get(camera_id : int):
    if db.camera_exists(camera_id):
        cam = get_camera_data(camera_id)
        return {"camera" : cam}
    else:
        return  {"ERROR" : "No camera defined"}


@app.get("/api/preset/add")
def preset_add(camera_id : int, position_start_x: str, position_start_y: str, position_end_x: str, position_end_y: str, zoom_start : str, zoom_end : str, speed: str):
    try:
        db.preset_create(camera_id, position_start_x, position_start_y, position_end_x, position_end_y, zoom_start, zoom_end, speed)
    except ValueError:
        return {"Error" : f"No camera defined at {camera_id}"}
    return {"SUCCESS": F"Preset created for camera {camera_id}"}


@app.get("/api/preset/update")
def preset_update(camera_id : int, preset_id : int, position_start_x: str, position_start_y: str, position_end_x: str, position_end_y: str, zoom_start : str, zoom_end : str, speed: str):
    try:
        db.preset_update(camera_id, preset_id, position_start_x, position_start_y, position_end_x, position_end_y, zoom_start, zoom_end, speed)
    except ValueError:
        return {"ERROR" : f"Camera or preset provided does not exist."}
    return {"SUCCESS" : f"Preset ({preset_id}) for camera ({camera_id}) has been updated."}

@app.get("/api/preset/delete")
def preset_delete(camera_id : int, preset_id : int):
    try:
        db.preset_delete(camera_id, preset_id)
    except ValueError:
        return {"ERROR" : f"Preset {preset_id} or camera {camera_id} does not exist."}
    return {"SUCCESS" : f"Preset deleted from {camera_id}"}

@app.get("/api/preset/get")
def preset_get(camera_id : int, preset_id : int):
    try:
        preset = db.preset_get(camera_id, preset_id)
    except ValueError as valError:
        return {"Error": valError}
    return {"PRESET" : preset}

@app.get("/api/preset/call")
async def preset_call(camera_id : int, preset_id : int, speed = -1):
    preset_id_from_db, address, port, model = get_camera_data(camera_id)
    head = ptzHead.Camera(address, model)
    try:
        preset_id_from_db, pos_start_x, pos_start_y, pos_end_x, pos_end_y, zoom_start, zoom_end, preset_speed = local_get_preset(camera_id, preset_id)
    except:
        # return {"ERROR": "Preset or camera does not exist"}
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"ERROR": "Preset or camera does not exist"}
        )
    speed = int(speed)
    if speed == -1:
        speed = preset_speed

    head.pan_tilt_stop()
    await asyncio.sleep(0.2)
    head.position_set_absolute_with_speed_hex(pos_start_x, pos_start_y, 59)
    await asyncio.sleep(0.2)
    head.zoom_set_absolute_hex(zoom_start)
    await asyncio.sleep(1.5)
    head.position_set_absolute_with_speed_hex(pos_end_x, pos_end_y, speed)
    
    return {"SUCCESS" : f"Calling preset {preset_id} for camera {camera_id}"}


@app.get("/api/preset/rec/start")
async def rec_start(camera_id : int):
    global presetTempStorage
    presetTempStorage.clear_temp() # Clear out temp storage before starting recording
    head = get_cam_head(camera_id)
    presetTempStorage.position_start_x, presetTempStorage.position_start_y = head.position_query_hex()
    await asyncio.sleep(0.2)
    presetTempStorage.zoom_start = head.zoom_query_hex()

    return {"position x:y:z": f"{presetTempStorage.position_start_x}:{presetTempStorage.position_start_y}:{presetTempStorage.zoom_start}"}


@app.get("/api/preset/rec/end")
async def rec_end(camera_id : int, speed : str, preset_id :int = None ):
    head = get_cam_head(camera_id)
    position_end_x, position_end_y = head.position_query_hex()
    await asyncio.sleep(0.2)
    zoom_end = head.zoom_query_hex()
    global presetTempStorage
    presetTempStorage.position_end_x = position_end_x
    presetTempStorage.position_end_y = position_end_y
    presetTempStorage.zoom_end = zoom_end
    presetTempStorage.speed = speed

    if preset_id is None:
        db.preset_create(camera_id,
                         presetTempStorage.position_start_x,
                         presetTempStorage.position_start_y,
                         presetTempStorage.position_end_x,
                         presetTempStorage.position_end_y,
                         presetTempStorage.zoom_start,
                         presetTempStorage.zoom_end,
                         presetTempStorage.speed)
    else:
        if db.preset_exists(camera_id, preset_id):
            db.preset_update(camera_id,
                             preset_id,
                             presetTempStorage.position_start_x,
                             presetTempStorage.position_start_y,
                             presetTempStorage.position_end_x,
                             presetTempStorage.position_end_y,
                             presetTempStorage.zoom_start,
                             presetTempStorage.zoom_end,
                             presetTempStorage.speed)
        else:
            db.preset_create(camera_id,
                             presetTempStorage.position_start_x,
                             presetTempStorage.position_start_y,
                             presetTempStorage.position_end_x,
                             presetTempStorage.position_end_y,
                             presetTempStorage.zoom_start,
                             presetTempStorage.zoom_end,
                             presetTempStorage.speed,
                             preset_id)
    return {"SUCCESS" : "Preset recorded"}


if __name__ == "__main__":
    import uvicorn
    print(apiHost)
    print(apiPort)
    uvicorn.run(app, host=apiHost, port=apiPort)