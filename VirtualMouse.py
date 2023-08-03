"""
Virtual Mouse 
By Tufayl
"""

import cv2
import time
import numpy as np
import HandTracking as ht
import mouse

# For Simulating Keyboard presses
import ctypes
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


# Calculate Frame Rate
pTime = 0
cTime = 0

# For Smooth Movement of the Virtual Mouse
plocX, plocY = 0, 0
clocX, clocY = 0, 0
smoothening = 7

cap = cv2.VideoCapture(
    0
)  # Gets the Camera, 0 for integrated Camera, 1 for external Camera
wCam, hCam = 640, 480  # Width and Height of window and Camera
wScr, hScr = 1920, 1080  # Width and Height of your Monitor
cap.set(3, wCam)
cap.set(4, hCam)
frameR = 100  # Reduce the input frame for the Virutal Mouse

# Volume Control
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]

taskviewOpen = False

# For Virtual Mouse Scroll
scrollStartY = 0
startScroll = False
deadZone = 10

rightClicked = False
holding = False

detector = ht.handDetector()  # Initialize the Hand Detector

while True:
    success, img = cap.read()  # Gets each Frame of the video
    img = cv2.flip(img, 1)
    img = detector.findHands(img, draw=False)  # Detects if there is a hand
    lmList = detector.findPosition(
        img, draw=True
    )  # Returns a list of all the landmark Positions (finger positions)

    if len(lmList) != 0:
        x1, y1 = lmList[8][1:]  # Gets the coordinates for the tip of the index finger
        x2, y2 = lmList[12][1:]  # Gets the coordinates for the tip of the middle finger

        fingers = detector.fingersUp()  # Returns a list of fingers that are up

        # Draws the Input Area
        cv2.rectangle(
            img, (frameR, frameR), (wCam - frameR, hCam - frameR), (255, 0, 255), 2
        )

        # Cursor Movement
        # You can only move the cursor if only the index finger is up
        if fingers[1] == 1 and fingers.count(1) < 2:
            x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
            y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))

            clocX = plocX + (x3 - plocX) / smoothening
            clocY = plocY + (y3 - plocY) / smoothening

            mouse.move(clocX, clocY)
            cv2.circle(img, (x1, y1), 8, (255, 255, 255), cv2.FILLED)

            plocX, plocY = clocX, clocY
            if startScroll:
                startScroll = False

        # Mouse Click
        if fingers[1] == 1 and fingers[2] == 1 and fingers.count(1) < 3:
            length, img, lineInfo = detector.findDistance(8, 12, img)
            # To Click, bring your index and middle finger together
            if length < 20:
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 8, (0, 255, 0), cv2.FILLED)
                if not holding:
                    mouse.click()
                taskviewOpen = False
                rightClicked = False
            # To Scroll, bring your middle and index finger far apart, then move your hand up and down to scroll
            elif length > 40:
                if not startScroll:
                    scrollStartY = y2
                    startScroll = True
                if y2 < scrollStartY - deadZone:
                    mouse.wheel(0.75)
                elif y2 > scrollStartY + deadZone:
                    mouse.wheel(-0.75)

        # Volume Control
        # Bring your index finger and thumb close together or far apart, to use as a slider
        if fingers[0] == 1 and fingers[1] == 1 and fingers.count(1) < 3:
            length, img, lineInfo = detector.findDistance(4, 8, img)
            # Calculate the volume based on the distance between thumb and index finger
            vol = np.interp(length, [12, 95], [minVol, maxVol])
            volume.SetMasterVolumeLevel(vol, None)

            if length < 25:
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 8, (0, 255, 0), cv2.FILLED)

        # Open all your fingers to go to Task View
        if fingers.count(1) == 5 and not taskviewOpen:
            ctypes.windll.user32.keybd_event(0x5B, 0, 0, 0)  # Press Win key
            ctypes.windll.user32.keybd_event(0x09, 0, 0, 0)  # Press Tab key
            ctypes.windll.user32.keybd_event(0x09, 0, 2, 0)  # Release Tab key
            ctypes.windll.user32.keybd_event(0x5B, 0, 2, 0)  # Release Win key
            taskviewOpen = True

        # Right Click
        # Open index, middle and ring finger
        if (
            fingers[1] == 1
            and fingers[2]
            and fingers[3] == 1
            and fingers.count(1) <= 3
            and not rightClicked
        ):
            mouse.right_click()
            rightClicked = True

        # Hold and Drag
        # Bring the thumb, index and finger together to hold
        if (
            fingers[0] == 1
            and fingers[1] == 1
            and fingers[2] == 1
            and fingers.count(1) <= 3
        ):
            thumb2index, img1, lineInfo1 = detector.findDistance(4, 8, img)
            thumb2middle, img2, lineInfo2 = detector.findDistance(4, 12, img)
            if thumb2index <= 25 and thumb2middle <= 25 and not holding:
                cv2.circle(
                    img, (lineInfo1[4], lineInfo1[5]), 8, (0, 255, 0), cv2.FILLED
                )
                print("Holding")
                mouse.press(button="left")
                holding = True
            if holding and thumb2index >= 35 and thumb2middle >= 35:
                print("Released")
                mouse.release(button="left")
                holding = False

            if holding:
                x3 = np.interp(lineInfo1[4], (frameR, wCam - frameR), (0, wScr))
                y3 = np.interp(lineInfo1[5], (frameR, hCam - frameR), (0, hScr))

                clocX = plocX + (x3 - plocX) / smoothening
                clocY = plocY + (y3 - plocY) / smoothening

                mouse.move(clocX, clocY)

                plocX, plocY = clocX, clocY

    # Calculate Frame Rate and Display it
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(
        img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3
    )
    cv2.imshow("Image", img)
    cv2.waitKey(1)
