from fastapi import FastAPI, status, HTTPException

from panasonicAW import ip
from tstore import memDb
import asyncio

dataBaseFile = "emulator.db3"
apiHost = "0.0.0.0"
apiPort = 8005

db = memDb.Database(dataBaseFile)
db.connectToDb()

presetTempStorage = None


def getCameraData(camera_id):
    camera = db.getCamera(camera_id)
    return camera

def localGetPreset(camera_id : int, preset_id : int):
    preset = db.getPreset(camera_id, preset_id)
    return preset

def getCamHead(camera_id : int):
    camData = getCameraData(camera_id)
    head = ip.camera(camData[1])
    return head
        

app = FastAPI()

@app.get("/api/test")
def testfunc():
    return {"message": "test"}

@app.get("/api/camera/add")
def addCamera(model : str, address: str, port = 80):
    try:
        db.addCamera(model, address, port)
    except ValueError:
        return {"Message": f"Error camera already exists at {address}"}
    return {"SUCCESS": f"Camera at {address} added"}

@app.get("/api/camera/delete")
def deleteCamera(id : int):
    try:
        db.deleteCamera(id)
    except ValueError:
        return {"ERROR": f"No camera defined for id {id}"}
    
    return {"SUCCESS": f"Camera {id} deleted."}

@app.get("/api/camera/list")
def listCameras():
    cams = db.getCameras()
    return {"CAMERAS" : cams}

@app.get("/api/camera/get")
def getCamera(Camera_id : int):
    if db.checkCameraExists(Camera_id):
        cam = getCameraData(Camera_id)
        return {"camera" : cam}
    else:
        return  {"ERROR" : "No camera defined"}


@app.get("/api/preset/add")
def addPreset(camera_id : int, position_start_x: str, position_start_y: str, position_end_x: str, position_end_y: str, zoom_start : str, zoom_end : str, speed: str):
    try:
        db.createPreset(camera_id, position_start_x, position_start_y, position_end_x, position_end_y, zoom_start, zoom_end, speed)
    except ValueError:
        return {"Error" : f"No camera defined at {camera_id}"}
    return {"SUCCESS": F"Preset created for camera {camera_id}"}


@app.get("/api/preset/update")
def updatePreset(camera_id : int, preset_id : int, position_start_x: str, position_start_y: str, position_end_x: str, position_end_y: str, zoom_start : str, zoom_end : str, speed: str):
    try:
        db.updatePreset(camera_id, preset_id, position_start_x, position_start_y, position_end_x, position_end_y, zoom_start, zoom_end, speed)
    except:
        return {"ERROR" : f"Camera or preset provided does not exist."}
    return {"SUCCESS" : f"Preset ({preset_id}) for camera ({camera_id}) has been updated."}

@app.get("/api/preset/delete")
def deletePreset(camera_id : int, preset_id : int):
    try:
        db.deletePreset(camera_id, preset_id)
    except ValueError:
        return {"ERROR" : f"Preset {preset_id} or camera {camera_id} does not exist."}
    return {"SUCCESS" : f"Preset deleted from {camera_id}"}

@app.get("/api/preset/get")
def getPreset(camera_id : int, preset_id : int):
    try:
        preset = db.getPreset(camera_id, preset_id)
    except ValueError as valError:
        return {"Error": valError}
    return {"PRESET" : preset}

@app.get("/api/preset/call")
async def callPreset(camera_id : int, preset_id : int, speed = -1):
    id, addess, port, model = getCameraData(camera_id)
    head = ip.camera(addess)
    try:
        id, pos_start_x, pos_start_y, pos_end_x, pos_end_y, zoom_start, zoom_end, preset_speed = localGetPreset(camera_id, preset_id)
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
async def recStart(camera_id : int):
    head = getCamHead(camera_id)
    startPos = head.queryPosition()
    await asyncio.sleep(0.2)
    startZoom = head.queryZoom()
    global presetTempStorage 
    presetTempStorage = (startPos, startZoom)
    return {"position": startPos}


@app.get("/api/preset/rec/end")
async def recEnd(camera_id : int, speed : str, preset_id :int = None ):
    head = getCamHead(camera_id)
    endPos = head.queryPosition()
    await asyncio.sleep(0.2)
    endZoom = head.queryZoom()
    if preset_id == None:
        db.createPreset(camera_id, presetTempStorage[0][0], presetTempStorage[0][1], endPos[0], endPos[1], presetTempStorage[1], endZoom, speed )
    else:
        if db.checkPresetExists(camera_id, preset_id):
            db.updatePreset(camera_id, preset_id, presetTempStorage[0][0], presetTempStorage[0][1], endPos[0], endPos[1], presetTempStorage[1], endZoom, speed)
        else:
            db.createPreset(camera_id, presetTempStorage[0][0], presetTempStorage[0][1], endPos[0], endPos[1], presetTempStorage[1], endZoom, speed, preset_id)
    return {"SUCCESS" : "Preset recorded"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=apiHost, port=apiPort)