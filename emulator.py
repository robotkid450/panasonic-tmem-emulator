import asyncio
import os
import logging
import time

from fastapi import FastAPI, status, HTTPException

from panasonicAW import ptzHead
from tstore import memDb

logger = logging.getLogger(__name__)
logging.getLogger("panasonicAW.ptzHead")
logging.getLogger("tstore.memDb")

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

file_handler = logging.FileHandler('data/panasonicAW.log')

console_handler = logging.StreamHandler()




__version__ = "2.2.2"

os.makedirs("data", exist_ok=True)
dataBaseFile = "data/emulator.db3"
apiHost = os.environ.get("API_HOST", "127.0.0.1")
apiPort = int(os.environ.get("API_PORT", 8005))
debugMode = os.environ.get("DEBUG", "FALSE")

camera_move_timeout = 240 #must be longer than the longest single move


db = memDb.Database(dataBaseFile)
db.connect_to_db()

loop_futures = {}


class TemporaryPreset:
    def __init__(self, position_start_x : str = None, position_start_y : str = None, zoom_start : str = None,
        position_end_x : str = None, position_end_y : str = None, zoom_end : str = None, speed : int = None):
        
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

def dump_preset_data(position_start_x : str, position_start_y : str,
                  position_end_x : str, position_end_y : str,
                  zoom_start : str, zoom_end : str, speed : int,
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
def preset_add(camera_id : int, position_start_x: str, position_start_y: str, position_end_x: str, position_end_y: str,
               zoom_start : str, zoom_end : str, speed: int):
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
def preset_update(camera_id : int, preset_id : int, position_start_x: str, position_start_y: str, position_end_x: str,
                position_end_y: str, zoom_start : str, zoom_end : str, speed: int):
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
async def preset_call(camera_id : int, preset_id : int, speed = -1, loop: bool = False):
    if camera_id in loop_futures:
        loop_futures[camera_id].cancel()

    if loop:
        coro = local_call_preset_loop(camera_id, preset_id, speed)
    else:
        coro = local_call_prest(camera_id, preset_id, speed)

    try:

        future = asyncio.ensure_future(coro)
        if loop:
            loop_futures[camera_id] = future

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"ERROR": str(e)}
        )
    except TimeoutError as e:
        raise HTTPException(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            detail={"ERROR": str(e)}
        )

    success_message = "Calling preset {preset_id} for camera {camera_id}".format(
        preset_id=preset_id,
        camera_id=camera_id
    )
    logger.info(success_message)
    return {"SUCCESS" : success_message}


@app.get("/api/loop/stop")
async def loop_stop(camera_id : int):
    if camera_id in loop_futures:
        loop_futures[camera_id].cancel()
        head = get_cam_head(camera_id)
        await asyncio.sleep(0.15)
        head.pan_tilt_stop()
        await asyncio.sleep(0.15)
        head.zoom_stop()
    return {"SUCCESS": "Loop stopped for camera {}".format(camera_id)}

@app.get("/api/loop/stopAll")
async def loop_stop_all():
    for camera_id in loop_futures:
        loop_futures[camera_id].cancel()
        head = get_cam_head(camera_id)
        await asyncio.sleep(0.15)
        head.pan_tilt_stop()
        await asyncio.sleep(0.15)
        head.zoom_stop()

    return {"SUCCESS": "Loop stopped for all cameras"}


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
    logger.info("Starting End preset recording")
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


async def local_call_preset_loop(camera_id : int, preset_id : int, speed = -1):
    logger.info("Starting loop for preset {preset_id}".format(preset_id=preset_id))
    while camera_id in loop_futures:
        logger.info("moving forward")
        await local_call_prest(camera_id=camera_id, preset_id=preset_id, speed=speed, reverse=False)
        logger.info("moving backward")
        await local_call_prest(camera_id=camera_id, preset_id=preset_id, speed=speed, reverse=True)





async def local_call_prest(camera_id : int, preset_id : int, speed = -1, reverse=False):
    preset_id_from_db, address, port, model = get_camera_data(camera_id)
    head = ptzHead.Camera(address, model)

    try:
        (preset_id_from_db, pos_start_x, pos_start_y, pos_end_x, pos_end_y, zoom_start, zoom_end,
         preset_speed) = local_get_preset(camera_id, preset_id)
    except:
        # return {"ERROR": "Preset or camera does not exist"}
        error_message = "Preset: {pre_id} or camera {cam_id} does not exist".format(pre_id=preset_id, cam_id=camera_id)
        logger.error(error_message)
        raise ValueError(error_message)

    speed = int(speed)
    if speed == -1:
        speed = preset_speed

    if reverse is True:
        logger.info("Reversing preset {preset_id}".format(preset_id=preset_id))
        temp_pos_start_x = pos_start_x
        temp_pos_start_y = pos_start_y
        temp_zoom_start = zoom_start
        temp_pos_end_x = pos_end_x
        temp_pos_end_y = pos_end_y
        temp_zoom_end = zoom_end

        pos_start_x = temp_pos_end_x
        pos_start_y = temp_pos_end_y
        zoom_start = temp_zoom_end
        pos_end_x = temp_pos_start_x
        pos_end_y = temp_pos_start_y
        zoom_end = temp_zoom_start

    dump_preset_data(preset_id=preset_id, camera_id=camera_id,
                     position_start_x=pos_start_x, position_start_y=pos_start_y,
                     position_end_x=pos_end_x, position_end_y=pos_end_y,
                     zoom_start=zoom_start, zoom_end=zoom_end, speed=speed)

    logger.debug("Moving to Start position")
    logger.debug("Starting position X:{x} Y:{y}".format(x=pos_start_x, y=pos_start_y))
    head.position_set_absolute_with_speed(pos_start_x, pos_start_y, max(head.speed_table))
    await asyncio.sleep(0.15)
    logger.debug("Starting Zoom:{zoom}".format(zoom=zoom_start))
    head.zoom_set_absolute(zoom_start)
    # await asyncio.sleep(1.5)
    # moving_to_position : bool = True
    await local_wait_for_move(head=head,target_x=pos_start_x, target_y=pos_start_y, target_zoom=zoom_start, timeout=5)

    await asyncio.sleep(0.15)
    logger.info("Running Camera Movement")
    logger.debug("Camera moving to X:{x} Y:{y} at speed: {speed}".format(
        x=pos_end_x, y=pos_end_y, speed=speed))
    head.position_set_absolute_with_speed(pos_end_x, pos_end_y, speed)
    success_message = "Calling preset {preset_id} for camera {camera_id}".format(
        preset_id=preset_id, camera_id=camera_id)
    logger.info(success_message)
    logger.debug("Waiting for preset movment to complete")
    await asyncio.sleep(0.15)
    await local_wait_for_move(head, target_x=pos_end_x, target_y=pos_end_y, target_zoom=zoom_end)
    return {"SUCCESS": success_message}


async def local_wait_for_move(head, target_x, target_y, target_zoom, timeout = camera_move_timeout):
    target_reached: bool = False
    zoom_change_completed: bool = False
    position_change_completed: bool = False
    x_change_complete: bool = False
    y_change_complete: bool = False
    call_exec_start_time = time.time()
    logger.info("Waiting for Camera Movement")
    logger.debug("Moving to target X:{x} Y:{y} Z:{z}".format(x=target_x, y=target_y,z=target_zoom))
    while not target_reached:
        if not position_change_completed:
            await asyncio.sleep(0.25)
            current_x, current_y = head.position_query()
            logger.debug("position query")
        if not zoom_change_completed:
            await asyncio.sleep(0.25)
            current_zoom = head.zoom_query()
            logger.debug("zoom query")
        logger.info("Target position x:{x} y:{y} z:{z}".format(x=target_x, y=target_y, z=target_zoom))
        logger.info("Current Position X:{x} Y:{y} z:{z}".format(x=current_x, y=current_y,z=current_zoom))

        x_diff = abs(target_x - current_x)
        y_diff = abs(target_y - current_y)

        if x_diff <= 3:
            x_change_complete = True

        if y_diff <= 3:
            y_change_complete = True

        if x_change_complete and y_change_complete:
            position_change_completed = True

        if abs((target_zoom - current_zoom)) <= 4:
            zoom_change_completed = True

        if position_change_completed:
            if zoom_change_completed:
                target_reached = True

        logger.debug("Waiting on head to finish move for {} seconds.".format(time.time() - call_exec_start_time))
        if time.time() - call_exec_start_time >= timeout:
            error_message = "Timeout moving to target {x}:{y}:{z}".format(x=target_x, y=target_y,z=target_zoom)
            logger.error(error_message)
            raise TimeoutError(error_message)
    logger.info("Camera Movement Completed")
    return


if __name__ == "__main__":
    import uvicorn

    if debugMode == "True":
        logger.setLevel(logging.DEBUG)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
    else:
        logger.setLevel(logging.INFO)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.info("Starting Panasonic Emulator")
    logger.debug("Running in debug mode")
    uvicorn.run(app, host=apiHost, port=apiPort)
    logger.info("Stopping Panasonic Emulator")