import cv2
import mediapipe as mp
from coach import Sense
from coach import Think
from coach import Act

import numpy as np

show_debug = True

# Main Program Loop
def main():
    """
    Main function to initialize the exercise tracking application.

    This function sets up the webcam feed, initializes the Sense, Think, and Act components,
    and starts the main loop to continuously process frames from the webcam.
    """

    
    # Initialize the components: Sense for input, Think for decision-making, Act for output
    sense = Sense.Sense()
    act = Act.Act()
    think = Think.Think(act)


    # Search and print available camera devices (may take a while to complete)
    #searchValidCameraIndexes()
    
    # Initialize the webcam capture
    cap = cv2.VideoCapture(0)  # Use the default camera (0) or change to a different index if multiple cameras are connected to system
    
    window_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    window_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    act.retrieve_window_size(window_width, window_height)

    # Main loop to process video frames
    while cap.isOpened():

        # Capture frame-by-frame from the webcam
        ret, frame = cap.read()
        mp_frame = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        # mp_frame = cv2.flip(mp_frame_mirrored, 1)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=mp_frame)

        if not ret:
            print("Failed to grab frame")
            break

        # Sense: Detect joints
        hands = sense.detect_hands(mp_image)
        hand_landmarks = hands.hand_landmarks
        if len(hand_landmarks) > 0:
            raw_x = hand_landmarks[0][8].x
            raw_y = hand_landmarks[0][8].y

            act.extract_finger_location(raw_x, raw_y, 4)
        
        if show_debug:
            act.print_debug(frame)
            act.draw_hands(mp_image, hands)

        decision = think.state
        
        # Exit if the 'q' key is pressed
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    # Release the webcam and close all OpenCV windows
    cap.release()
    cv2.destroyAllWindows()


def searchValidCameraIndexes():
    # checks the first 10 indexes. May take a while to complete
    
    print(f"Searching available camera index nrs")
    valid_cams = []
    for i in range(10):
        cap = cv2.VideoCapture(i)
        if cap is None or not cap.isOpened():
            print(f"Warning: unable to open video source: {i}")
        else:
            print(f"Found valid video source: {i}")
            valid_cams.append(i)
            
    print(f"Available camera index nrs: {valid_cams}")

if __name__ == "__main__":
    main()
