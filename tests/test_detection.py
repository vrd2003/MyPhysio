import unittest
from unittest.mock import MagicMock
import sys
import os

# Adjust path to find src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.exercises import Exercise

class MockLandmark:
    def __init__(self, x, y, z, visibility):
        self.x = x
        self.y = y
        self.z = z
        self.visibility = visibility

class MockLandmarks:
    def __init__(self, landmark_list):
        self.landmark = landmark_list

def create_mock_landmarks_with_vis(vis_dict):
    # defaulted to 0 visibility
    landmarks = [MockLandmark(0,0,0, 0.0) for _ in range(33)]
    for idx, vis in vis_dict.items():
        landmarks[idx] = MockLandmark(0, 0, 0, vis)
    return MockLandmarks(landmarks)

class TestLegDetection(unittest.TestCase):
    def test_detect_left_side(self):
        ex = Exercise("Test")
        # Left side (23, 25, 27) highly visible
        # Right side (24, 26, 28) low visibility
        lms = create_mock_landmarks_with_vis({
            23: 0.9, 25: 0.9, 27: 0.9,
            24: 0.1, 26: 0.1, 28: 0.1
        })
        side = ex.detect_active_side(lms)
        self.assertEqual(side, "LEFT")

    def test_detect_right_side(self):
        ex = Exercise("Test")
        lms = create_mock_landmarks_with_vis({
            23: 0.1, 25: 0.1, 27: 0.1,
            24: 0.9, 26: 0.9, 28: 0.9
        })
        side = ex.detect_active_side(lms)
        self.assertEqual(side, "RIGHT")

if __name__ == '__main__':
    unittest.main()
