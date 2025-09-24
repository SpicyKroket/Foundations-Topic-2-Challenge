# Act Component: Provide feedback to the user

import mediapipe as mp
import cv2
import numpy as np
import random
import pyttsx3

from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.framework.formats import landmark_pb2
from mediapipe import solutions

# Act Component: Visualization to motivate user, visualization such as the skeleton and debugging information.
# Things to add: Other graphical visualization, a proper GUI, more verbal feedback
class Act:

    def __init__(self):
        # Tracking of animation states
        self.transition_count = 0
        self.max_transitions = 10  
        self.engine = pyttsx3.init()
        
        self.pos_x = 0
        self.pos_y = 0

        self.motivating_utterances = []

    def draw_hands(self, image, detection_result):
        annotated_image = draw_landmarks_on_image(image.numpy_view(), detection_result)
        cv2.imshow("Working Title", cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR))

    def display_controller(self):
        self.draw_hands()

    def extract_finger_location(self, raw_x, raw_y, no_decimals):
       x_absolute = round(raw_x * window_width, no_decimals)
       y_absolute = round(raw_y * window_height, no_decimals)

       self.pos_x = x_absolute
       self.pos_y = y_absolute

       return x_absolute, y_absolute

    def print_debug(self, frame):
        # Set font and text position
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = .9
        font_color = (0, 0, 0)  # White color in BGR
        thickness = 2

        text_position = (50, 50)
        
        # Information to be printed
        text_finger_location = ("Index finger location - x:{0} -- y:{1}".format( self.pos_x, self.pos_y))

        cv2.putText(frame, text_finger_location, text_position, font, font_scale, font_color, thickness)

        cv2.imshow("Working Title", frame)
        cv2.waitKey(1)

    def retrieve_window_size(self, width, height):
        global window_width
        global window_height

        window_width = width
        window_height = height
    
    def visualize_dot(self, frame):
        window_margin = 100
        # Generate a new dot if update_dot is True
        if self.update_dot:
            self.dot_x = random.randrange(window_margin, int(window_width - window_margin))
            self.dot_y = random.randrange(window_margin, int(window_height - window_margin))
            self.dot_radius = random.randrange(20, window_margin*2)
            self.update_dot=False
        
        cv2.circle(frame,center=(self.dot_x, self.dot_y), radius=self.dot_radius, color=(1,1,1), thickness=-1)

MARGIN = 10  # pixels
FONT_SIZE = 1
FONT_THICKNESS = 1
HANDEDNESS_TEXT_COLOR = (88, 205, 54) # vibrant green

def draw_landmarks_on_image(rgb_image, detection_result):
  hand_landmarks_list = detection_result.hand_landmarks
  handedness_list = detection_result.handedness
  annotated_image = np.copy(rgb_image)

  # Loop through the detected hands to visualize.
  for idx in range(len(hand_landmarks_list)):
    hand_landmarks = hand_landmarks_list[idx]
    handedness = handedness_list[idx]

    # Draw the hand landmarks.
    hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
    hand_landmarks_proto.landmark.extend([
      landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in hand_landmarks
    ])
    solutions.drawing_utils.draw_landmarks(
      annotated_image,
      hand_landmarks_proto,
      solutions.hands.HAND_CONNECTIONS,
      solutions.drawing_styles.get_default_hand_landmarks_style(),
      solutions.drawing_styles.get_default_hand_connections_style())

    # Get the top left corner of the detected hand's bounding box.
    height, width, _ = annotated_image.shape
    x_coordinates = [landmark.x for landmark in hand_landmarks]
    y_coordinates = [landmark.y for landmark in hand_landmarks]
    text_x = int(min(x_coordinates) * width)
    text_y = int(min(y_coordinates) * height) - MARGIN

    # Draw handedness (left or right hand) on the image.
    cv2.putText(annotated_image, f"{handedness[0].category_name}",
                (text_x, text_y), cv2.FONT_HERSHEY_DUPLEX,
                FONT_SIZE, HANDEDNESS_TEXT_COLOR, FONT_THICKNESS, cv2.LINE_AA)

  return annotated_image