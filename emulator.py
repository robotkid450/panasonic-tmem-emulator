from fastapi import FastAPI

from panasonicAW import ip
# from tstore import tmem
from tstore import dataStore
from tstore import memDb
import time
import asyncio

dataBaseFile = "emulator.db3"

TmemStore = "tmems.pickle"

headAddr = "192.168.1.150"

# head = ip.camera(headAddr)

# tmem_data_store = dataStore.dataStore(TmemStore)
# tmem_data_store.loadPickle()
# tmems = tmem_data_store.tmems

speeds = {
    "0" : ("1D", "2"),
    "1" : ("05", "0"),
    "2" : ("0A", "0"),
    "3" : ("0F", "0"),
    "4" : ("05", "1"),
    "5" : ("0A", "1"),
    "6" : ("0F", "1"),

 }


db = memDb.Database(dataBaseFile)
db.connectToDb()

presetTempStorage = None


def getCameraData(camera_id):
    camera = db.getCamera(camera_id)
    # print(camera)
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

@app.get("/api/preset/delete")
def deletePreset(camera_id : int, preset_id : int):
    try:
        db.deletePreset(camera_id, preset_id)
    except ValueError:
        return {"ERROR" : f"Preset {preset_id} or camera {camera_id} does not exist."}
    return {"SUCCESS" : f"Preset deleted from {camera_id}"}

@app.get("/api/preset/get")
def getPreset(camera_id : int, preset_id : int):
    preset = db.getPreset(camera_id, preset_id)
    return {"PRESET" : preset}

@app.get("/api/preset/call")
def callPreset(camera_id : int, preset_id : int):
    camData = getCameraData(camera_id)
    head = ip.camera(camData[1])
    try:
        id, pos_start_x, pos_start_y, pos_end_x, pos_end_y, zoom_start, zoom_end, speed = localGetPreset(camera_id, preset_id)
    except:
        return {"ERROR": "Preset or camera does not exist"}
    head.setPosABSSpeed(pos_start_x, pos_start_y, speeds["0"][0], speeds["0"][1])
    time.sleep(1)
    head.setPosABSSpeed(pos_end_x, pos_end_y, speeds[speed][0], speeds[speed][1])


@app.get("/api/preset/rec/start")
def recStart(camera_id : int):
    head = getCamHead(camera_id)
    startPos = head.queryPosition()
    global presetTempStorage 
    presetTempStorage = (startPos, None)
    return {"position": startPos}


@app.get("/api/preset/rec/end")
def recEnd(camera_id : int, speed : str):
    head = getCamHead(camera_id)
    endPos = head.queryPosition()
    db.createPreset(camera_id, presetTempStorage[0][0], presetTempStorage[0][1], endPos[0], endPos[1], 0, 0, speed )
    


    


# @app.get("/api/callPreset")
# def callPreset(camera : int, preset : int):
    # id = preset
    # head.setPosABSSpeed(tmems[id].pos_start[0], tmems[id].pos_start[1], "1D", "2")
    # time.sleep(1)
    # head.setPosABSSpeed(tmems[id].pos_end[0], tmems[id].pos_end[1], "0F", "0")
    # return {f"message: preset {id}"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8005)