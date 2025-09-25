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

show_debug_info = True

# Act Component: Visualization to motivate user, visualization such as the skeleton and debugging information.
# Things to add: Other graphical visualization, a proper GUI, more verbal feedback
class Act:

    def __init__(self):
        # Tracking of animation states
        self.transition_count = 0
        self.max_transitions = 10  
        self.engine = pyttsx3.init()

        self.two_hands = None

        self.update_dot = True
        self.dots_hit = 0
        
        self.pos_x = -1
        self.pos_y = -1
        self.dot_x = -1
        self.dot_y = -1
        self.dot_radius = 0

        self.max_dots = 10

        self.motivating_utterances = []

    def draw_target_line(self, frame):
        if self.pos_x > 0 and self.pos_y > 0:
            cv2.line(frame, (int(self.pos_x), int(self.pos_y)), (int(self.dot_x), int(self.dot_y)), (0, 0, 255), thickness=1)

    def extract_finger_location(self, raw_x, raw_y, no_decimals):
       x_absolute = round(raw_x * window_width, no_decimals)
       y_absolute = round(raw_y * window_height, no_decimals)

       self.pos_x = x_absolute
       self.pos_y = y_absolute
    
    def finger_dot(self, frame):
        if self.pos_x > 0 and self.pos_y > 0:
            cv2.circle(frame, (int(self.pos_x), int(self.pos_y)), 20, (1, 1, 1), thickness=-1)
        else:
            cv2.circle(frame, (-1, -1), 1, (0, 0, 0), thickness=-1)

    def retrieve_window_size(self, width, height):
        global window_width
        global window_height

        window_width = width
        window_height = height
    
    def task_complete(self):
        img = np.zeros((600, 450, 3), dtype=np.uint8)

        

        # Show image
        cv2.imshow('Task completed', img)
        cv2.waitKey(1)

    def visualize_program(self, frame, decision, image, detection, distance):
        # Target for how many dots should be hit

        # Code to show hand skeleton
        annotated_image = draw_landmarks_on_image(image.numpy_view(), detection)
        hand_skeleton_mirror = cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR)
        hand_skeleton = cv2.flip(hand_skeleton_mirror, 1)

        # Set font and text position
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = .9
        font_color = (0, 0, 0)  # White color in BGR
        thickness = 2

        text_position = (50, 50)

        
        
        # Information to be printed
        if show_debug_info:
            text_finger_location = "Index finger location - x:{0} -- y:{1}".format(self.pos_x, self.pos_y)
            cv2.putText(frame, text_finger_location, text_position, font, font_scale, font_color, thickness)

            text_target_distance = "Distance to target: {0}".format(distance) 
            cv2.putText(frame, text_target_distance, (50, 90), font, font_scale, font_color, thickness)

            # self.finger_dot(frame)
            self.draw_target_line(frame)
        
        text_dots_hit = "Dots hit: {0} out of {1}".format(self.dots_hit, self.max_dots)
        cv2.putText(frame, text_dots_hit, (50, 130), font, font_scale, font_color, thickness)

        # Drawing of the dots
        if self.dots_hit < self.max_dots:
            self.visualize_dot(frame)
        else:
            self.task_complete()

        if self.two_hands:
            window_offset = 30
            corner_x = int(window_width - window_offset)
            corner_y = int(window_height - window_offset)
            cv2.rectangle(frame, (window_offset, window_offset), (corner_x, corner_y), (30, 30, 255), thickness=-1)
            cv2.putText(frame, "Failure in hand detection!", (200, 200), font, font_scale, font_color, thickness)
            cv2.putText(frame, "- Two hands detected", (200, 230), font, font_scale, font_color, thickness)

        if show_debug_info: 
            combined = cv2.addWeighted(frame, 0.8, hand_skeleton, 0.2, 0)
            cv2.imshow("Feedback window", combined)
        else: cv2.imshow("Task window", frame)

        if self.two_hands: cv2.waitKey(500)
        else: cv2.waitKey(1)
    
    def visualize_dot(self, frame):
        window_margin = 300 # Margin to make sure the dot does not go outside of the screen

        if self.update_dot:
            self.dot_x = random.randrange(window_margin, int(window_width - window_margin))
            self.dot_y = random.randrange(window_margin, int(window_height - window_margin))
            self.dot_radius = random.randrange(20, 75)
            self.update_dot = False
        
        cv2.circle(frame, center=(self.dot_x, self.dot_y), radius=self.dot_radius, color=(1,1,1), thickness=-1)
    
    def visualize_task(self):
        # Background
        img = np.zeros((500, 500, 3), dtype=np.uint8)

        self.visualize_dot(img)

        # Show image
        cv2.imshow('Move your finger to the dots!', img)
        cv2.waitKey(1)
    
    
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