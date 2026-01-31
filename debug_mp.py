import mediapipe as mp
print(f"MediaPipe path: {mp.__path__}")
try:
    print(f"Has solutions: {'solutions' in dir(mp)}")
    import mediapipe.python.solutions as solutions
    print("Direct import of solutions worked")
except ImportError as e:
    print(f"Direct import failed: {e}")
except Exception as e:
    print(f"Error: {e}")
