#!python

import sys
import pickle
import time
from panasonicAW import ip
from tstore import tmem
from tstore import dataStore

#proof of concept for camera control

#path of tmem storage file
TmemStore = "tmems.pickle"

headAddr = "192.168.1.150"

def getPosition():
    print("get position")
    pos = head.queryPosition()
    return pos

def tmemAdd():
    print("adding TMEM")
    print("Position starting key frame, then press ENTER.")
    input()
    #startPos = (0,0)
    startPos = head.queryPosition()
    # startZoom = head.queryZoom()
    print("Position ending keyframe, the press ENTER.")
    input()
    endPos = head.queryPosition()
    #endPos = (100, 100)
    print("Please enter period to run in seconds")
    runtime = input()
    mem = tmem.tmem()
    mem.setPosStart(startPos)
    mem.setPosEnd(endPos)
    mem.setRunTime(int(runtime))
    tmem_data_store.tmemAdd(mem)
    tmem_data_store.savePickle()
    input()

def tmemList():
    for item in tmems:
        print(item.id)

def tmemDel(id):
    tmem_data_store.removeTmem(id)
    tmem_data_store.savePickle()

def tmemPlay(id):
    print("playTmem")
    print(id)
    print(tmems[0].pos_start)
    head.setPosABSSpeed(tmems[id].pos_start[0], tmems[id].pos_start[1], "1D", "2")
    time.sleep(1)
    head.setPosABSSpeed(tmems[id].pos_end[0], tmems[id].pos_end[1], "0F", "0")



head = ip.camera(headAddr)

args = sys.argv

args.pop(0) #discard script name

userCommand = str(args.pop(0))

userCommandArgs = args

tmem_data_store = dataStore.dataStore(TmemStore)
tmem_data_store.loadPickle()
tmems = tmem_data_store.tmems



if userCommand == 'add':
    tmemAdd()
elif userCommand == 'play':
    tmem_to_play = int(userCommandArgs.pop())
    tmemPlay(tmem_to_play)

elif userCommand == 'list':
    tmemList()

elif userCommand == 'del':
    tmem_to_delete = int(userCommandArgs.pop())
    tmemDel(tmem_to_delete)
else:
    print("ERROR: Invalid command")
