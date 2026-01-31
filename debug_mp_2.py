import sys
import mediapipe as mp
print(f"MP dir: {dir(mp)}")
try:
    from mediapipe.python import solutions
    print("Found solutions in mediapipe.python")
except ImportError:
    print("Could not find solutions in mediapipe.python")
