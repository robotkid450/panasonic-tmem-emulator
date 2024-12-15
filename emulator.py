import asyncio
import os
import logging

from fastapi import FastAPI, status, HTTPException

from panasonicAW import ptzHead
from tstore import memDb

logger = logging.getLogger(__name__)
logging.getLogger("panasonicAW.ptzHead")

__version__ = "2.1.1"

dataBaseFile = "data/emulator.db3"
apiHost = os.environ.get("API_HOST", "127.00.1")
apiPort = int(os.environ.get("API_PORT", 8005))


db = memDb.Database(dataBaseFile)
db.connect_to_db()

class TemporaryPreset:
    def __init__(self, position_start_x : int = None, position_start_y : int = None, zoom_start : int = None,
        position_end_x : int = None, position_end_y : int = None, zoom_end : int = None, speed : int = None):
        
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

def dump_preset_data(position_start_x : int, position_start_y : int,
                  position_end_x : int, position_end_y : int,
                  zoom_start : int, zoom_end : int, speed : int,
                  camera_id : int = "NA", preset_id : int = "NA",):
    logger.debug("Preset Data:")
    logger.debug("Camera ID: {camera_id}".format(camera_id=camera_id))
    logger.debug("Preset ID: {preset_id}".format(preset_id=preset_id))
    logger.debug("Position start X: {position_start_x}".format(position_start_x=position_start_x))
    logger.debug("Position start Y: {position_start_y}".format(position_start_y=position_start_y))
    logger.debug("Position end X: {position_end_x}".format(position_end_x=position_end_x))
    logger.debug("Position end Y: {position_end_y}".format(position_end_y=position_end_y))
    logger.debug("Zoom start: {zoom_start}".format(zoom_start=zoom_start))
    logger.debug("Zoom end: {zoom_end}".format(zoom_end=zoom_end))
    logger.debug("Speed: {speed}".format(speed=speed))
    logger.debug("Preset Data END")
app = FastAPI()

@app.get("/api/test")
def test_func():
    logger.info("API Test function ran successfully")
    return {"message": "API Test function ran successfully"}

@app.get("/api/camera/add")
def camera_add(model : str, address: str, port = 80):
    logger.info("Attempting to add {model} at address {address}".format(model=model, address=address))
    try:
        db.camera_add(model.upper(), address, port)
    except ValueError:
        error_message = "Error camera already exists at {address}".format(address=address)
        logger.error(error_message)
        return {"Message": error_message}
    success_message = "Camera at {address} added successfully".format(address=address)
    logger.info(success_message)
    return {"SUCCESS": success_message}

@app.get("/api/camera/delete")
def camera_delete(camera_id : int):
    logger.info("Attempting to delete camera {camera_id}".format(camera_id=camera_id))
    try:
        db.camera_delete(camera_id)
    except ValueError:
        error_message = "Error camera {camera_id} does not exist".format(camera_id=camera_id)
        logger.error(error_message)
        return {"ERROR": error_message}
    success_message = "Camera {camera_id} deleted successfully".format(camera_id=camera_id)
    logger.info(success_message)
    return {"SUCCESS": success_message}

@app.get("/api/camera/list")
def cameras_list():
    cams = db.camera_list()
    logger.info("Listing cameras")
    logger.debug("List of cameras: {}".format(cams))
    return {"CAMERAS" : cams}

@app.get("/api/camera/get")
def camera_get(camera_id : int):
    logger.info("Attempting to get camera {camera_id}".format(camera_id=camera_id))
    if db.camera_exists(camera_id):
        cam = get_camera_data(camera_id)
        logger.info("Camera {camera_id} found".format(camera_id=camera_id))
        logger.info("Camera info: {}".format(cam))
        return {"camera" : cam}
    else:
        error_message = "Camera {camera_id} does not exist".format(camera_id=camera_id)
        logger.error(error_message)
        return  {"ERROR" : error_message}


@app.get("/api/preset/add")
def preset_add(camera_id : int, position_start_x: int, position_start_y: int, position_end_x: int, position_end_y: int,
               zoom_start : int, zoom_end : int, speed: int):
    logger.info("Adding preset to {camera_id}".format(camera_id=camera_id))
    dump_preset_data(position_start_x=position_start_x, position_start_y=position_start_y, position_end_x=position_end_x,
                     position_end_y=position_end_y, zoom_start=zoom_start, zoom_end=zoom_end,
                     camera_id=camera_id, speed=speed)
    try:
        db.preset_create(camera_id, position_start_x, position_start_y, position_end_x,
                         position_end_y, zoom_start, zoom_end, speed)
    except ValueError as e:
        error_message = e
        logger.error(error_message)
        return {"Error" : error_message}

    success_message = "Preset {camera_id} added successfully".format(camera_id=camera_id)
    logger.info(success_message)
    return {"SUCCESS": success_message}


@app.get("/api/preset/update")
def preset_update(camera_id : int, preset_id : int, position_start_x: int, position_start_y: int, position_end_x: int,
                position_end_y: int, zoom_start : int, zoom_end : int, speed: int):
    logger.info("Updating preset {camera_id}".format(camera_id=camera_id))
    dump_preset_data(position_start_x=position_start_x, position_start_y=position_start_y,
                     position_end_x=position_end_x, position_end_y=position_end_y,
                     zoom_start=zoom_start, zoom_end=zoom_end,speed=speed,
                     camera_id=camera_id,preset_id=preset_id)

    try:
        db.preset_update(camera_id=camera_id, preset_id=preset_id, position_start_x=position_start_x,
                         position_start_y=position_start_y, position_end_x= position_end_x,
                         position_end_y=position_end_y, zoom_start=zoom_start,
                         zoom_end=zoom_end,speed= speed)
    except ValueError:
        error_message = "Camera: {cam_id} or Preset: {preset_id} does not exist".format(cam_id=camera_id, preset_id=preset_id)
        logger.error(error_message)
        return {"ERROR" : error_message}
    success_message = "Preset {camera_id} updated successfully".format(camera_id=camera_id)
    logger.info(success_message)
    return {"SUCCESS" : success_message}

@app.get("/api/preset/delete")
def preset_delete(camera_id : int, preset_id : int):
    logger.info("Deleting preset {camera_id}".format(camera_id=camera_id))
    try:
        db.preset_delete(camera_id, preset_id)
    except ValueError:
        error_message = "Preset {preset_id} or camera {cam_id} does not exist.".format(
            preset_id=preset_id,cam_id=camera_id)
        logger.error(error_message)
        return {"ERROR" : error_message}
    success_message = "Preset {preset_id} for {cam_id} deleted successfully".format(
        preset_id=preset_id,cam_id=camera_id
    )
    logger.info(success_message)
    return {"SUCCESS" : success_message}

@app.get("/api/preset/get")
def preset_get(camera_id : int, preset_id : int):
    logger.info("Getting preset {preset_id} for {camera_id}".format(
        preset_id = preset_id,camera_id=camera_id))

    try:
        preset = db.preset_get(camera_id, preset_id)
    except ValueError as valError:
        logger.error(valError)
        return {"Error": valError}
    logger.info("Preset {preset_id} for {camera_id} retrieved".format(
        preset_id=preset_id,camera_id=camera_id))
    logger.debug("Preset info: {}".format(preset))
    return {"PRESET" : preset}

@app.get("/api/preset/call")
async def preset_call(camera_id : int, preset_id : int, speed = -1):
    preset_id_from_db, address, port, model = get_camera_data(camera_id)
    head = ptzHead.Camera(address, model)

    try:
        (preset_id_from_db, pos_start_x, pos_start_y, pos_end_x, pos_end_y, zoom_start, zoom_end,
            preset_speed) = local_get_preset(camera_id, preset_id)
    except:
        # return {"ERROR": "Preset or camera does not exist"}
        error_message = "Preset: {pre_id} or camera {cam_id} does not exist".format(pre_id=preset_id, cam_id=camera_id)
        logger.error(error_message)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"ERROR": error_message}
        )

    speed = int(speed)
    if speed == -1:
        speed = preset_speed

    dump_preset_data(preset_id=preset_id, camera_id=camera_id,
                     position_start_x=pos_start_x, position_start_y=pos_start_y,
                     position_end_x=pos_end_x, position_end_y=pos_end_y,
                     zoom_start=zoom_start,zoom_end=zoom_end,speed=speed)
    logger.info("Stopping Camera movment")
    head.pan_tilt_stop()
    await asyncio.sleep(0.3)
    logger.debug("Camera stopped")
    logger.debug("Moving to Start position")
    logger.debug("Starting position X:{x} Y:{y}".format(x=pos_start_x, y=pos_start_y))
    head.position_set_absolute_with_speed(pos_start_x, pos_start_y, max(head.speed_table))
    await asyncio.sleep(0.3)
    logger.info("Setting start Zoom")
    logger.debug("Starting Zoom:{zoom}".format(zoom=zoom_start))
    head.zoom_set_absolute(zoom_start)
    logger.debug("Zoom set")
    await asyncio.sleep(1.5)
    logger.info("Running Camera Movement")
    logger.debug("Camera moving to X:{x} Y:{y} at speed: {speed}".format(
        x=pos_end_x, y=pos_end_y, speed=speed))
    head.position_set_absolute_with_speed(pos_end_x, pos_end_y, speed)
    success_message = "Calling preset {preset_id} for camera {camera_id}".format(
        preset_id=preset_id,camera_id=camera_id)
    logger.info(success_message)
    return {"SUCCESS" : success_message}


@app.get("/api/preset/rec/start")
async def rec_start(camera_id : int):
    logger.info("Starting preset recording")
    global presetTempStorage
    presetTempStorage.clear_temp() # Clear out temp storage before starting recording
    head = get_cam_head(camera_id)
    presetTempStorage.position_start_x, presetTempStorage.position_start_y = head.position_query()
    logging.debug("Start position X:[{x} Y:{y}".format(
        x=presetTempStorage.position_start_x, y=presetTempStorage.position_start_y))
    await asyncio.sleep(0.2)
    presetTempStorage.zoom_start = head.zoom_query()
    logger.debug("Zoom Start: {zoom}".format(zoom=presetTempStorage.zoom_start))
    success_message = "{x}:{y}:{z}".format(
        x=presetTempStorage.position_start_x, y=presetTempStorage.position_start_y,z=presetTempStorage.zoom_start
    )

    return {"position x:y:z": success_message}


@app.get("/api/preset/rec/end")
async def rec_end(camera_id : int, speed : int, preset_id :int = None ):
    logger.info("Ending preset recording")
    head = get_cam_head(camera_id)
    position_end_x, position_end_y = head.position_query()
    await asyncio.sleep(0.2)
    zoom_end = head.zoom_query()
    global presetTempStorage
    presetTempStorage.position_end_x = position_end_x
    presetTempStorage.position_end_y = position_end_y
    presetTempStorage.zoom_end = zoom_end
    presetTempStorage.speed = speed
    dump_preset_data(preset_id=preset_id, camera_id=camera_id,
        position_start_x=presetTempStorage.position_start_x,
        position_start_y=presetTempStorage.position_start_y,
        position_end_x=presetTempStorage.position_end_x,
        position_end_y=presetTempStorage.position_end_y,
        zoom_start=presetTempStorage.zoom_start,
        zoom_end=presetTempStorage.zoom_end,
        speed=speed)

    if preset_id is None:
        logger.info("Creating preset for camera{id}".format(id=camera_id))
        db.preset_create(camera_id=camera_id,
                         position_start_x=presetTempStorage.position_start_x,
                         position_start_y=presetTempStorage.position_start_y,
                         position_end_x=presetTempStorage.position_end_x,
                         position_end_y=presetTempStorage.position_end_y,
                         zoom_start=presetTempStorage.zoom_start,
                         zoom_end=presetTempStorage.zoom_end,
                         speed=presetTempStorage.speed)
    else:
        if db.preset_exists(camera_id, preset_id):
            logger.info("Preset {preset_id} already exists".format(preset_id=preset_id))
            logger.info("Updating preset {preset_id}".format(preset_id=preset_id))
            db.preset_update(camera_id=camera_id,
                             preset_id=preset_id,
                             position_start_x=presetTempStorage.position_start_x,
                             position_start_y=presetTempStorage.position_start_y,
                             position_end_x=presetTempStorage.position_end_x,
                             position_end_y=presetTempStorage.position_end_y,
                             zoom_start=presetTempStorage.zoom_start,
                             zoom_end=presetTempStorage.zoom_end,
                             speed=presetTempStorage.speed)
        else:
            db.preset_create(camera_id=camera_id,
                             position_start_x=presetTempStorage.position_start_x,
                             position_start_y=presetTempStorage.position_start_y,
                             position_end_x=presetTempStorage.position_end_x,
                             position_end_y=presetTempStorage.position_end_y,
                             zoom_start=presetTempStorage.zoom_start,
                             zoom_end=presetTempStorage.zoom_end,
                             speed=presetTempStorage.speed,
                             preset_id=preset_id)
    return {"SUCCESS" : "Preset recorded"}


if __name__ == "__main__":
    import uvicorn
    os.makedirs("data", exist_ok=True)
    logging.basicConfig(level=logging.DEBUG, filename="./data/panasonicAW.log")
    uvicorn.run(app, host=apiHost, port=apiPort)