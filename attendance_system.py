from flask import Flask, render_template, Response, jsonify, request
import cv2
import numpy as np
import os
import csv
from datetime import datetime
import threading

app = Flask(__name__)

KNOWN_FACES_DIR = 'known_faces'
ATTENDANCE_CSV_PATH = 'attendance.csv'

known_face_encodings = []
known_face_names = []
attendance_set = set()
camera_running = False
camera_thread = None
current_frame = None
frame_lock = threading.Lock()
status_message = "System ready. Load faces to begin."
session_log = []

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
recognizer = cv2.face.LBPHFaceRecognizer_create()
label_map = {}
is_trained = False


def load_known_faces():
    global known_face_encodings, known_face_names, status_message, recognizer, label_map, is_trained

    if not os.path.exists(KNOWN_FACES_DIR):
        os.makedirs(KNOWN_FACES_DIR)
        status_message = f"Created '{KNOWN_FACES_DIR}' folder."
        return False, status_message

    faces = []
    labels = []
    label_map = {}
    label_id = 0

    for filename in os.listdir(KNOWN_FACES_DIR):
        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            image_path = os.path.join(KNOWN_FACES_DIR, filename)
            try:
                img = cv2.imread(image_path)
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                detected = face_cascade.detectMultiScale(gray, 1.1, 5)
                if len(detected) > 0:
                    x, y, w, h = detected[0]
                    face_roi = gray[y:y+h, x:x+w]
                    face_roi = cv2.resize(face_roi, (200, 200))
                    name = os.path.splitext(filename)[0]
                    if name not in label_map.values():
                        label_map[label_id] = name
                        label_id += 1
                    current_id = [k for k, v in label_map.items() if v == name][0]
                    faces.append(face_roi)
                    labels.append(current_id)
            except Exception as e:
                print(f"Error loading {filename}: {e}")

    if len(faces) == 0:
        status_message = "No valid face images found."
        is_trained = False
        return False, status_message

    recognizer.train(faces, np.array(labels))
    is_trained = True
    known_face_names = list(label_map.values())
    status_message = f"Loaded {len(label_map)} face(s) successfully."
    return True, status_message


def mark_attendance(name):
    global session_log
    if name not in attendance_set:
        now = datetime.now()
        dt_string = now.strftime('%Y-%m-%d %H:%M:%S')

        if not os.path.exists(ATTENDANCE_CSV_PATH):
            with open(ATTENDANCE_CSV_PATH, 'w', newline='') as f:
                csv.writer(f).writerow(['Name', 'DateTime'])

        with open(ATTENDANCE_CSV_PATH, 'a', newline='') as f:
            csv.writer(f).writerow([name, dt_string])

        attendance_set.add(name)
        entry = {'name': name, 'time': dt_string}
        session_log.append(entry)
        return entry
    return None


def camera_loop():
    global camera_running, current_frame, status_message
    import time

    video_capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not video_capture.isOpened():
        video_capture = cv2.VideoCapture(0)

    video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    time.sleep(2)

    if not video_capture.isOpened():
        status_message = "Error: Could not open camera."
        camera_running = False
        return

    status_message = "Camera active. Scanning for faces..."

    while camera_running:
        ret, frame = video_capture.read()
        if not ret:
            time.sleep(0.1)
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 5)

        for (x, y, w, h) in faces:
            name = "Unknown"
            if is_trained:
                face_roi = gray[y:y+h, x:x+w]
                face_roi = cv2.resize(face_roi, (200, 200))
                label_id, confidence = recognizer.predict(face_roi)
                print(f"Confidence: {confidence}, Label: {label_id}")
                if confidence < 80:
                    name = label_map.get(label_id, "Unknown")

            color = (255, 255, 255) if name != "Unknown" else (80, 80, 80)
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            cv2.rectangle(frame, (x, y+h-30), (x+w, y+h), color, cv2.FILLED)
            cv2.putText(frame, name, (x+6, y+h-8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 0), 2)

            if name != "Unknown":
                mark_attendance(name)

        with frame_lock:
            current_frame = frame.copy()

    video_capture.release()
    status_message = "Camera stopped."
    camera_running = False


def generate_frames():
    while True:
        with frame_lock:
            frame = current_frame

        if frame is None:
            blank = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(blank, "No Camera Feed", (180, 240),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (80, 80, 80), 2)
            frame = blank

        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' +
               buffer.tobytes() + b'\r\n')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/api/load_faces', methods=['POST'])
def api_load_faces():
    success, message = load_known_faces()
    return jsonify({'success': success, 'message': message,
                    'count': len(known_face_names), 'names': known_face_names})


@app.route('/api/start_camera', methods=['POST'])
def api_start_camera():
    global camera_running, camera_thread
    if camera_running:
        return jsonify({'success': False, 'message': 'Camera already running.'})
    camera_running = True
    camera_thread = threading.Thread(target=camera_loop, daemon=True)
    camera_thread.start()
    return jsonify({'success': True, 'message': 'Camera started.'})


@app.route('/api/stop_camera', methods=['POST'])
def api_stop_camera():
    global camera_running
    camera_running = False
    return jsonify({'success': True, 'message': 'Camera stopped.'})


@app.route('/api/new_session', methods=['POST'])
def api_new_session():
    global attendance_set, session_log
    attendance_set.clear()
    session_log.clear()
    return jsonify({'success': True, 'message': 'New session started.'})


@app.route('/api/status')
def api_status():
    return jsonify({
        'camera_running': camera_running,
        'status': status_message,
        'faces_loaded': len(known_face_names),
        'log': session_log,
        'attendance_count': len(attendance_set)
    })


@app.route('/api/attendance')
def api_attendance():
    records = []
    if os.path.exists(ATTENDANCE_CSV_PATH):
        with open(ATTENDANCE_CSV_PATH, 'r') as f:
            records = list(csv.DictReader(f))
    return jsonify({'records': records})


@app.route('/api/upload_face', methods=['POST'])
def api_upload_face():
    if 'file' not in request.files or 'name' not in request.form:
        return jsonify({'success': False, 'message': 'Missing file or name.'})
    file = request.files['file']
    name = request.form['name'].strip()
    if not name:
        return jsonify({'success': False, 'message': 'Name cannot be empty.'})
    if not os.path.exists(KNOWN_FACES_DIR):
        os.makedirs(KNOWN_FACES_DIR)
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ['.jpg', '.jpeg', '.png']:
        return jsonify({'success': False, 'message': 'Only JPG/PNG images allowed.'})
    file.save(os.path.join(KNOWN_FACES_DIR, f"{name}{ext}"))
    return jsonify({'success': True, 'message': f"Face saved for '{name}'."})


if __name__ == '__main__':
    if not os.path.exists(KNOWN_FACES_DIR):
        os.makedirs(KNOWN_FACES_DIR)
    app.run(debug=True, threaded=True, use_reloader=False)