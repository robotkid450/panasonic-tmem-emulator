#!python

import sys


def getPosition():
    print("get position")

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
