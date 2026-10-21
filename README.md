##Air_Drawing
An air-drawing system using hand and finger gesture recognition with Python, OpenCV, and MediaPipe

README
🎨 Air Drawing — Draw in the Air with Hand Detection

A Computer Vision project in Python that lets the user draw on the camera feed without touching the screen, using only finger movements.

In this project, MediaPipe Hand Landmarker is used to detect hand and finger movements, and each gesture is mapped to a specific command for drawing, erasing, changing color, and clearing the entire canvas.

✨ Features
🖊️ Draw with the index finger

🧹 Erase parts of the drawing by making a fist

🗑️ Clear the entire canvas by raising the thumb

🎨 Change color by raising two fingers

✋ Pause by raising all fingers

🌈 Support for multiple colors

📷 Real-time webcam input

🖥️ Fullscreen display

⌨️ Keyboard controls for clearing and exiting the program

🤌 Hand Gestures
Hand Gesture	Action
☝️ Index finger only	Draw
✊ Fist	Erase
👍 Thumb only	Clear entire canvas
✌️ Two fingers	Change color
🖐️ Five fingers	Pause
No hand	Idle / Ready state
🛠️ Technologies Used
Python

OpenCV

MediaPipe

Math

Time

📦 Installing Dependencies
First, install the required libraries:

text
pip install opencv-python mediapipe
📁 Project Structure
text
Air_Drawing/
│
├── Air_Drawing.py
├── hand_landmarker.task
└── README.md
The hand_landmarker.task file is the MediaPipe model used for hand detection and must be placed alongside the Python file.

▶️ Running the Project
After installing the libraries and placing the model file in the project folder, run the program:

text
python Air_Drawing.py
The webcam will activate, and you can start drawing with hand gestures.

🎨 Available Colors
The project currently supports the following colors:

⚪ White

🔵 Blue

🟢 Green

🔴 Red

🟡 Yellow

🟣 Purple

You can cycle through the colors using the two-finger gesture.

⌨️ Keyboard Controls
Key	Action
C	Clear the canvas
Q	Exit the program
ESC	Exit the program
🧠 How It Works
First, the image captured from the webcam is processed by OpenCV. Then MediaPipe identifies the various landmarks of the hand.

By examining the positions of these landmarks, it determines which fingers are extended. Based on the number and combination of extended fingers, the corresponding gesture is recognized.

In DRAW mode, the position of the index fingertip is converted to image coordinates, and a line is drawn between the current and previous positions.

👩‍💻 About the Project
This project was developed as a practical exercise in the areas of Computer Vision, Hand Tracking, and Human-Computer Interaction (HCI).

The goal of the project is to use hand gesture recognition to create a user interface that requires no screen contact.

This project was developed as a practical exercise in the areas of Computer Vision, Hand Tracking, and Human-Computer Interaction (HCI).

The goal of the project is to use hand gesture recognition to create a user interface that requires no screen contact.

