<div align="center">

# Attend-AI

### Real-Time Face Recognition Attendance System

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-Latest-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![OpenCV](https://img.shields.io/badge/OpenCV-Latest-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)](https://opencv.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Accuracy](https://img.shields.io/badge/Accuracy-89.38%25-brightgreen?style=for-the-badge)](README.md)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-blue?style=for-the-badge)](README.md)

A web-based attendance management system that uses real-time facial recognition to automatically mark attendance — no hardware, no manual roll calls, no proxy fraud.

</div>

---

## Overview

AttendAI eliminates the inefficiency and dishonesty of manual attendance systems. Using a standard laptop webcam, it detects and identifies registered individuals in real time, automatically logging their attendance with timestamps — all through a clean web dashboard accessible from any browser on the network.

---

## Features

- **Real-Time Face Recognition** — detects and identifies multiple faces simultaneously from a live webcam feed
- **Automatic Attendance Logging** — marks attendance with name and timestamp instantly upon recognition
- **Anti-Duplicate Protection** — each person is recorded only once per session, regardless of how long they stay in frame
- **Face Registration** — register new students by uploading a face photo through the web dashboard
- **Session Management** — start new sessions, view live logs, and reset counters without losing historical records
- **Attendance Records** — view, filter, and export complete attendance history from a CSV database
- **Browser-Based** — accessible from any device on the network; no client-side installation required
- **Unknown Face Handling** — unrecognized faces are labeled "Unknown" and not recorded
- **Multi-Face Support** — handles up to 5 faces simultaneously in a single frame
- **REST API Architecture** — clean separation of frontend and backend via HTTP endpoints

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Language** | Python 3.11 |
| **Web Framework** | Flask |
| **Face Recognition** | face_recognition 1.3.0 (dlib-based) |
| **Computer Vision** | OpenCV (opencv-python) |
| **Deep Learning Model** | dlib 19.22+ (metric learning, 128-d embeddings) |
| **Video Streaming** | MJPEG over HTTP |
| **Data Storage** | CSV (attendance.csv) |
| **Frontend** | HTML, CSS, JavaScript |
| **Numerical Processing** | NumPy |
| **Image Handling** | Pillow |
| **Threading** | Python threading with Lock |
| **Configuration** | configparser |

---

## System Architecture

```
Browser (Any Device)
        │
        ▼
  Flask Web Server (app.py)
        │
        ├── /video_feed  ──────────► MJPEG Stream (OpenCV camera thread)
        ├── /load_faces  ──────────► face_recognition (load encodings from known_faces/)
        ├── /register_face ────────► Save image → known_faces/
        ├── /get_log ──────────────► Return session attendance log (JSON)
        ├── /get_records ──────────► Read attendance.csv → return all records
        └── /new_session ──────────► Clear session set + log

Camera Thread (background)
        │
        ├── Capture frame (OpenCV)
        ├── Resize → face detection (HOG/dlib)
        ├── Encode detected faces (128-d vectors)
        ├── Compare against known_faces encodings
        ├── If match → check attendance_set → log with timestamp
        └── Annotate frame → send to MJPEG stream
```

---

## Performance

| Metric | Value |
|---|---|
| Face Recognition Accuracy | **89%** (LFW benchmark) |
| Recognition Speed (per face) | < 200ms on Intel Core i5 |
| Stream Latency | < 500ms capture to browser |
| Max Simultaneous Faces | 5 faces per frame |
| Session Stability | 60+ minutes continuous operation |
| Test Cases | 6/6 PASSED |

---

## Requirements

### System Requirements

| Requirement | Specification |
|---|---|
| OS | Windows 10/11 (64-bit) or Ubuntu 20.04 LTS+ |
| Python | **3.11 only** (required for dlib wheel compatibility) |
| RAM | Minimum 4 GB (8 GB recommended) |
| Processor | Intel Core i3 2.0GHz minimum (i5 recommended) |
| Webcam | Built-in or USB webcam (720p minimum) |
| Storage | 2 GB free disk space |
| Browser | Chrome 90+, Firefox 88+, or Edge 90+ |

---

## Installation

### Step 1 — Install Visual C++ Build Tools (Windows Only)

1. Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Run the installer and select **"Desktop development with C++"** workload
3. Click **Install** and wait 10–20 minutes
4. **Restart your computer** after installation

> Linux users skip this step.

---

### Step 2 — Clone the Repository

```bash
git clone https://github.com/AdilFaraz-ML/AttendAI.git
cd AttendAI
```

---

### Step 3 — Create a Virtual Environment (Python 3.11)

**Windows (PowerShell):**
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
py -3.11 -m venv venv311
venv311\Scripts\Activate.ps1
```

**Linux/macOS:**
```bash
python3.11 -m venv venv311
source venv311/bin/activate
```

---

### Step 4 — Install Dependencies

```bash
pip install -r requirements.txt
```

> The `dlib` compilation step takes **5–15 minutes**. Do not close the terminal.

---

### Step 5 — Run the Application

```bash
python app.py
```

Open your browser and navigate to: **http://127.0.0.1:5000**

---

## Requirements.txt

```
flask
opencv-python
face-recognition==1.3.0
dlib>=19.22
numpy
Pillow
configparser
```

---

## Project Structure

```
AttendAI/
│
├── app.py                    # Main Flask application + camera thread + REST API
├── config.ini                # Configuration (camera index, paths, settings)
├── requirements.txt          # Python dependencies
├── attendance.csv            # Auto-generated attendance database
│
├── known_faces/              # Registered face images (JPG/PNG)
│   ├── student_name.jpg
│   └── ...
│
├── templates/
│   └── index.html            # Main dashboard (Jinja2)
│
└── static/
    ├── css/
    │   └── style.css         # Black-themed responsive stylesheet
    └── js/
        └── main.js           # Dashboard logic, polling, session controls
```

---

## Usage

### 1. Register a Student
- Enter the student's name in the **Register New Face** panel
- Upload a clear, well-lit, frontal face photo (JPG or PNG)
- Click **Register Face** — image is saved to `known_faces/`

### 2. Load Known Faces
- Click **Load Known Faces** to encode all registered face images into memory
- Always reload after registering new students

### 3. Start Attendance Session
- Click **Start Camera** to activate the webcam
- Students walk in front of the camera — they are automatically recognized and marked present with a timestamp

### 4. View Records
- Click **Records** to view the complete attendance history in a modal table
- All records are stored in `attendance.csv` (Name, DateTime)

### 5. New Session
- Click **New Session** to clear the current session log and reset the counter
- Historical records in `attendance.csv` are preserved

### 6. Stop Camera
- Click **Stop** to end the session when the class is complete

---

## Troubleshooting

| Problem | Cause | Solution |
|---|---|---|
| `dlib` fails to install | Visual C++ Build Tools not installed | Install Build Tools, select C++ workload, restart PC |
| `ModuleNotFoundError: cv2` | Virtual environment not activated | Run `Activate.ps1` before installing or running |
| Camera black screen / not working | Wrong camera index | Edit `config.ini`, change `CAMERA_INDEX` from `0` to `1` |
| Face not recognized | Poor image quality or faces not loaded | Use clear frontal photo; click **Load Known Faces** after adding |
| CSS not loading | Incorrect folder structure | Ensure `style.css` is in `static/css/` and `index.html` in `templates/` |
| Page not loading | Flask not running | Run `python app.py`; open `http://127.0.0.1:5000` |
| Slow recognition | Too many apps running | Close background applications; system handles up to 5 faces |

---

## Limitations

- Single webcam only (multi-camera not yet supported)
- CSV storage is not optimal for large-scale deployments
- No HTTPS or login system (LAN use only)
- Does not recognize masked faces
- No Android/iOS app

---


<div align="center">

Made with dedication by **Adil Faraz**

</div>
