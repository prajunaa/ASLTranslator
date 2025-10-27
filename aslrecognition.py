"""
Hello, Arjun here!
This is an ASL Translator which recognizes the ASL alphabet and can be trained to recognize other gestures as well!
Additional gestures would be added using data_collector.py and asl_trainer.py.

The python, flask, and machine learning were all programmed and trained solely by myself, Arjun Prabhakaran.
The frontend design was all made by Satyanarayana Rudraraju.
The Speech Recognition component was made by Abhinav Balaganesh.

Here you will find my documentation/explanations scattered throughout, should you have any questions feel free to reach me at arjunaprabgamer@gmail.com
"""

import cv2, mediapipe as mp, argparse, joblib, numpy as np, time

print("Script started successfully")

try:
    clf = joblib.load("asl_letter_model.pkl")
    print("Model loaded successfully.")
except:
    print("Couldn't find 'asl_letter_model.pkl'. You haven't trained it yet.")
    exit()

word_list = []
latest_frame = None

#Grab arguments for the initialization of the camera.
def get_args():
    parser = argparse.ArgumentParser()

    #Which device is the camera recording from?
    parser.add_argument("--device", type=int, default=0)
    #Width of OpenCV's Window
    parser.add_argument("--width", type=int, default=960)
    #Height of OpenCV's Window
    parser.add_argument("--height", type=int, default=540)

    args = parser.parse_args()
    return args

def main():
    #Grabs arguments and initializes OpenCV camera as cap
    args = get_args()

    cap_device = args.device
    cap_width = args.width
    cap_height = args.height
    
    cap = cv2.VideoCapture(cap_device)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, cap_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cap_height)
    #Load Handtracking Model
    mp_hands = mp.solutions.hands
    
    #Initial Hand Tracking Model for 2 Hands and 
    #static_image_mode as false so that it can track across frames
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.4,
        min_tracking_confidence=0.3
    )
    
    #Adds drawing tools to help visualize
    mp_draw = mp.solutions.drawing_utils

    last_pred = None
    last_pred_time = 0

    #While true loop in order to infinitely read frames and scan until stopped by user.
    while True: 
        #checks whether the camera suceeds in capturing a frame and gives us the frame in variable frame
        success, frame = cap.read() 
        # Mirror the camera to look nicer :)
        frame = cv2.flip(frame, 1) 
        # OpenCV renders the frames in BGR but mediapipe recognizes only RGB so we convert the frame
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) 
        """
        Result is IMPORTANT to understand to replicate this program as most of the program is dependant on such.
        When mediapipe analzyes and processes each frame, the data is stored in result.
        Result contains 3 attributes: multi_hand_landmarks, multi_handedness, and multi_hand_world_landmarks
        We won't focus on the third attribute as it remains untouched for this project.

        multi_hand_landmarks is a list of NormalizedLandmarkList, each one containing 21 points for the x, y, and z of each joint/index
        multi_handedness is a list of ClassificationList, containing whether the hand is "Left" or "Right" with confidence scores.
        """
        result = hands.process(rgb)
        
        #Checks if hands were scanned, if hands weren't scanned and we tried running code the program will return an error for nonetype as theres 
        #no landmark data to pull when no hands are present. This simply makes sure we only pull when there ARE hands.
        if result.multi_hand_landmarks:
            #Add labels on each hand on whether it is right or left, countHand checks whether the hand is the first or second.
            countHand=0
            for hand_handedness in result.multi_handedness:
                index_zero = result.multi_hand_landmarks[countHand].landmark[mp_hands.HandLandmark.WRIST]
                #We grab the position of the hand and the size of the window to place Left/Right text is a spot near wrist.
                h, w, c = frame.shape
                cx, cy = (index_zero.x * w), (index_zero.y * h)
                
                if(hand_handedness.classification[0].label == "Right"):
                    cv2.putText(frame, "Right",(int(cx)-50, int(cy)+50),cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
                else:
                    cv2.putText(frame, "Left",(int(cx)-50, int(cy)+50),cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
                countHand = countHand+1
            
            #Simply draws where the lines and joints are, helps with visualization.
            for hand_landmarks in result.multi_hand_landmarks: 
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
        
        features = processing_landmarks(result, frame)
        if features is not None:
            try:
                pred = clf.predict(features)[0]
                cv2.putText(frame, f"Word: {''.join(word_list)}", (50, 160),cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                cv2.putText(frame,pred,(int(cx)-50, int(cy)-50),cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
                current_time = time.time()

                if pred != last_pred and (current_time - last_pred_time) > 5:  # Only add new letters to list when they change
                    word_list.append(pred)
                    last_pred = pred
                    last_pred_time = current_time #reset timer

                elif (current_time - last_pred_time) > 5:
                    word_list.append(pred)
                    last_pred_time = current_time  #reset timer
            except Exception as e:
                print("Prediction error:", e)    

        global latest_frame
        latest_frame = frame.copy()
 
    #Ends the program if q is pressed.
        cv2.imshow("Hand Tracker", frame) 
        if cv2.waitKey(1) & 0xFF == ord('q'): 
            break

    cap.release()
    cv2.destroyAllWindows()

def processing_landmarks(results, frame):
    h, w, c = frame.shape
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            true_landmarks = [[lmk.x * w, lmk.y * h] for lmk in hand_landmarks.landmark]
            wrist = true_landmarks[0]
            relative_landmarks = []
            for i in true_landmarks:
                relative_landmarks.append([(i[0]-wrist[0])/w, (i[1]-wrist[1])/h])
            return np.array(relative_landmarks).flatten().reshape(1, -1)
    return None

from flask import Flask, jsonify, Response
from flask_cors import CORS
import threading

app = Flask(__name__)
CORS(app)  # allow JavaScript to fetch from localhost

@app.route("/get_words")
def get_words():
    return jsonify({"text": "".join(word_list)})

@app.route("/clear_words", methods=["POST"])
def clear_words():
    global word_list
    word_list = []
    return jsonify({"status": "cleared"})

@app.route("/video_feed")
def video_feed():
    def generate():
        global latest_frame
        while True:
            if latest_frame is not None:
                success, buffer = cv2.imencode('.jpg', latest_frame)
                if success:
                    yield (b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            time.sleep(0.03)  # prevents 100% CPU usage
    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


def run_flask():
    app.run(host="0.0.0.0", port=5000)

if __name__ == '__main__':
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    main()