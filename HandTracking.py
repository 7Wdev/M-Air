# 7Wdev !
# M-Air is a free tool for contorling your cursor by moving your hand in air.
# all credits for: Snowy (SnowyDragon)!

from math import sqrt
import cv2
import mediapipe as mp
import time

from numpy.lib import math


class HandDetector():

    def __init__(self, mode=False, max_hands=2, detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.max_hands = max_hands
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpHands = mp.solutions.hands
        self.mpDrawer = mp.solutions.drawing_utils
        self.hands = self.mpHands.Hands(self.mode, self.max_hands,
                                        self.detectionCon, self.trackCon)

        self.test_landmarks_data = [
            0.499651, 0.849638, 0.614354, 0.796254,
            0.686660, 0.692482, 0.743792, 0.606666,
            0.809362, 0.512337, 0.538779, 0.499517,
            0.513829, 0.361394, 0.484049, 0.260214,
            0.452508, 0.173999, 0.445565, 0.512067,
            0.396448, 0.358399, 0.355494, 0.245083, 0.318670,
            0.157915, 0.355069, 0.562040, 0.278774,
            0.435983, 0.221781, 0.345394, 0.178977, 0.273430,
            0.288238, 0.631016, 0.219506, 0.544787,
            0.162939, 0.483343, 0.110222, 0.422808]

    def findHands(self, img, draw=True):
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(rgb)
        # print(results.multi_hand_landmarks)
        if self.results.multi_hand_landmarks:
            for handLM in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDrawer.draw_landmarks(
                        img, handLM, self.mpHands.HAND_CONNECTIONS)
        return img

    def findPosition(self, img, handInd=0, draw=True):
        lmList = []
        if self.results.multi_hand_landmarks:
            hand = self.results.multi_hand_landmarks[handInd]
            for id, lm in enumerate(hand.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                #print(id, cx, cy)
                lmList.append([id, cx, cy])
                if id == 0:
                    pass
                if draw:
                    cv2.circle(img, (cx, cy), 15, (255, 255, 0), cv2.FILLED)

        return lmList

    def get_Euclidean_DistanceAB(self, a_x: float, a_y: float, b_x: float, b_y: float):
        dist = pow(a_x - b_x, 2) + pow(a_y - b_y, 2)
        return sqrt(dist)

    def isThumbNearFirstFinger(self, point1, point2):
        distance = self.get_Euclidean_DistanceAB(
            point1[1], point1[2], point2[1], point2[2])
        return distance < 0.1

    def findGesture(self, lmList=[], img=None, handInd=0):
        gesture = "UNKNOWN"
        thumbIsOpen, firstFingerIsOpen, secondFingerIsOpen, thirdFingerIsOpen, fourthFingerIsOpen = False, False, False, False, False
        isLeft: bool = lmList[5][1] < lmList[17][1]
        if isLeft:
            fixedKeyPoint = lmList[2][1]
            if lmList[3][1] < fixedKeyPoint and lmList[4][1] < fixedKeyPoint:
                thumbIsOpen = True
        else:
            fixedKeyPoint = lmList[2][1]
            if lmList[3][1] > fixedKeyPoint and lmList[4][1] > fixedKeyPoint:
                thumbIsOpen = True

        fixedKeyPoint = lmList[6][2]
        if lmList[7][2] < fixedKeyPoint and lmList[8][2] < fixedKeyPoint:
            firstFingerIsOpen = True

        fixedKeyPoint = lmList[10][2]
        if lmList[11][2] < fixedKeyPoint and lmList[12][2] < fixedKeyPoint:
            secondFingerIsOpen = True

        fixedKeyPoint = lmList[14][2]
        if lmList[15][2] < fixedKeyPoint and lmList[16][2] < fixedKeyPoint:
            thirdFingerIsOpen = True

        fixedKeyPoint = lmList[18][2]
        if lmList[19][2] < fixedKeyPoint and lmList[20][2] < fixedKeyPoint:
            fourthFingerIsOpen = True

        if thumbIsOpen and firstFingerIsOpen and secondFingerIsOpen and thirdFingerIsOpen and fourthFingerIsOpen:
            print("FIVE!")

        elif not thumbIsOpen and firstFingerIsOpen and secondFingerIsOpen and thirdFingerIsOpen and fourthFingerIsOpen:
            return "FOUR!"

        elif thumbIsOpen and firstFingerIsOpen and secondFingerIsOpen and not thirdFingerIsOpen and not fourthFingerIsOpen:
            return "TREE!"

        elif thumbIsOpen and firstFingerIsOpen and not secondFingerIsOpen and not thirdFingerIsOpen and not fourthFingerIsOpen:
            return "TWO!"

        elif not thumbIsOpen and firstFingerIsOpen and not secondFingerIsOpen and not thirdFingerIsOpen and not fourthFingerIsOpen:
            return "ONE!"

        elif not thumbIsOpen and firstFingerIsOpen and secondFingerIsOpen and not thirdFingerIsOpen and not fourthFingerIsOpen:
            return "YEAH!"

        elif not thumbIsOpen and firstFingerIsOpen and not secondFingerIsOpen and not thirdFingerIsOpen and fourthFingerIsOpen:
            return "ROCK!"

        elif thumbIsOpen and firstFingerIsOpen and not secondFingerIsOpen and not thirdFingerIsOpen and fourthFingerIsOpen:
            return "SPIDERMAN!"

        elif not thumbIsOpen and not firstFingerIsOpen and not secondFingerIsOpen and not thirdFingerIsOpen and not fourthFingerIsOpen:
            return "FIST!"

        elif not firstFingerIsOpen and secondFingerIsOpen and thirdFingerIsOpen and fourthFingerIsOpen and self.isThumbNearFirstFinger(lmList[4], lmList[8]):
            return "OK!"

        return gesture


def test():
    cap = cv2.VideoCapture(0)
    pTime, cTime = 0, 0

    detector = HandDetector()

    while True:
        success, img = cap.read()

        img = detector.findHands(img)
        lmList = detector.findPosition(img)
        if len(lmList) > 0:
            print(lmList[4])

        # fps part
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        cv2.putText(img, str(int(fps)), (10, 70),
                    cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 0), 3)

        cv2.imshow("Image", img)
        cv2.waitKey(1)


def main():
    pass


if __name__ == '__main__':
    main()
