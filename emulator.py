from fastapi import FastAPI

from panasonicAW import ip
# from tstore import tmem
from tstore import dataStore
from tstore import memDb
import time

dataBaseFile = "emulator.db3"

TmemStore = "tmems.pickle"

headAddr = "192.168.1.150"

# head = ip.camera(headAddr)

# tmem_data_store = dataStore.dataStore(TmemStore)
# tmem_data_store.loadPickle()
# tmems = tmem_data_store.tmems

db = memDb.Database(dataBaseFile)
db.connectToDb()


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
    cams = db.listCameras()
    return {"CAMERAS" : cams}

@app.get("/api/camera/get")
def getCamera(Camera_id : int):
    if db.checkCameraExists(Camera_id):
        pass #TODO write camera getter in memDB


@app.get("/api/preset/add")
def addPreset(camera_id : int, position_start: str, position_end: str, zoom_start : str, zoom_end : str, speed: str):
    try:
        db.createPreset(camera_id, position_start, position_end, zoom_start, zoom_end, speed)
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

@app.get("/api/preset/call")
def callPreset(camera_id : int, preset_id : int):
    pass


# @app.get("/api/callPreset")
# def callPreset(camera : int, preset : int):
    # id = preset
    # head.setPosABSSpeed(tmems[id].pos_start[0], tmems[id].pos_start[1], "1D", "2")
    # time.sleep(1)
    # head.setPosABSSpeed(tmems[id].pos_end[0], tmems[id].pos_end[1], "0F", "0")
    # return {f"message: preset {id}"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)