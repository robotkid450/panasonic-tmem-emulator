from fastapi import FastAPI, status, HTTPException

from panasonicAW import ip
from tstore import memDb
import asyncio

__version__ = "1.0.1"

dataBaseFile = "emulator.db3"
apiHost = "0.0.0.0"
apiPort = 8004

db = memDb.Database(dataBaseFile)
db.connectToDb()

presetTempStorage = None


def get_camera_data(camera_id):
    camera = db.getCamera(camera_id)
    return camera

def local_get_reset(camera_id : int, preset_id : int):
    preset = db.getPreset(camera_id, preset_id)
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
        db.addCamera(model, address, port)
    except ValueError:
        return {"Message": f"Error camera already exists at {address}"}
    return {"SUCCESS": f"Camera at {address} added"}

@app.get("/api/camera/delete")
def camera_delete(camera_id : int):
    try:
        db.deleteCamera(camera_id)
    except ValueError:
        return {"ERROR": f"No camera defined for id {camera_id}"}
    
    return {"SUCCESS": f"Camera {camera_id} deleted."}

@app.get("/api/camera/list")
def cameras_list():
    cams = db.getCameras()
    return {"CAMERAS" : cams}

@app.get("/api/camera/get")
def camera_get(camera_id : int):
    if db.checkCameraExists(camera_id):
        cam = get_camera_data(camera_id)
        return {"camera" : cam}
    else:
        return  {"ERROR" : "No camera defined"}


@app.get("/api/preset/add")
def preset_add(camera_id : int, position_start_x: str, position_start_y: str, position_end_x: str, position_end_y: str, zoom_start : str, zoom_end : str, speed: str):
    try:
        db.createPreset(camera_id, position_start_x, position_start_y, position_end_x, position_end_y, zoom_start, zoom_end, speed)
    except ValueError:
        return {"Error" : f"No camera defined at {camera_id}"}
    return {"SUCCESS": F"Preset created for camera {camera_id}"}


@app.get("/api/preset/update")
def preset_update(camera_id : int, preset_id : int, position_start_x: str, position_start_y: str, position_end_x: str, position_end_y: str, zoom_start : str, zoom_end : str, speed: str):
    try:
        db.updatePreset(camera_id, preset_id, position_start_x, position_start_y, position_end_x, position_end_y, zoom_start, zoom_end, speed)
    except:
        return {"ERROR" : f"Camera or preset provided does not exist."}
    return {"SUCCESS" : f"Preset ({preset_id}) for camera ({camera_id}) has been updated."}

@app.get("/api/preset/delete")
def preset_delete(camera_id : int, preset_id : int):
    try:
        db.deletePreset(camera_id, preset_id)
    except ValueError:
        return {"ERROR" : f"Preset {preset_id} or camera {camera_id} does not exist."}
    return {"SUCCESS" : f"Preset deleted from {camera_id}"}

@app.get("/api/preset/get")
def preset_get(camera_id : int, preset_id : int):
    try:
        preset = db.getPreset(camera_id, preset_id)
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

    head.moveStop()
    await asyncio.sleep(0.2)
    head.setPosABSSpeed(pos_start_x, pos_start_y, 59)
    await asyncio.sleep(0.2)
    head.setZoomABS(zoom_start)
    await asyncio.sleep(1.5)
    head.setPosABSSpeed(pos_end_x, pos_end_y, speed)
    
    return {"SUCCESS" : f"Calling preset {preset_id} for camera {camera_id}"}


@app.get("/api/preset/rec/start")
async def rec_start(camera_id : int):
    head = get_ham_head(camera_id)
    start_pos = head.queryPosition()
    await asyncio.sleep(0.2)
    start_zoom = head.queryZoom()
    global presetTempStorage 
    presetTempStorage = (start_pos, start_zoom)
    return {"position": start_pos}


@app.get("/api/preset/rec/end")
async def rec_end(camera_id : int, speed : str, preset_id :int = None ):
    head = get_ham_head(camera_id)
    end_pos = head.queryPosition()
    await asyncio.sleep(0.2)
    end_zoom = head.queryZoom()
    if preset_id is None:
        db.createPreset(camera_id, presetTempStorage[0][0], presetTempStorage[0][1], end_pos[0], end_pos[1], presetTempStorage[1], end_zoom, speed )
    else:
        if db.checkPresetExists(camera_id, preset_id):
            db.updatePreset(camera_id, preset_id, presetTempStorage[0][0], presetTempStorage[0][1], end_pos[0], end_pos[1], presetTempStorage[1], end_zoom, speed)
        else:
            db.createPreset(camera_id, presetTempStorage[0][0], presetTempStorage[0][1], end_pos[0], end_pos[1], presetTempStorage[1], end_zoom, speed, preset_id)
    return {"SUCCESS" : "Preset recorded"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=apiHost, port=apiPort)