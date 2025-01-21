import cv2
import dlib
import numpy as np
import pandas as pd
from scipy.spatial import distance

def eye_aspect_ratio(eye):
    A = distance.euclidean(eye[1], eye[5])
    B = distance.euclidean(eye[2], eye[4])
    C = distance.euclidean(eye[0], eye[3])
    return (A + B) / (2.0 * C)

def draw_rectangle(frame, shape, color=(0, 255, 0)):
    leftEye = shape[36:42]
    rightEye = shape[42:48]
    leftEyeHull = cv2.convexHull(leftEye)
    rightEyeHull = cv2.convexHull(rightEye)
    cv2.drawContours(frame, [leftEyeHull], -1, color, 1)
    cv2.drawContours(frame, [rightEyeHull], -1, color, 1)

# Initialize Dlib's face detector and landmark predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# Start webcam
cap = cv2.VideoCapture(0)

# Blink detection parameters
EYE_AR_THRESH = 0.3
EYE_AR_CONSEC_FRAMES = 3

# Initialize counters
blink_counter = 0
frame_counter = 0

# Data recording
blink_data = []

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector(gray, 0)

        for face in faces:
            shape = predictor(gray, face)
            shape = np.array([[p.x, p.y] for p in shape.parts()])

            draw_rectangle(frame, shape)

            leftEye = shape[42:48]
            rightEye = shape[36:42]

            leftEAR = eye_aspect_ratio(leftEye)
            rightEAR = eye_aspect_ratio(rightEye)

            ear = (leftEAR + rightEAR) / 2.0
            print(f"EAR: {ear}")


            if ear < EYE_AR_THRESH:
                frame_counter += 1
            else:
                if frame_counter >= EYE_AR_CONSEC_FRAMES:
                    blink_counter += 1
                    blink_data.append({'Blink': blink_counter})
                frame_counter = 0

        cv2.putText(frame, f"Blink Count: {blink_counter}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.imshow("Frame", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    blink_data = [{'Total Blinks': blink_counter}]
    pd.DataFrame(blink_data).to_csv('data.csv', index=False)

    cap.release()
    cv2.destroyAllWindows()
