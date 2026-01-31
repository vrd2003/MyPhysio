import unittest
from src.geometry import calculate_angle

class TestGeometry(unittest.TestCase):
    def test_angle_90(self):
        # A(1,0), B(0,0), C(0,1) -> 90 degrees
        angle = calculate_angle([1,0], [0,0], [0,1])
        self.assertAlmostEqual(angle, 90.0)

    def test_angle_180(self):
        # A(1,0), B(0,0), C(-1,0) -> 180 degrees
        angle = calculate_angle([1,0], [0,0], [-1,0])
        self.assertAlmostEqual(angle, 180.0)
        
    def test_angle_45(self):
        # A(1,0), B(0,0), C(1,1) -> 45 degrees
        angle = calculate_angle([1,0], [0,0], [1,1])
        self.assertAlmostEqual(angle, 45.0)

if __name__ == '__main__':
    unittest.main()
