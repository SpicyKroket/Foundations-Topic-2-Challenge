import cv2
import mediapipe as mp
import math
import numpy as np
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import os
import platform

# Sense Component: Detect joints using the camera
# Things you need to improve: Make the skeleton tracking smoother and robust to errors.
class Sense:

    def __init__(self):
        # Initialize the Mediapipe Pose object to track joints

        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_hands = mp.solutions.hands.Hands()
        self.mp_pose = mp.solutions.pose.Pose()

        # STEP 2: Create an HandLandmarker object.
        system = platform.system()
        if system == "Windows":
            task_path = Path(_file_).parent / "../hand_landmarker.task"
            base_options = python.BaseOptions(model_asset_path=open(str(task_path.resolve(), "rb")).read())
        else: base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')

        options = vision.HandLandmarkerOptions(base_options=base_options,
                                               num_hands=2)
        self.detector = vision.HandLandmarker.create_from_options(options)
        # used later for having a moving avergage
        self.angle_window = [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
        self.previous_angle = -1 

    def detect_hands(self, mp_image):
        results = self.detector.detect(mp_image)
        return results if results else None

    def extract_finger_joint_coordinates(selfs, landmarks, joint):
        joint_index_map = {
            'index_tip': mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP,
            'middle_tip': mp.solutions.hands.HandLandmark.MIDDLE_FINGER_TIP,
            'ring_tip': mp.solutions.hands.HandLandmark.RING_FINGER_TIP,
            'pinky_tip': mp.solutions.hands.HandLandmark.PINKY_TIP,
            'thumb_tip': mp.solutions.hands.HandLandmark.THUMB_TIP
        }

        joint_index = joint_index_map[joint]
        landmark = landmarks.landmark[joint_index]

        return landmark.x, landmark.y