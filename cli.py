#!python

import sys
from panasonicAW import ip


headAddr = "localhost:8000"

def getPosition():
    print("get position")
    pos = head.queryPosition()
    return pos

def addTmem():
    print("adding TMEM")
    print("Position starting key frame, then press ENTER.")
    input()
    getPosition()
    print("Position ending keyframe, the press ENTER.")
    input()
    getPosition()

def playTmem(args):
    print("playTmem")
    print(args)



head = ip.camera(headAddr)

args = sys.argv

args.pop(0) #discard script name

userCommand = str(args.pop(0))

userCommandArgs = args

if userCommand == 'add':
    addTmem()
elif userCommand == 'play':
    playTmem(args)
else:
    print("erorr")
