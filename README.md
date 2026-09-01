# Face Recognition-Based Attendance System

## 📌 Project Overview
A web-based attendance system for schools using face recognition. Teachers mark attendance by scanning a student's face through the browser's webcam; the principal has full control over attendance records and user management.

## 🚀 Live demo

[https://face-recognition-attendance.onrender.com](https://face-recognition-attendance.onrender.com)

Try it with the seeded demo accounts:

| Role | Username | Password |
|---|---|---|
| Teacher (Class 1, Class 2) | `arush` | `p1uJhSGn` |
| Teacher (Class 3, Class 4) | `pranav` | `pass123` |
| Principal | `vipinjain` | `dkEm41kt` |

> All data in this repo (student names, photos, parent emails, account passwords) is sample/demo data for portfolio purposes, not real students. Free-tier hosting spins down after inactivity, so the first request after a while may take 30-60 seconds.

## 🔥 Features

### 1. User Authentication
Login system with separate access for **Principal** and **Teacher**, credentials stored in `data/users.csv`.

### 2. Teacher Dashboard
- Select a class and date before marking attendance
- Capture and store a new student's face photo
- Scan a face via webcam and mark attendance automatically
- View attendance, plain and by percentage
- Edit past attendance records

### 3. Principal Dashboard
- Manage teachers and students
- Manage class slots
- View and edit attendance across all classes

### 4. Face Recognition
Detects faces with an OpenCV Haar cascade, then recognizes them with OpenCV's
built-in **LBPH (Local Binary Patterns Histograms)** face recognizer, trained
on-the-fly from each class's stored photos. (The original version of this
project used `dlib` for face embeddings, but `dlib` has no prebuilt wheels
for any platform - installing it means compiling from source with CMake and
a C++ toolchain, which is slow and unreliable on free-tier hosting. LBPH
ships as a normal installable wheel via `opencv-contrib-python-headless` and
needs no multi-hundred-megabyte model file, at the cost of being a somewhat
less discriminating recognizer than a deep embedding model - reasonable for
a small class roster, and a big win for actually being deployable.)

### 5. Attendance Storage
Attendance is stored per class per day:
```
data/attendance/{class_name}/{date}.csv
```

### 6. Email Notifications
Optionally emails parents when their child is marked present, if `EMAIL_USER`/`EMAIL_PASS` environment variables are set (Gmail SMTP). Without them, attendance marking still works - emails are just silently skipped.

## 📂 Project Structure

```
Face-recognition-attendance-system/
├── app.py                          # Flask app entry point
├── email_notifications.py          # Optional parent email notifications
├── requirements.txt
├── Procfile
├── routes/
│   ├── auth.py                     # Login/logout
│   ├── teacher.py                  # Face capture, recognition, attendance marking
│   └── principal.py                # User/class management
├── templates/
│   ├── auth/, common/, teacher/, principal/
├── static/                         # CSS, JS, images
└── data/
    ├── users.csv                   # Account credentials (demo data)
    ├── students.csv                # Student roster (demo data)
    ├── faces/{class}/               # Stored face photos (demo data)
    ├── attendance/{class}/{date}.csv
    └── haarcascade_frontalface_default.xml
```

## 🚀 Local setup

```bash
pip install -r requirements.txt
python app.py
```

Open [http://127.0.0.1:5000/](http://127.0.0.1:5000/).

Optional environment variables:
- `SECRET_KEY` — Flask session signing key. Without it, a random key is generated at startup (sessions won't survive a restart, but nothing is hardcoded).
- `EMAIL_USER` / `EMAIL_PASS` — Gmail account for sending parent notifications.
- `FLASK_DEBUG` — set to `true` for local development only. Never enable this on a public deployment.

## 🤝 Contribution & Support
For any issues, feel free to report bugs or suggest features.

---
**Made for Schools | Automated & Secure Attendance System** 🎓 ✅
