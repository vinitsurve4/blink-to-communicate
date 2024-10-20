from gtts import gTTS
import os
from scipy.spatial import distance as dist
from imutils.video import FileVideoStreamr
from imutils.video import VideoStream
from imutils import face_utils
import numpy as np
import argparse
import imutils
import time
import dlib
import cv2
import matplotlib.pyplot as plt
import pygame

timeseries, totalCount, altSignal, blinkLen = ([], [], [], [])
framenumber = 0

def eye_aspect_ratio(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    ear = (A + B) / (2.0 * C)
    return ear

ap = argparse.ArgumentParser()
ap.add_argument("-p", "--shape-predictor", required=True, help="path to facial landmark predictor")
ap.add_argument("-v", "--video", type=str, default="", help="path to input video file")
args = vars(ap.parse_args())

EYE_AR_THRESH = 0.3
EYE_AR_CONSEC_FRAMES = 8
MORSE_PAUSE = 8

COUNTER = 0
TOTAL = 0
PAUSE_COUNTER = 0

print("[INFO] loading facial landmark predictor...")
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(args["shape_predictor"])

(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

print("[INFO] starting video stream thread...")
if args["video"]:
    vs = FileVideoStream(args["video"]).start()
    fileStream = True
else:
    vs = VideoStream(src=0).start()
    fileStream = False

time.sleep(1.0)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
GREENISH = (220, 255, 220)
RED = (255, 0, 0)

WIDTH = 60
HEIGHT = 40
MARGIN = 5

ROWS = 7
COLS = 7

grid = []
for row in range(ROWS):
    grid.append([])
    for column in range(COLS):
        grid[row].append(0)

CIRORDER = "aeiou5_bfjpv6.cgkqw7?dhlrx8!13msy9$24ntz0@"
alphabet = " " * ROWS + CIRORDER
alphabet_pos = {}
MESSAGE = ""

pygame.init()

winHeight = ROWS * (HEIGHT + MARGIN) + MARGIN
winWidth = COLS * (WIDTH + MARGIN) + MARGIN
WINDOW_SIZE = [winWidth, winHeight]
screen = pygame.display.set_mode(WINDOW_SIZE)

pygame.display.set_caption("Array Backed Grid")

done = False
clock = pygame.time.Clock()

font = pygame.font.SysFont('arial', 40)

currentTile = (0, 0)
downwards = True

cursor_timer = pygame.USEREVENT + 1
blinkRef = pygame.USEREVENT + 2
blinkEvent = pygame.event.Event(blinkRef)
CURSORDELAY = 800
pygame.time.set_timer(cursor_timer, CURSORDELAY)

def text_objects(text):
    textSurface = font.render(text, True, (0, 50, 0))
    return textSurface, textSurface.get_rect()

def clickToggle():
    pos = pygame.mouse.get_pos()
    column = pos[0] // (WIDTH + MARGIN)
    row = pos[1] // (HEIGHT + MARGIN)
    toggle_grid(row, column)
    clicked_str = alphabet_pos[(row, column)]
    console_msg = "Clicked char {0} at grid point {1}:{2}".format(clicked_str, row, column)
    print(console_msg)

def toggle_grid(row, column, only_one_active=True):
    if grid[row][column] == 0:
        grid[row][column] = 1
    else:
        grid[row][column] = 0

def inc_before_end(c, end):
    if c < end - 1:
        return c + 1
    else:
        return 0

def movingCursor(currentTile, downwards):
    x, y = currentTile
    if downwards:
        x = inc_before_end(x, ROWS)
    else:
        y = inc_before_end(currentTile[1], COLS)
    return (x, y)

def handle_backspace():
    global MESSAGE
    if MESSAGE:
        MESSAGE = MESSAGE[:-1]  # Remove the last character from MESSAGE
        speak_message(MESSAGE)

def speak_message(message):
    language = 'en'
    myobj = gTTS(text=message, lang=language, slow=False)
    with open("temp.mp3", "wb") as f:
        myobj.write_to_fp(f)
    os.system("mpg123.exe temp.mp3")

while not done:
    if fileStream and not vs.more():
        break

    frame = vs.read()
    frame = imutils.resize(frame, width=450)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    rects = detector(gray, 0)

    if len(rects) > 1:
        # cv2.putText(frame, "Warning: More than one person detected!", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, RED, 2)
        mytext = "Warning: More than one person detected!"
        cv2.putText(frame,mytext,(10,60),cv2.FONT_HERSHEY_SIMPLEX,0.7,BLACK,2)
        speak_message(mytext)

    for rect in rects:
        shape = predictor(gray, rect)
        shape = face_utils.shape_to_np(shape)

        leftEye = shape[lStart:lEnd]
        rightEye = shape[rStart:rEnd]
        leftEAR = eye_aspect_ratio(leftEye)
        rightEAR = eye_aspect_ratio(rightEye)

        ear = (leftEAR + rightEAR) / 2.0

        leftEyeHull = cv2.convexHull(leftEye)
        rightEyeHull = cv2.convexHull(rightEye)
        cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
        cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)

        altSignal.append(0)

        if ear < EYE_AR_THRESH:
            COUNTER += 1
            timeseries.append((framenumber, 1))
            pygame.event.set_blocked(cursor_timer)

        else:
            if COUNTER >= EYE_AR_CONSEC_FRAMES:
                TOTAL += 1
                startBlinkFrame = framenumber - COUNTER
                theBlink = [1 for i in altSignal[startBlinkFrame:framenumber]]
                altSignal[startBlinkFrame:framenumber] = theBlink
                blinkLen.append(len(theBlink))
                pygame.event.set_allowed(cursor_timer)
                pygame.event.post(blinkEvent)
            timeseries.append((framenumber, 0))
            COUNTER = 0

        cv2.putText(frame, "Blinks: {}".format(TOTAL), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        cv2.putText(frame, "Eye Aspect Ratio: {:.2f}".format(ear), (250, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    totalCount.append((framenumber, TOTAL))
    framenumber += 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type in (pygame.MOUSEBUTTONDOWN, blinkRef):
            if currentTile[1] != 0:
                MESSAGE = MESSAGE + alphabet_pos[currentTile]
                print(MESSAGE)
                speak_message(MESSAGE)  # Speak out the message
                currentTile = (0, 0)
                downwards = True
            elif currentTile[1] == 0 and not downwards:
                currentTile = (0, 0)
                downwards = True
            elif downwards:
                downwards = False
        elif event.type == cursor_timer:
            currentTile = movingCursor(currentTile, downwards)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                handle_backspace()

    screen.fill(BLACK)
    string_counter = 0
    for column in range(COLS):
        for row in range(ROWS):
            color = WHITE
            if row == currentTile[0]:
                color = GREENISH
            if (row, column) == currentTile:
                color = GREEN
            x_coord = (MARGIN + WIDTH) * column + MARGIN
            y_coord = (MARGIN + HEIGHT) * row + MARGIN
            pygame.draw.rect(screen, color, [x_coord, y_coord, WIDTH, HEIGHT])
            currentChar = alphabet[string_counter]
            surf, rect = text_objects(currentChar)
            screen.blit(surf, (x_coord, y_coord))
            alphabet_pos.update({(row, column): currentChar})
            string_counter += 1

    # Adding the backspace symbol "@" to the bottom-right corner
    backspace_row = ROWS - 1
    backspace_column = COLS - 1
    backspace_x = (MARGIN + WIDTH) * backspace_column + MARGIN
    backspace_y = (MARGIN + HEIGHT) * backspace_row + MARGIN
    backspace_surf, backspace_rect = text_objects("@")
    screen.blit(backspace_surf, (backspace_x, backspace_y))
    alphabet_pos.update({(backspace_row, backspace_column): "@"})

    clock.tick(60)
    pygame.display.flip()
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

pygame.quit()
cv2.destroyAllWindows()
vs.stop()

def timeAxis(series):
    return [t for t in range(len(series))]

def plotWrangler(series):
    t = timeAxis(series)
    val = series
    return (t, val)

print(blinkLen)
x, y = plotWrangler(altSignal)
plt.step(x, y)
plt.show()



