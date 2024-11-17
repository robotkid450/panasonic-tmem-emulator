import asyncio
import os

from fastapi import FastAPI, status, HTTPException

from panasonicAW import ip
from tstore import memDb


__version__ = "1.1s.1"

dataBaseFile = "emulator.db3"
apiHost = os.environ.get("API_HOST", "127.0.0.1")
apiPort = int(os.environ.get("API_PORT", 8004))


db = memDb.Database(dataBaseFile)
db.connect_to_db()

presetTempStorage = None


def get_camera_data(camera_id):
    camera = db.camera_get(camera_id)
    return camera

def local_get_reset(camera_id : int, preset_id : int):
    preset = db.preset_get(camera_id, preset_id)
    return preset

def get_ham_head(camera_id : int):
    cam_data = get_camera_data(camera_id)
    head = ip.Camera(cam_data[1])
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
    except:
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
    head = ip.Camera(address)
    try:
        preset_id_from_db, pos_start_x, pos_start_y, pos_end_x, pos_end_y, zoom_start, zoom_end, preset_speed = local_get_reset(camera_id, preset_id)
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
    head.position_set_absolute_with_speed(pos_start_x, pos_start_y, 59)
    await asyncio.sleep(0.2)
    head.zoom_set_absolute(zoom_start)
    await asyncio.sleep(1.5)
    head.position_set_absolute_with_speed(pos_end_x, pos_end_y, speed)
    
    return {"SUCCESS" : f"Calling preset {preset_id} for camera {camera_id}"}


@app.get("/api/preset/rec/start")
async def rec_start(camera_id : int):
    head = get_ham_head(camera_id)
    start_pos = head.position_query()
    await asyncio.sleep(0.2)
    start_zoom = head.zoom_query()
    global presetTempStorage 
    presetTempStorage = (start_pos, start_zoom)
    return {"position": start_pos}


@app.get("/api/preset/rec/end")
async def rec_end(camera_id : int, speed : str, preset_id :int = None ):
    head = get_ham_head(camera_id)
    end_pos = head.position_query()
    await asyncio.sleep(0.2)
    end_zoom = head.zoom_query()
    if preset_id is None:
        db.preset_create(camera_id, presetTempStorage[0][0], presetTempStorage[0][1], end_pos[0], end_pos[1], presetTempStorage[1], end_zoom, speed)
    else:
        if db.preset_exists(camera_id, preset_id):
            db.preset_update(camera_id, preset_id, presetTempStorage[0][0], presetTempStorage[0][1], end_pos[0], end_pos[1], presetTempStorage[1], end_zoom, speed)
        else:
            db.preset_create(camera_id, presetTempStorage[0][0], presetTempStorage[0][1], end_pos[0], end_pos[1], presetTempStorage[1], end_zoom, speed, preset_id)
    return {"SUCCESS" : "Preset recorded"}


if __name__ == "__main__":
    import uvicorn
    print(apiHost)
    print(apiPort)
    uvicorn.run(app, host=apiHost, port=apiPort)