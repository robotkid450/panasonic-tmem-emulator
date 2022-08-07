#!python

import sys
import pickle
from panasonicAW import ip
from tstore import tmem
from tstore import dataStore

#path of tmem storage file
TmemStore = "tmems.pickle"

headAddr = "localhost:8000"

def getPosition():
    print("get position")
    pos = head.queryPosition()
    return pos

def tmemAdd():
    print("adding TMEM")
    print("Position starting key frame, then press ENTER.")
    input()
    startPos = (0,0)
    #startPos = head.queryPosition()
    #startZoom = head.queryZoom()
    print("Position ending keyframe, the press ENTER.")
    input()
    #endPos = head.queryPosition()
    endPos = (100, 100)
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

def tmemPlay(args):
    print("playTmem")
    print(args)



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
    tmemPlay(args)

elif userCommand == 'list':
    tmemList()

elif userCommand == 'del':
    tmem_to_delete = int(userCommandArgs.pop())
    tmemDel(tmem_to_delete)
else:
    print("ERROR: Invalid command")
