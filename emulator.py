from fastapi import FastAPI

from panasonicAW import ip
# from tstore import tmem
from tstore import dataStore
import time

TmemStore = "tmems.pickle"

headAddr = "192.168.1.150"

head = ip.camera(headAddr)

tmem_data_store = dataStore.dataStore(TmemStore)
tmem_data_store.loadPickle()
tmems = tmem_data_store.tmems


app = FastAPI()

@app.get("/api/test")
def testfunc():
    return {"message": "test"}

@app.get("/api/nom")
def nomfunc():
    return {"message": "nom"}

@app.get("/api/play")
def playfunc():
    id=0
    head.setPosABSSpeed(tmems[id].pos_start[0], tmems[id].pos_start[1], "1D", "2")
    time.sleep(1)
    head.setPosABSSpeed(tmems[id].pos_end[0], tmems[id].pos_end[1], "0F", "0")
    return {"message": "play"}

@app.get("/api/play2")
def play3func():
    id=1
    head.setPosABSSpeed(tmems[id].pos_start[0], tmems[id].pos_start[1], "1D", "2")
    time.sleep(1)
    head.setPosABSSpeed(tmems[id].pos_end[0], tmems[id].pos_end[1], "0F", "0")
    return {"message": "play2"}


@app.get("/api/callPreset")
def callPreset(preset : int):
    id = preset
    head.setPosABSSpeed(tmems[id].pos_start[0], tmems[id].pos_start[1], "1D", "2")
    time.sleep(1)
    head.setPosABSSpeed(tmems[id].pos_end[0], tmems[id].pos_end[1], "0F", "0")
    return {f"message: preset {id}"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)