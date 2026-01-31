import numpy as np

def calculate_angle(a, b, c):
    """
    Calculates the angle between three points a, b, and c.
    a, b, c are (x, y) or (x, y, z) coordinates.
    The angle is calculated at point b.
    Returns angle in degrees.
    """
    a = np.array(a) # First
    b = np.array(b) # Mid
    c = np.array(c) # End
    
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    
    if angle > 180.0:
        angle = 360-angle
        
    return angle

def get_landmark_coords(landmarks, landmark_index, width=1, height=1):
    """
    Extracts coordinates from a MediaPipe landmark list.
    """
    # Check if landmarks is a list or a normalized landmark list object
    # For flexibility we assume it's an object with .landmark or a list of objects
    try:
        lm = landmarks.landmark[landmark_index]
        return [lm.x * width, lm.y * height, lm.z]
    except AttributeError:
        # Fallback if it's a simple list or dict
        pass
    return [0, 0, 0]

def get_landmark_visibility(landmarks, landmark_index):
    """
    Returns visibility score of a landmark.
    """
    try:
        return landmarks.landmark[landmark_index].visibility
    except AttributeError:
        return 0.0

def normalize_landmarks(landmarks):
    """
    Centers the pose at the hip midpoint and normalizes scale.
    Input: MediaPipe landmarks
    Output: Normalized numpy array of shape (33, 3)
    """
    # Placeholder for advanced normalization
    # For now, we often rely on angles which are scale invariant
    pass
