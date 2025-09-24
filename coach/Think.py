from transitions import Machine
import collections


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


        # Define initial state and thresholds for transitions
        self.state = 'moving'  # Initial state
        self.previous_state = self.state
        # Act component for visualization
        self.act_component = act_component

        # Define the state machine with states 'flexion' and 'extension'
        states = ['moving', 'on_target']

        # Initialize the state machine
        self.machine = Machine(model=self, states=states, initial='moving')

        # Define transitions
        

    # Method to update the FSM state based on the current elbow angle
    def update_state(self, current_x, current_y, ):
        """
        Updates the state machine based on the current angle (flexion or extension).

        :param current_angle: The current elbow joint angle (in degrees)
        :param previous_angle: The previous elbow joint angle (in degrees)
        """