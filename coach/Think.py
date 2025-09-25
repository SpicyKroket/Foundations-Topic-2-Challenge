from transitions import Machine
import numpy as np
from coach import Act
import collections
import time


# Think Component: Decision Making
# Things you need to improve: Add states and transitions according to your intervention/rehabilitation coaching design

class Think(object):
    def __init__(self, act_component):
        """
        Initializes the state machine and sets up the transition logic.
        :param act_component: Reference to the Act component to trigger visual feedback
        :param flexion_threshold: threshold for entering the flexion state
        :param extension_threshold: threshold for entering the extension state
        """
        act = Act.Act()

        # Define initial state and thresholds for transitions
        self.state = 'moving'  # Initial state
        self.hit_target = False
        self.previous_state = self.state

        # Distances that decide whether user is close enough
        self.minimum_distance = 50
        self.distance_to_target = 999
        self.targets_hit = 0
        self.on_target_start = -1
        self.req_time_on_target= 0.15 # Time that user should hold their finger on the target for

        # Act component for visualization
        self.act_component = act_component

        # Tracking how long it took to hit a dot
        self.dot_time_start = time.time()
        self.time_to_hit = 0
        self.last_dot_time = 999
        
    
    def calculate_distance(self, x_pos, y_pos, dot_x, dot_y):
        if x_pos > 0 and y_pos > 0:
            self.distance_to_target = round(np.sqrt(np.square(x_pos - dot_x) + np.square(y_pos - dot_y)), 4)
        else:
            self.distance_to_target = 999

    # Method to update the FSM state based on the current finger position
    def update_state(self, x_finger, y_finder, dot_x, dot_y, dot_radius):
        """
        Updates the state machine based on the current angle (flexion or extension).

        :param current_angle: The current elbow joint angle (in degrees)
        :param previous_angle: The previous elbow joint angle (in degrees)
        """
        self.calculate_distance(x_finger, y_finder, dot_x, dot_y)
    

        # current_time = time.time()
        time_elapsed = time.time() - self.on_target_start
        minimum_dist = self.minimum_distance + dot_radius

        if self.distance_to_target <= minimum_dist and self.state != "on_target":
            self.state = "on_target"
            self.on_target_start = time.time()
        elif self.state == "on_target" and time_elapsed >= self.req_time_on_target:
            self.time_to_hit = time.time() - self.dot_time_start
            self.dot_time_start = time.time()

            self.hit_target = True
            self.on_target_start = 0
            self.state = "hit_target"
        elif self.distance_to_target > self.minimum_distance:
            self.on_target_start = 0
            self.state = "moving"
