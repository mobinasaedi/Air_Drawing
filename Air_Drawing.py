import cv2
import mediapipe as mp
import math
import time


# ============================================================
# MEDIAPIPE SETUP
# ============================================================

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
RunningMode = mp.tasks.vision.RunningMode

MODEL_PATH = "hand_landmarker.task"

options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=MODEL_PATH),
    running_mode=RunningMode.VIDEO,
    num_hands=1,
    min_hand_detection_confidence=0.5,
    min_hand_presence_confidence=0.5,
    min_tracking_confidence=0.5,
)

detector = HandLandmarker.create_from_options(options)


# ============================================================
# COLORS
# ============================================================

COLORS = [
    ("WHITE", (255, 255, 255)),
    ("BLUE", (255, 0, 0)),
    ("GREEN", (0, 255, 0)),
    ("RED", (0, 0, 255)),
    ("YELLOW", (0, 255, 255)),
    ("PURPLE", (255, 0, 255)),
]

current_color_index = 0
current_color = COLORS[current_color_index][1]


# ============================================================
# CAMERA
# ============================================================

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("ERROR: Could not open webcam.")
    detector.close()
    exit()


# ============================================================
# FULLSCREEN WINDOW
# ============================================================

WINDOW_NAME = "Air Drawing"

cv2.namedWindow(
    WINDOW_NAME,
    cv2.WINDOW_NORMAL
)

cv2.setWindowProperty(
    WINDOW_NAME,
    cv2.WND_PROP_FULLSCREEN,
    cv2.WINDOW_FULLSCREEN
)


# ============================================================
# SCREEN SIZE
# ============================================================

screen_width = 1920
screen_height = 1080

# Try to get monitor resolution using OpenCV.
# If unavailable, the default above is used.

try:
    temp = cv2.imread("")
except:
    pass


# ============================================================
# CANVAS
# ============================================================

canvas = None

prev_x = None
prev_y = None

prev_smooth_x = None
prev_smooth_y = None

timestamp_ms = 0


# ============================================================
# GESTURE STATE
# ============================================================

thumb_action_done = False
two_finger_action_done = False

last_color_change = 0
COLOR_COOLDOWN = 1.0


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def distance(point1, point2):
    """Calculate distance between two landmarks."""

    return math.sqrt(
        (point1.x - point2.x) ** 2
        + (point1.y - point2.y) ** 2
        + (point1.z - point2.z) ** 2
    )


def fingers_up(hand):
    """Detect which fingers are extended."""

    # Index finger
    index_up = hand[8].y < hand[6].y

    # Middle finger
    middle_up = hand[12].y < hand[10].y

    # Ring finger
    ring_up = hand[16].y < hand[14].y

    # Pinky
    pinky_up = hand[20].y < hand[18].y

    # Thumb
    thumb_up = (
        distance(hand[4], hand[0])
        > distance(hand[3], hand[0]) * 1.15
    )

    return (
        thumb_up,
        index_up,
        middle_up,
        ring_up,
        pinky_up
    )


def get_gesture(hand):

    thumb, index, middle, ring, pinky = fingers_up(hand)

    count = sum([
        thumb,
        index,
        middle,
        ring,
        pinky
    ])

    # ========================================================
    # FIVE FINGERS = STOP
    # ========================================================

    if count == 5:
        return "STOP"

    # ========================================================
    # FIST = ERASE
    # ========================================================

    if count == 0:
        return "ERASE"

    # ========================================================
    # THUMB ONLY = CLEAR
    # ========================================================

    if (
        thumb
        and not index
        and not middle
        and not ring
        and not pinky
    ):
        return "CLEAR"

    # ========================================================
    # INDEX ONLY = DRAW
    # ========================================================

    if (
        index
        and not thumb
        and not middle
        and not ring
        and not pinky
    ):
        return "DRAW"

    # ========================================================
    # TWO FINGERS = COLOR
    # ========================================================

    if (
        index
        and middle
        and not thumb
        and not ring
        and not pinky
    ):
        return "COLOR"

    return "IDLE"


def change_color():

    global current_color_index
    global current_color

    current_color_index += 1

    if current_color_index >= len(COLORS):
        current_color_index = 0

    current_color = COLORS[current_color_index][1]

    print(
        "Color:",
        COLORS[current_color_index][0]
    )


def clear_canvas():

    global canvas
    global prev_x
    global prev_y

    canvas[:] = 0

    prev_x = None
    prev_y = None

    print("Canvas cleared")


# ============================================================
# MAIN LOOP
# ============================================================

while True:

    success, frame = cap.read()

    if not success:
        print("ERROR: Could not read webcam.")
        break

    # Mirror camera
    frame = cv2.flip(frame, 1)

    # ========================================================
    # CREATE CANVAS
    # ========================================================

    if canvas is None:

        canvas = frame.copy()

        canvas[:] = 0

    # ========================================================
    # HAND DETECTION
    # ========================================================

    rgb_frame = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb_frame
    )

    timestamp_ms = int(time.time() * 1000)

    result = detector.detect_for_video(
        mp_image,
        timestamp_ms
    )

    gesture = "NO HAND"


    # ========================================================
    # HAND FOUND
    # ========================================================

    if result.hand_landmarks:

        hand = result.hand_landmarks[0]

        gesture = get_gesture(hand)

        # Index fingertip
        index_tip = hand[8]

        h, w, _ = frame.shape

        smooth_x = int(prev_smooth_x * 0.7 + x * 0.3)
        smooth_y = int(prev_smooth_y * 0.7 + y * 0.3)

        x = max(0, min(w - 1, x))
        y = max(0, min(h - 1, y))


        # ====================================================
        # DRAW CURSOR
        # ====================================================

        cv2.circle(
            frame,
            (x, y),
            8,
            current_color,
            -1
        )


        # ====================================================
        # DRAW
        # ====================================================

        if gesture == "DRAW":

            if prev_x is not None and prev_y is not None:

                cv2.line(
                    canvas,
                    (prev_x, prev_y),
                    (x, y),
                    current_color,
                    6,
                    cv2.LINE_AA
                )

            prev_x = x
            prev_y = y


        # ====================================================
        # ERASE
        # ====================================================

        elif gesture == "ERASE":

            cv2.circle(
                canvas,
                (x, y),
                40,
                (0, 0, 0),
                -1
            )

            cv2.circle(
                frame,
                (x, y),
                40,
                (255, 255, 255),
                2
            )

            prev_x = None
            prev_y = None


        # ====================================================
        # CLEAR
        # ====================================================

        elif gesture == "CLEAR":

            if not thumb_action_done:

                clear_canvas()

                thumb_action_done = True

            prev_x = None
            prev_y = None


        # ====================================================
        # CHANGE COLOR
        # ====================================================

        elif gesture == "COLOR":

            current_time = time.time()

            if (
                not two_finger_action_done
                and current_time - last_color_change
                > COLOR_COOLDOWN
            ):

                change_color()

                last_color_change = current_time

                two_finger_action_done = True

            prev_x = None
            prev_y = None


        # ====================================================
        # STOP
        # ====================================================

        elif gesture == "STOP":

            prev_x = None
            prev_y = None


        # ====================================================
        # IDLE
        # ====================================================

        else:

            prev_x = None
            prev_y = None


    else:

        prev_x = None
        prev_y = None

        thumb_action_done = False
        two_finger_action_done = False


    # ========================================================
    # RESET GESTURE LOCKS
    # ========================================================

    if gesture != "CLEAR":
        thumb_action_done = False

    if gesture != "COLOR":
        two_finger_action_done = False


    # ========================================================
    # COMBINE CAMERA + DRAWING
    # ========================================================

    output = frame.copy()

    mask = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(mask, 1, 255, cv2.THRESH_BINARY)

    output[mask > 0] = canvas[mask > 0]
    


    # ========================================================
    # RESIZE TO FULLSCREEN
    # ========================================================

    output = cv2.resize(
        output,
        (screen_width, screen_height),
        interpolation=cv2.INTER_LINEAR
    )


    # ========================================================
    # TOP INFORMATION BAR
    # ========================================================

    cv2.rectangle(
        output,
        (0, 0),
        (screen_width, 95),
        (20, 20, 20),
        -1
    )

    cv2.putText(
        output,
        "AIR DRAWING",
        (30, 38),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.0,
        (255, 255, 255),
        2
    )

    cv2.putText(
        output,
        "Gesture: " + gesture,
        (30, 75),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        current_color,
        2
    )


    # ========================================================
    # BOTTOM TOOLBAR
    # ========================================================

    toolbar_height = 110

    cv2.rectangle(
        output,
        (
            0,
            screen_height - toolbar_height
        ),
        (
            screen_width,
            screen_height
        ),
        (25, 25, 25),
        -1
    )


    # ========================================================
    # COLOR LABEL
    # ========================================================

    cv2.putText(
        output,
        "COLORS",
        (30, screen_height - 65),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (255, 255, 255),
        2
    )


    # ========================================================
    # COLOR CIRCLES
    # ========================================================

    start_x = 170
    circle_y = screen_height - 55

    for i, (name, color) in enumerate(COLORS):

        circle_x = start_x + i * 90

        # Highlight selected color
        if i == current_color_index:

            cv2.circle(
                output,
                (circle_x, circle_y),
                27,
                (255, 255, 255),
                3
            )

        cv2.circle(
            output,
            (circle_x, circle_y),
            18,
            color,
            -1
        )


    # ========================================================
    # INSTRUCTIONS
    # ========================================================

    cv2.putText(
        output,
        "INDEX = DRAW",
        (800, screen_height - 70),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (255, 255, 255),
        1
    )

    cv2.putText(
        output,
        "FIST = ERASE",
        (800, screen_height - 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (255, 255, 255),
        1
    )

    cv2.putText(
        output,
        "THUMB = CLEAR",
        (1010, screen_height - 70),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (255, 255, 255),
        1
    )

    cv2.putText(
        output,
        "2 FINGERS = COLOR",
        (1010, screen_height - 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (255, 255, 255),
        1
    )

    cv2.putText(
        output,
        "5 FINGERS = STOP",
        (1280, screen_height - 55),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (255, 255, 255),
        1
    )


    # ========================================================
    # DISPLAY
    # ========================================================

    cv2.imshow(
        WINDOW_NAME,
        output
    )


    # ========================================================
    # KEYBOARD CONTROLS
    # ========================================================

    key = cv2.waitKey(1) & 0xFF

    # C = Clear
    if key == ord("c"):

        clear_canvas()

    # Q = Quit
    elif key == ord("q"):

        break

    # ESC = Quit
    elif key == 27:

        break


# ============================================================
# CLEANUP
# ============================================================

cap.release()

detector.close()

cv2.destroyAllWindows()

import mediapipe as mp

print(mp.tasks)
import os

print(os.listdir())