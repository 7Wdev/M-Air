# 7Wdev !
# M-Air is a free tool for contorling your cursor by moving your hand in air.
# all credits for: Snowy (SnowyDragon)!

import cv2
import time
import numpy as np
import mediapipe as mp
import HandTracking as htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
import pyautogui
import win32api
import win32con
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import keyboard

wCam, hCam = 640, 480
wBox, hBox = 240, 150
rect = [int(wCam/3), 60, int(wCam/3)+wBox, hBox+60]
width, height = pyautogui.size()

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

pTime, cTime = 0, 0

detector = htm.HandDetector(mode=False, detectionCon=0.7)
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]

lastx, lasty = 0, 0

xFixer, yFixer = 8, 8

isMouseDown = False

def moveMouseTo(x: int, y: int):
    win32api.SetCursorPos((x, y))

def mouseDown(x, y):
    global isMouseDown
    isMouseDown = True
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)

def mouseUp(x, y):
    global isMouseDown
    isMouseDown = False
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)

def inRect(pt):
    print(pt[1], rect[0], rect[2])
    logic1 = pt[1] > rect[0] and pt[1] < rect[2]
    logic2 = pt[2] < rect[3] and pt[2] > rect[1]
    print(logic1, logic2)
    return logic1 and logic2

while not keyboard.is_pressed('q'):
    success, img = cap.read()
    img = cv2.flip(img, 1)
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)
    cv2.rectangle(img, (rect[0], rect[1]), (rect[2], rect[3]), (0, 255, 0), 2)
    if len(lmList) > 0:
        print(inRect(lmList[8]))
        if inRect(lmList[8]):
            gesture = detector.findGesture(lmList=lmList)
            x1, y1 = lmList[8][1], lmList[8][2]
            #cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
            xPos = int(np.interp(np.interp(x1, (rect[0], rect[2]),
                                           (0, wCam)), (0, wCam), (0, width)))
            yPos = int(np.interp(y1, [rect[1], rect[3]], [0, height]))
            if gesture != "ROCK!":
                if isMouseDown:
                    mouseUp(lastx, lasty)
            if abs(xPos - lastx) <= xFixer:
                xPos = lastx
            else:
                lastx = xPos
            if abs(yPos - lasty) <= yFixer:
                yPos = lasty
            else:
                lasty = yPos
            if gesture != "ROCK!":
                moveMouseTo(xPos, yPos)
            elif not isMouseDown:
                mouseDown(xPos, yPos)

    # fps part
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(img, "FPS: " + str(int(fps)), (10, 50),
                cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2)

    cv2.imshow("M-Air", img)
    k = cv2.waitKey(30) & 0xff
    # once you inter Esc capturing will stop
    if k == 27:
        break
cap.release()
cv2.destroyAllWindows()
