# Act Component: Provide feedback to the user
import mediapipe as mp
import cv2
import numpy as np
import random
import pyttsx3
from gtts import gTTS
import pygame
import os

from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.framework.formats import landmark_pb2
from mediapipe import solutions

import time

show_debug_info = True

# Act Component: Visualization to motivate user, visualization such as the skeleton and debugging information.
# Things to add: Other graphical visualization, a proper GUI, more verbal feedback
class Act:

    def __init__(self):
        # Tracking of animation states
        self.transition_count = 0
        self.max_transitions = 10  
        self.engine = pyttsx3.init()
        self.completed = False

        # Check wether there are two hands in the screen
        self.two_hands = None

        # Variables for the dots
        self.update_dot = True
        self.dots_hit = 0
        self.max_dots = 10
        self.dot_times = list()
        
        # Tracking of finger and dot location
        self.pos_x = -1
        self.pos_y = -1
        self.dot_x = -1
        self.dot_y = -1
        self.dot_radius = 0

        # Timer variables
        self.start_timer = time.time()
        self.timer_duration = 60
        self.end_timer =  time.time() + self.timer_duration
        self.timer_complete = False

        # Feedback
        pygame.mixer.init()
        self.last_feedback_time = 0
        self.feedback_interval = 5
        self.last_phrase = None
        # self.last_phrase_time = time.time()

        self.feedback_phrases = {
            "Good": "good.mp3",
            "Excellent": "excellent.mp3",
            "Very close": "very_close.mp3",
            "Almost": "almost.mp3",
            "Keep trying": "try_again.mp3"
        }

        # Generate the files with phrase once
        for phrase, file in self.feedback_phrases.items():
            if not os.path.exists(file):
                tts = gTTS(text=phrase, lang="en")
                tts.save(file)

    def draw_target_line(self, frame):
        if self.pos_x > 0 and self.pos_y > 0:
            cv2.line(frame, (int(self.pos_x), int(self.pos_y)), (int(self.dot_x), int(self.dot_y)), (0, 0, 255), thickness=1)

    def extract_finger_location(self, raw_x, raw_y, no_decimals):
       x_absolute = raw_x * window_width
       y_absolute = raw_y * window_height

       self.pos_x = round(x_absolute, 4)
       self.pos_y = round(y_absolute, 4)
    
    def finger_dot(self, frame):
        if self.pos_x > 0 and self.pos_y > 0:
            cv2.circle(frame, (int(self.pos_x), int(self.pos_y)), 20, (1, 1, 1), thickness=-1)
        else:
            cv2.circle(frame, (-1, -1), 1, (0, 0, 0), thickness=-1)

    def give_feedback(self, distance_to_target):
        import time
        import random
        now = time.time()
        time_since_last_phrase = now - self.last_feedback_time

        phrase = None

        if time_since_last_phrase < self.feedback_interval:
            return

        if distance_to_target < 100:
            phrase = "Excellent"
        elif distance_to_target < 250:
            options = ["Very close", "Almost", "Good"]
            safe_options = [p for p in options if p != getattr(self, "last_phrase", None)]
            if not safe_options:
                safe_options = options
            phrase = random.choice(safe_options)
        elif distance_to_target > 500 and time_since_last_phrase > 5:
            phrase = "Keep trying"

        if phrase:
            self.speak_feedback(phrase)
            self.last_feedback_time = now
            self.last_phrase = phrase

    def retrieve_window_size(self, width, height):
        global window_width
        global window_height

        window_width = width
        window_height = height

    def show_timer(self, frame):
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = .9
        font_color = (0, 0, 0)  # White color in BGR
        thickness = 2
        
        time_left = int(self.end_timer - time.time())

        if time_left >= 0:
            text_countdown = "Time left: {0}s".format(time_left)
            cv2.putText(frame, text_countdown, (50, 200), font, font_scale, font_color, thickness)
        else:
            self.timer_complete = True

    def speak_feedback(self, phrase):
        file = self.feedback_phrases[phrase]
        pygame.mixer.music.load(file)
        pygame.mixer.music.play()
    
    def task_complete(self):
        self.completed = True

        average_time = round(np.mean(self.dot_times), 1)
        best_time = round(np.min(self.dot_times), 1)
        score_board = np.zeros((450, 600, 3), dtype=np.uint8)
        
        text_dot_score = "You hit {0} dots!".format(self.dots_hit)
        text_average_time = "You took {0}s on average.".format(average_time)
        text_quickest_dot = "Your fastests time was {0}s.".format(best_time)

        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = .9
        font_color = (255, 255, 255)  # White color in BGR
        thickness = 2

        cv2.putText(score_board, text_dot_score, (10, 50), font, font_scale, font_color, thickness)
        cv2.putText(score_board, text_average_time, (10, 90), font, font_scale, font_color, thickness)
        cv2.putText(score_board, text_quickest_dot, (10, 130), font, font_scale, font_color, thickness)
        
        # Show image
        cv2.imshow('Task completed', score_board)
        
        # Wait until a key is hit and then quit the program

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
            text_finger_location = "Index finger location - x:{0} y:{1}".format(self.pos_x, self.pos_y)
            cv2.putText(frame, text_finger_location, text_position, font, font_scale, font_color, thickness)

            text_target_distance = "Distance to target: {0}px".format(distance) 
            cv2.putText(frame, text_target_distance, (50, 90), font, font_scale, font_color, thickness)

            # self.finger_dot(frame)
            self.draw_target_line(frame)
        
        # text_dots_hit = "Dots hit: {0} out of {1}".format(self.dots_hit, self.max_dots)
        text_dots_hit = "Dots hit: {0}".format(self.dots_hit)
        cv2.putText(frame, text_dots_hit, (50, 130), font, font_scale, font_color, thickness)

        # Drawing of the dots
        # if self.dots_hit < self.max_dots:
        if not self.timer_complete:
            self.visualize_dot(frame)
        else:
            window_offset = 30
            corner_x = int(window_width - window_offset)
            corner_y = int(window_height - window_offset)
            cv2.rectangle(frame, (window_offset, window_offset), (corner_x, corner_y), (50, 50, 50), thickness=-1)
            if not self.dot_times: self.dot_times = [0]
            self.task_complete()

        if self.two_hands:
            window_offset = 30
            corner_x = int(window_width - window_offset)
            corner_y = int(window_height - window_offset)
            cv2.rectangle(frame, (window_offset, window_offset), (corner_x, corner_y), (30, 30, 255), thickness=-1)
            cv2.putText(frame, "Failure in hand detection!", (200, 200), font, font_scale, font_color, thickness)
            cv2.putText(frame, "- Two hands detected", (200, 230), font, font_scale, font_color, thickness)

        self.show_timer(frame)

        if show_debug_info: 
            combined = cv2.addWeighted(frame, 0.8, hand_skeleton, 0.2, 0)
            cv2.imshow("Feedback window", combined)
        else: cv2.imshow("Task window", frame)

        if self.two_hands: cv2.waitKey(500)
        else: cv2.waitKey(1)
    
    def visualize_dot(self, frame):
        window_margin = 300 # Margin to make sure the dot does not go outside of the screen
        window_margin = int(min(window_width, window_height) // 4)

        if self.update_dot:
            self.dot_x = random.randrange(window_margin, int(window_width - window_margin))
            self.dot_y = random.randrange(window_margin, int(window_height - window_margin))
            self.dot_radius = random.randrange(20, 75)
            self.update_dot = False
        
        cv2.circle(frame, center=(self.dot_x, self.dot_y), radius=self.dot_radius, color=(1,1,1), thickness=-1)
     
    
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