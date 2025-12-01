from scipy.spatial import distance
from imutils import face_utils
from pygame import mixer
import imutils
import dlib
import cv2
import requests
import geocoder
import time

# ---------------- SETTINGS ----------------
UBIDOTS_TOKEN = "BBUS-woznaG7gX6VLDXL8T6clJoNhobPZZp"
DEVICE_LABEL = "drowsiness_tracker"  # Your Ubidots device name

# ---------------- ESP32 SETUP ----------------
import serial
try:
     esp32 = serial.Serial(port='COM7', baudrate=9600, timeout=0.1)
     print("✅ Connected to ESP32")
except serial.SerialException:
     esp32 = None
     print("⚠️ ESP32 not connected, skipping hardware alerts")

  # For now, no ESP32

# ---------------- AUDIO ALERT ----------------
mixer.init()
mixer.music.load(r"C:\Users\jagad\Downloads\music.wav")

# ---------------- DROWSINESS SETTINGS ----------------
EYE_AR_THRESH = 0.25
EYE_AR_CONSEC_FRAMES = 20

# ---------------- FACE DETECTOR ----------------
print("Loading facial landmark predictor...")
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(r"C:\Users\jagad\Downloads\shape_predictor_68_face_landmarks.dat")
(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_68_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_68_IDXS["right_eye"]

# ---------------- VIDEO STREAM ----------------
print("Starting video stream...")
cap = cv2.VideoCapture(0)
frame_counter = 0
alarm_on = False

# ---------------- FUNCTIONS ----------------
def eye_aspect_ratio(eye):
    A = distance.euclidean(eye[1], eye[5])
    B = distance.euclidean(eye[2], eye[4])
    C = distance.euclidean(eye[0], eye[3])
    return (A + B) / (2.0 * C)

def send_ubidots_alert(lat, lon):
    """Send location + SMS-style message to Ubidots"""
    maps_link = f"https://www.google.com/maps?q={lat},{lon}"
    message = f"⚠️ Driver asleep! Location: {maps_link}"
    payload = {
        "position": {"value": 1, "context": {"lat": lat, "lng": lon}},
        "alert_message": {"value": 1, "context": {"text": message}}
    }
    url = f"https://industrial.api.ubidots.com/api/v1.6/devices/{DEVICE_LABEL}/"
    headers = {"X-Auth-Token": UBIDOTS_TOKEN, "Content-Type": "application/json"}
    try:
        response = requests.post(url=url, headers=headers, json=payload)
        if response.status_code in [200, 201]:
            print("✅ Ubidots alert sent")
        else:
            print(f"❌ Ubidots failed: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"❌ Ubidots error: {e}")

# ---------------- MAIN LOOP ----------------
while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame = imutils.resize(frame, width=450)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    rects = detector(gray, 0)

    for rect in rects:
        shape = predictor(gray, rect)
        shape = face_utils.shape_to_np(shape)
        leftEye = shape[lStart:lEnd]
        rightEye = shape[rStart:rEnd]
        leftEAR = eye_aspect_ratio(leftEye)
        rightEAR = eye_aspect_ratio(rightEye)
        ear = (leftEAR + rightEAR) / 2.0

        if ear < EYE_AR_THRESH:
            frame_counter += 1
            if frame_counter >= EYE_AR_CONSEC_FRAMES:
                if not alarm_on:
                    alarm_on = True
                    print("🚨 DROWSINESS DETECTED!")

                    # Play alarm sound
                    

                    # Optional ESP32 signal
                    if esp32:
                        esp32.write(b'A')
                        print("📡 Sent alert to ESP32")
                        

                    # Ubidots alert
                    try:
                        location = geocoder.ip('me')
                        if location.latlng:
                            lat, lon = location.latlng
                            print(f"🌍 Location: {lat}, {lon}")
                            send_ubidots_alert(lat, lon)
                        else:
                            print("⚠️ Could not get location")
                    except Exception as e:
                        print(f"❌ Location error: {e}")

                cv2.putText(frame, "DROWSINESS ALERT!", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        else:
            frame_counter = 0
            alarm_on = False

    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
print("✅ Script finished")
