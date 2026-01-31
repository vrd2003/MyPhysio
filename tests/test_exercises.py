import unittest
from unittest.mock import MagicMock
from datetime import datetime, timedelta
import sys
import os

# Adjust path to find src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.exercises import QuadricepsSet, StraightLegRaise

class MockLandmark:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class MockLandmarks:
    def __init__(self, landmark_list):
        self.landmark = landmark_list

def create_mock_landmarks(coords_dict):
    # defaulted to 33 zeros
    landmarks = [MockLandmark(0,0,0) for _ in range(33)]
    for idx, (x, y, z) in coords_dict.items():
        landmarks[idx] = MockLandmark(x, y, z)
    return MockLandmarks(landmarks)

class TestQuadricepsSet(unittest.TestCase):
    def test_state_transitions(self):
        ex = QuadricepsSet()
        
        # 1. Start with knee bent (bad form) -> State START
        # Hip 24, Knee 26, Ankle 28. Angle < 170.
        # A(0,1), B(0,0), C(1,0) is 90 deg. 
        # Let's align on X axis: Hip(0,0), Knee(1,0), Ankle(2,0) is 180.
        # Knee(1,0.2) makes it bent.
        
        # Straight leg: Hip(0,0), Knee(1,0), Ankle(2,0) -> 180 deg
        lms_straight = create_mock_landmarks({24:(0,0,0), 26:(1,0,0), 28:(2,0,0)})
        state, fb, reps = ex.update(lms_straight)
        self.assertEqual(state, "HOLD")
        
        # 2. Hold for 4 seconds (less than 5)
        ex.hold_start_time = datetime.now() - timedelta(seconds=4)
        state, fb, reps = ex.update(lms_straight)
        self.assertEqual(state, "HOLD")
        
        # 3. Hold for 5+ seconds -> REACH RELAX
        ex.hold_start_time = datetime.now() - timedelta(seconds=5.1)
        state, fb, reps = ex.update(lms_straight)
        self.assertEqual(reps, 1)
        self.assertEqual(state, "RELAX")
        
        # 4. In Relax state, pass time. 2 seconds (less than 3)
        # Verify timer is set
        self.assertIsNotNone(ex.relax_start_time)
        ex.relax_start_time = datetime.now() - timedelta(seconds=2)
        state, fb, reps = ex.update(lms_straight)
        self.assertEqual(state, "RELAX")
        
        # 5. Pass 3+ seconds -> Back to START
        ex.relax_start_time = datetime.now() - timedelta(seconds=3.1)
        state, fb, reps = ex.update(lms_straight)
        self.assertEqual(state, "START")

class TestStraightLegRaise(unittest.TestCase):
    def test_transitions(self):
        ex = StraightLegRaise()
        
        # 1. Lift leg: Shoulder(0,0), Hip(0,1), Knee(0.2, 2) -> Hip Flexion
        # Simple Geometry: Vertical body.
        # Shoulder(0,0), Hip(0,1). Vertical line.
        # Knee at (0.5, 2) -> Lifted.
        
        # Let's construct specific angles.
        # HipAngle: Shoulder(0,0), Hip(0,10), Knee(0, 20) -> 180 deg (Standing/Lying flat)
        # Lift 30 deg: Knee at (sin(30)*10, 10 + cos(30)*10) ?
        # easier: Shoulder(0,0), Hip(1,0), Knee(2,0) -> 180.
        # Flex hip: Knee(2, 0.5)
        
        # Flat: S(0,0), H(1,0), K(2,0) -> 180.
        # Lifted 30 deg: H(1,0). Leg vector (1,0) rotated 30 deg.
        # Vector len 1. x = cos(30)=0.866, y=sin(30)=0.5. K=(1.866, 0.5).
        # Need coordinates for S, H, K.
        
        # Hip Angle: S(0,0), H(1,0), K(1+0.866, 0.5) -> Angle at H.
        # Vector HS = (-1, 0). Vector HK = (0.866, 0.5).
        # Angle is 180 - 30 = 150. Correct for 30 deg flexion.
        
        lms_lifted = create_mock_landmarks({
            12: (0,0,0), 
            24: (1,0,0), 
            26: (1.866, 0.5, 0),
            28: (2.732, 1.0, 0) # Ankle keeping knee straight (colinear with HK)
        })
        
        state, fb, reps = ex.update(lms_lifted)
        # 150 deg hip means 30 deg flexion. Min is 15. Max is 45. Should hold.
        self.assertEqual(state, "HOLD")
        
        # Hold complete
        ex.hold_start_time = datetime.now() - timedelta(seconds=3.1)
        state, fb, reps = ex.update(lms_lifted)
        self.assertEqual(state, "RELAX")
        self.assertEqual(reps, 1)

if __name__ == '__main__':
    unittest.main()
