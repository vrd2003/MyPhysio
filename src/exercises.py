from datetime import datetime
import numpy as np
from .geometry import calculate_angle, get_landmark_coords, get_landmark_visibility

class Exercise:
    def __init__(self, name):
        self.name = name
        self.state = "SETUP" # SETUP, START, MOVEMENT, HOLD, REST/RELAX
        self.reps = 0
        self.hold_start_time = None
        self.setup_start_time = None
        self.relax_start_time = None
        self.feedback = "Setup: Get into position."
        self.current_angle = 0.0
        self.side = "RIGHT" 
        self.auto_side = True # Enable auto-detection by default

    def toggle_side(self):
        """
        Manually toggles side and disables auto-detection.
        """
        self.auto_side = False
        self.side = "LEFT" if self.side == "RIGHT" else "RIGHT"

    def detect_active_side(self, landmarks):
        """
        Determines which side (LEFT/RIGHT) is more visible.
        Returns: "LEFT" or "RIGHT"
        """
        # If manual override is active, don't auto-detect
        if not self.auto_side:
            return self.side

        # Left: 23, 25, 27. Right: 24, 26, 28
        left_vis = sum([get_landmark_visibility(landmarks, i) for i in [23, 25, 27]])
        right_vis = sum([get_landmark_visibility(landmarks, i) for i in [24, 26, 28]])
        
        return "LEFT" if left_vis > right_vis else "RIGHT"

    def get_leg_landmarks(self, landmarks):
        """
        Returns (hip, knee, ankle) coordinates for the active side.
        """
        if self.side == "LEFT":
            return (get_landmark_coords(landmarks, 23),
                    get_landmark_coords(landmarks, 25),
                    get_landmark_coords(landmarks, 27))
        else:
            return (get_landmark_coords(landmarks, 24),
                    get_landmark_coords(landmarks, 26),
                    get_landmark_coords(landmarks, 28))

    def check_setup(self, landmarks):
        """
        Validates starting pose.
        Returns: True/False, feedback_string
        """
        return True, "Ready"

    def update(self, landmarks):
        """
        Input: landmarks (MediaPipe)
        Returns: current_state, feedback, reps
        """
        raise NotImplementedError

class QuadricepsSet(Exercise):
    def __init__(self):
        super().__init__("Quadriceps Set")
        self.hold_duration = 5.0 
        self.relax_duration = 3.0
        self.setup_duration = 3.0
        self.target_knee_angle = 170.0 

    def check_setup(self, landmarks):
        self.side = self.detect_active_side(landmarks)
        hip, knee, ankle = self.get_leg_landmarks(landmarks)
        
        if hip == [0,0,0] or knee == [0,0,0] or ankle == [0,0,0]:
            return False, f"Ensure full {self.side} leg is visible."
            
        angle = calculate_angle(hip, knee, ankle)
        if angle < 140:
             return False, f"Straighten {self.side} leg on floor/bed."
             
        return True, f"Hold {self.side} leg still..."

    def update(self, landmarks):
        hip, knee, ankle = self.get_leg_landmarks(landmarks)
        
        angle = calculate_angle(hip, knee, ankle)
        self.current_angle = angle
        
        if self.state == "SETUP":
            is_valid, msg = self.check_setup(landmarks)
            if is_valid:
                if self.setup_start_time is None:
                    self.setup_start_time = datetime.now()
                
                elapsed = (datetime.now() - self.setup_start_time).total_seconds()
                if elapsed >= self.setup_duration:
                    self.state = "START"
                    self.feedback = f"Started! Straighten {self.side} leg."
                    self.auto_side = False # Lock side when starting
                else:
                    self.feedback = f"Hold {self.side}... {int(self.setup_duration - elapsed)}"
            else:
                self.setup_start_time = None
                self.feedback = f"Setup ({self.side}): {msg}"
        
        elif self.state == "START":
            if angle > self.target_knee_angle:
                self.state = "HOLD"
                self.hold_start_time = datetime.now()
                self.feedback = "Hold it! Tighten quads!"
            else:
                self.feedback = "Straighten your leg completely."
        
        elif self.state == "HOLD":
            if angle < (self.target_knee_angle - 10):
                self.state = "START" 
                self.feedback = "Knee bent! Restart rep."
                self.hold_start_time = None
            else:
                elapsed = (datetime.now() - self.hold_start_time).total_seconds()
                if elapsed >= self.hold_duration:
                    self.reps += 1
                    self.state = "RELAX"
                    self.relax_start_time = datetime.now()
                    self.feedback = "Relax leg."
                else:
                    self.feedback = f"Holding... {int(self.hold_duration - elapsed)}"

        elif self.state == "RELAX":
            elapsed = (datetime.now() - self.relax_start_time).total_seconds()
            if elapsed >= self.relax_duration:
                self.state = "START"
                self.feedback = "Ready for next rep."
            else:
                self.feedback = f"Relaxing... {int(self.relax_duration - elapsed)}"

        return self.state, self.feedback, self.reps

class StraightLegRaise(Exercise):
    def __init__(self):
        super().__init__("Straight Leg Raise")
        self.hold_duration = 3.0
        self.relax_duration = 3.0
        self.setup_duration = 3.0
        self.min_hip_flexion = 15.0
        self.relax_start_time = None

    def check_setup(self, landmarks):
        self.side = self.detect_active_side(landmarks)
        # Need Shoulder, Hip, Knee, Ankle
        shoulder_idx = 11 if self.side == "LEFT" else 12
        if get_landmark_coords(landmarks, shoulder_idx) == [0,0,0]:
             return False, "Show upper body."
        
        shoulder = get_landmark_coords(landmarks, shoulder_idx)
        hip, knee, ankle = self.get_leg_landmarks(landmarks)
        
        hip_angle = calculate_angle(shoulder, hip, knee)
        
        if hip_angle < 150:
             return False, "Lie flat on back."
        
        return True, f"Hold {self.side} leg still..."

    def update(self, landmarks):
        shoulder_idx = 11 if self.side == "LEFT" else 12
        shoulder = get_landmark_coords(landmarks, shoulder_idx)
        hip, knee, ankle = self.get_leg_landmarks(landmarks)
        
        hip_angle = calculate_angle(shoulder, hip, knee)
        knee_angle = calculate_angle(hip, knee, ankle)
        
        self.current_angle = hip_angle
        
        if self.state == "SETUP":
             is_valid, msg = self.check_setup(landmarks)
             if is_valid:
                if self.setup_start_time is None:
                    self.setup_start_time = datetime.now()
                elapsed = (datetime.now() - self.setup_start_time).total_seconds()
                if elapsed >= self.setup_duration:
                    self.state = "START"
                    self.feedback = f"Start! Lift {self.side} leg."
                    self.auto_side = False # Lock side
                else:
                    self.feedback = f"Hold {self.side}... {int(self.setup_duration - elapsed)}"
             else:
                self.setup_start_time = None
                self.feedback = f"Setup ({self.side}): {msg}"

        elif self.state == "START":
            if knee_angle > 170 and hip_angle < (180 - self.min_hip_flexion):
                self.state = "HOLD"
                self.hold_start_time = datetime.now()
                self.feedback = "Hold!"
            elif knee_angle < 160:
                self.feedback = "Keep knee straight."
            else:
                self.feedback = "Lift your leg."

        elif self.state == "HOLD":
            elapsed = (datetime.now() - self.hold_start_time).total_seconds()
            if hip_angle > (180 - self.min_hip_flexion + 5) or knee_angle < 160:
                 self.state = "START"
                 self.feedback = "Leg dropped or knee bent."
            elif elapsed >= self.hold_duration:
                self.reps += 1
                self.state = "RELAX"
                self.relax_start_time = datetime.now()
                self.feedback = "Lower leg slowly."
            else:
                self.feedback = f"Holding... {int(self.hold_duration - elapsed)}"

        elif self.state == "RELAX":
            elapsed = (datetime.now() - self.relax_start_time).total_seconds()
            if elapsed >= self.relax_duration:
                if hip_angle > 170:
                    self.state = "START"
                    self.feedback = "Ready."
                else:
                    self.feedback = "Lower leg completely."
            else:
                 self.feedback = f"Relaxing... {int(self.relax_duration - elapsed)}"

        return self.state, self.feedback, self.reps
    
class HeelSlide(Exercise):
    def __init__(self):
        super().__init__("Heel Slide")
        self.min_knee_flexion = 45.0
        self.setup_duration = 3.0
        self.setup_start_time = None
    
    def check_setup(self, landmarks):
         self.side = self.detect_active_side(landmarks)
         hip, knee, ankle = self.get_leg_landmarks(landmarks)
         
         if knee == [0,0,0]: return False, f"Show {self.side} leg"
         
         angle = calculate_angle(hip, knee, ankle)
         if angle < 140: return False, "Lie down, leg straight."
         return True, f"Hold {self.side} leg still..."

    def update(self, landmarks):
        hip, knee, ankle = self.get_leg_landmarks(landmarks)
        
        knee_angle = calculate_angle(hip, knee, ankle)
        self.current_angle = knee_angle
        
        if self.state == "SETUP":
             is_valid, msg = self.check_setup(landmarks)
             if is_valid:
                if self.setup_start_time is None:
                    self.setup_start_time = datetime.now()
                elapsed = (datetime.now() - self.setup_start_time).total_seconds()
                if elapsed >= self.setup_duration:
                    self.state = "START"
                    self.feedback = "Go: Slide heel."
                    self.auto_side = False # Lock side
                else:
                    self.feedback = f"Hold {self.side}... {int(self.setup_duration - elapsed)}"
             else:
                self.setup_start_time = None
                self.feedback = f"Setup ({self.side}): {msg}"
        
        elif self.state == "START":
            if knee_angle > 160:
                self.feedback = "Slide heel towards hip."
            elif knee_angle < 150:
                 self.state = "MOVEMENT"
                 self.feedback = "Keep sliding."
            else:
                self.feedback = "Ready."

        elif self.state == "MOVEMENT":
            if knee_angle < self.min_knee_flexion: 
                 self.state = "HOLD" 
                 self.feedback = "Good bend! Return."
            elif knee_angle > 160:
                 self.state = "START"
                 self.feedback = "Try to bend more next time." 

        elif self.state == "HOLD":
             self.state = "RETURN"
             self.feedback = "Slide back."

        elif self.state == "RETURN":
            if knee_angle > 170:
                self.reps += 1
                self.state = "START"
                self.feedback = "Rep complete."
        
        return self.state, self.feedback, self.reps

class WallSquat(Exercise):
    def __init__(self):
        super().__init__("Wall Squat")
        self.hold_duration = 5.0
        self.setup_duration = 3.0
        self.target_knee_angle = 90.0 
        self.setup_start_time = None
        
    def check_setup(self, landmarks):
        self.side = self.detect_active_side(landmarks)
        hip, knee, ankle = self.get_leg_landmarks(landmarks)
        
        angle = calculate_angle(hip, knee, ankle)
        
        if angle < 160: return False, "Stand up straight."
        return True, "Hold still..."

    def update(self, landmarks):
        hip, knee, ankle = self.get_leg_landmarks(landmarks)
        
        knee_angle = calculate_angle(hip, knee, ankle)
        self.current_angle = knee_angle
        
        if self.state == "SETUP":
             is_valid, msg = self.check_setup(landmarks)
             if is_valid:
                if self.setup_start_time is None:
                    self.setup_start_time = datetime.now()
                elapsed = (datetime.now() - self.setup_start_time).total_seconds()
                if elapsed >= self.setup_duration:
                    self.state = "START"
                    self.feedback = "Go: Lean & Squat."
                    self.auto_side = False 
                else:
                    self.feedback = f"Hold {self.side}... {int(self.setup_duration - elapsed)}"
             else:
                self.setup_start_time = None
                self.feedback = f"Setup ({self.side}): {msg}"

        elif self.state == "START":
            if knee_angle < 170:
                self.state = "MOVEMENT"
                self.feedback = "Lower down."
            else:
                self.feedback = "Lean against wall."
                
        elif self.state == "MOVEMENT":
            if knee_angle <= 100: 
                self.state = "HOLD"
                self.hold_start_time = datetime.now()
                self.feedback = "Hold!"
            elif knee_angle > 175:
                self.state = "START"
                
        elif self.state == "HOLD":
             elapsed = (datetime.now() - self.hold_start_time).total_seconds()
             if knee_angle > 130: 
                 self.state = "START"
                 self.feedback = "Stood up too soon."
             elif elapsed >= self.hold_duration:
                 self.state = "RETURN"
                 self.feedback = "Stand up."
             else:
                 self.feedback = f"Holding... {int(elapsed)}"
                 
        elif self.state == "RETURN":
            if knee_angle > 170:
                self.reps += 1
                self.state = "START"
                self.feedback = "Rep complete."

        return self.state, self.feedback, self.reps

class KneeExtensionROM(Exercise):
    def __init__(self):
        super().__init__("Knee Extension ROM")
        self.target_angle = 180.0
        self.setup_start_time = None
        self.setup_duration = 3.0

    def check_setup(self, landmarks):
         # Knee bent to start (e.g. sitting or heel slide pos)
        self.side = self.detect_active_side(landmarks)
        hip, knee, ankle = self.get_leg_landmarks(landmarks)
        
        angle = calculate_angle(hip, knee, ankle)
        if angle > 160: return False, "Sit down, knee bent."
        return True, f"Hold {self.side} leg still..."
        
    def update(self, landmarks):
        hip, knee, ankle = self.get_leg_landmarks(landmarks)
        
        angle = calculate_angle(hip, knee, ankle)
        self.current_angle = angle
        
        if self.state == "SETUP":
             is_valid, msg = self.check_setup(landmarks)
             if is_valid:
                if self.setup_start_time is None:
                    self.setup_start_time = datetime.now()
                elapsed = (datetime.now() - self.setup_start_time).total_seconds()
                if elapsed >= self.setup_duration:
                    self.state = "START"
                    self.feedback = "Go: Straighten knee."
                    self.auto_side = False
                else:
                    self.feedback = f"Hold {self.side}... {int(self.setup_duration - elapsed)}"
             else:
                self.setup_start_time = None
                self.feedback = f"Setup ({self.side}): {msg}"

        elif self.state == "START":
            if angle < 140:
                self.state = "MOVEMENT"
                self.feedback = "Straighten your knee."
            else:
                 self.feedback = "Bend knee to start."

        elif self.state == "MOVEMENT":
            if angle > 175:
                self.reps += 1
                self.state = "START" 
                self.feedback = "Fully extended! Relax."
                
        return self.state, self.feedback, self.reps
