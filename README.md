Virtual Mouse Controlled by Hand Gestures
=========================================

This project showcases a virtual mouse that can be controlled using hand gestures. The mouse cursor's movement is simulated on the screen based on the movements of your hand. This is achieved using Python and various libraries.

Requirements
------------

-   Python 3.x
-   Webcam

Installation
------------

1.  Download the latest release or clone this repository: `git clone https://github.com/tufaylasaf/virtualmouse.git`
2.  Navigate to the project directory: `cd virtualmouse`
3.  Install the required Python packages: `pip install -r requirements.txt`

Usage
-----

1.  Run the main script: `python VirtualMouse.py`
2.  Ensure your webcam is enabled, properly positioned and your hand is visible. 

Features
--------

-   Real-time hand gesture tracking
-   Smooth cursor movement
-   Left and Right Click
-   Scrolling
-   Volume Control

How It Works
------------

The Project uses the following Resources:

-   [MediaPipe](https://developers.google.com/mediapipe/solutions/vision/hand_landmarker#get_started) - There are many Machine Learning Models trained by Google, I made use of the Hand Landmarks Detection Model to detect Hands.

The core logic involves:

-   Detecting if a Hand exists in a Frame.
-   Detects which fingers are Open or Closed, based on this you can simulate an actual Mouse Cursor.

License
-------

This project is licensed under the [MIT License](https://opensource.org/license/mit/).
