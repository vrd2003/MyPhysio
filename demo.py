import cv2
import sys
import time
from src.pose_engine import PoseEngine
from src.exercises import QuadricepsSet, StraightLegRaise, HeelSlide, WallSquat, KneeExtensionROM

def display_menu():
    print("\n=== Physio Monitor ===")
    print("1. Quadriceps Set")
    print("2. Straight Leg Raise")
    print("3. Heel Slide")
    print("4. Wall Squat")
    print("5. Knee Extension ROM")
    print("q. Quit")
    print("======================")

def run_exercise(exercise_class):
    exercise = exercise_class()
    engine = PoseEngine()
    cap = cv2.VideoCapture(0)
    
    start_time = time.time()
    
    print(f"\nStarting {exercise.name}...")
    print("Press 'q' to end session.")
    print("Press 's' to toggle side (Left/Right) during Setup.")
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        results = engine.process_frame(frame)
        engine.draw_landmarks(frame, results)
        
        # Get frame dimensions
        h, w, _ = frame.shape
        
        if results.pose_landmarks:
            state, feedback, reps = exercise.update(results.pose_landmarks)
            
            # Helper to draw text with background for readability
            def draw_text(text, y_pos, color=(0,0,0), scale=0.7):
                cv2.putText(frame, text, (10, y_pos), 
                            cv2.FONT_HERSHEY_SIMPLEX, scale, (255, 255, 255), 4, cv2.LINE_AA)
                cv2.putText(frame, text, (10, y_pos), 
                            cv2.FONT_HERSHEY_SIMPLEX, scale, color, 2, cv2.LINE_AA)

            # Header
            cv2.rectangle(frame, (0, 0), (w, 80), (245, 117, 16), -1)
            cv2.putText(frame, f"{exercise.name}", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2, cv2.LINE_AA)
            cv2.putText(frame, f"Reps: {reps}", (w-120, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, cv2.LINE_AA)

            # State & Angle
            draw_text(f"State: {state}", 110, (0, 255, 0) if state != "SETUP" else (0, 165, 255))
            draw_text(f"Angle: {int(exercise.current_angle)}", 140, (255, 255, 0))
            
            # Side Info
            side_color = (0, 255, 255) if exercise.auto_side else (0, 0, 255)
            mode_str = "Auto" if exercise.auto_side else "Manual"
            draw_text(f"Side: {exercise.side} ({mode_str})", 170, side_color)

            # Feedback (Large and Central if Setup)
            if state == "SETUP":
                 cv2.putText(frame, f"{feedback}", (20, h//2), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
                 cv2.putText(frame, "Press 's' to swap side", (20, h-30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2, cv2.LINE_AA)
            else:
                 draw_text(f"{feedback}", 210, (255, 0, 0))

        else:
            cv2.putText(frame, "No Pose Detected", (10, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        cv2.imshow('Physio Monitor', frame)
        
        key = cv2.waitKey(10) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            if exercise.state == "SETUP":
                exercise.toggle_side()
                print(f"Side toggled to {exercise.side}")
            
    cap.release()
    cv2.destroyAllWindows()
    print(f"Session Ended. Total Reps: {exercise.reps}")

def main():
    while True:
        display_menu()
        choice = input("Select Exercise: ").strip()
        
        if choice == '1':
            run_exercise(QuadricepsSet)
        elif choice == '2':
            run_exercise(StraightLegRaise)
        elif choice == '3':
            run_exercise(HeelSlide)
        elif choice == '4':
            run_exercise(WallSquat)
        elif choice == '5':
            run_exercise(KneeExtensionROM)
        elif choice.lower() == 'q':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
