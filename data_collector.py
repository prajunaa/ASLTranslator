import cv2
import mediapipe as mp
import csv
import numpy as np

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.4)
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)

print("Press a key (A-Z) while showing the corresponding sign. Press 'q' to quit.")


"""
When training the model with normal landmarks, 
the X and Y aspect of the landmarks makes the predictions 
consider where in the frame the hand is as a factor of the sign.
To circumvent this, I made all the joints as points relative to the wrist or index 0,
therefore, the points would help the prediction be based on orientation of the hand rather than
where they were in the X, Y of the camera. 

It starts with the NormalizedListLandmark format which I changed into a list of [[x,y], [x,y] and so on so forth] for each joint
based on the size of the window, eg index 0 might have been [504, 126]

Then I changed that to be the relative position to index 0, so if index 1 or Thumb_CNC was at [510, 200], the new relative position would be at
[504-510, 126-200]

Then I divided the X values over the width of the camera and Y values by the height to make it relative regardless of window size.
The final list looks something like:
[[relativex 0, relativey 0], [relativex 1, relativey 1] so on so forth until joint 21]
then we flatten into a numpy array to feed for training.
"""
def processing_landmarks(results, frame):
    h, w, c = frame.shape
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            true_landmarks = [[lmk.x * w, lmk.y * h] for lmk in hand_landmarks.landmark]
            wrist = true_landmarks[0]
            relative_landmarks = []
            for i in true_landmarks:
                relative_landmarks.append([(i[0]-wrist[0])/w, (i[1]-wrist[1])/h])
            return np.array(relative_landmarks).flatten()
    return None

while True:
    success, frame = cap.read()
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    cv2.imshow("ASL Data Collector", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord('0'):
        break

    if key==32 or 65 <= key <= 90 or 97 <= key <= 122:  #check if key a-z
        letter = chr(key).upper()
        vector = processing_landmarks(results, frame)
        if vector is not None:
            with open("asl_dataset.csv", "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([letter] + vector.tolist())
            print(f"Saved sample for '{letter}'")

cap.release()
cv2.destroyAllWindows()
