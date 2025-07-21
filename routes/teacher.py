from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
import os
import csv
from datetime import datetime
import base64
import numpy as np
import cv2
import dlib
from email_notifications import send_attendance_email

teacher_bp = Blueprint("teacher", __name__, template_folder="../templates/teacher")
DATA_DIR = "data"
ATTENDANCE_DIR = os.path.join(DATA_DIR, "attendance")
FACES_DIR = os.path.join(DATA_DIR, "faces")
USER_CSV = os.path.join(DATA_DIR, "users.csv")
STUDENTS_CSV = os.path.join(DATA_DIR, "students.csv")
LANDMARK_MODEL_PATH = "data/shape_predictor_68_face_landmarks.dat"
FACE_REC_MODEL_PATH = "data/dlib_face_recognition_resnet_model_v1.dat"

face_cascade = cv2.CascadeClassifier("data/haarcascade_frontalface_default.xml")
predictor = dlib.shape_predictor(LANDMARK_MODEL_PATH)
face_rec = dlib.face_recognition_model_v1(FACE_REC_MODEL_PATH)

os.makedirs(ATTENDANCE_DIR, exist_ok=True)
os.makedirs(FACES_DIR, exist_ok=True)

def ensure_users_csv():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(USER_CSV):
        with open(USER_CSV, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['user_code', 'username', 'password', 'role', 'assigned_class'])

def get_teacher_assigned_classes(username):
    with open(USER_CSV, "r") as file:
        for row in csv.DictReader(file):
            if row["username"] == username and row["role"] == "teacher":
                return row["assigned_class"].split(";") if row["assigned_class"] else []
    return []

def get_class_attendance(class_name, date):
    file_path = os.path.join(ATTENDANCE_DIR, class_name, f"{date}.csv")
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r") as file:
        return list(csv.reader(file))

def process_student_name(student_name):
    base_name, _ = os.path.splitext(student_name)
    parts = base_name.rsplit("_", 1)
    name = " ".join(word.capitalize() for word in parts[0].split())
    reg_no = parts[1] if len(parts) > 1 else "Unknown"
    return name, reg_no

def check_attendance(student_name, class_name, date, reg_no):
    file_path = os.path.join(ATTENDANCE_DIR, class_name, f"{date}.csv")
    if os.path.exists(file_path):
        with open(file_path, mode='r', newline='') as file:
            reader = csv.reader(file)
            next(reader, None)
            return any(row[0] == reg_no and row[1] == student_name for row in reader)
    return False

def manage_attendance(class_name, student_name, reg_no, date):
    file_path = os.path.join(ATTENDANCE_DIR, class_name, f"{date}.csv")
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    file_exists = os.path.exists(file_path)
    if not file_exists:
        with open(file_path, mode='w', newline='') as file:
            csv.writer(file).writerow(["Reg No", "Student Name", "Status", "Date-Time"])

    if check_attendance(student_name, class_name, date, reg_no):
        return jsonify({"message": "Student is already present", "status": 201}), 201

    with open(file_path, mode='a', newline='') as file:
        csv.writer(file).writerow([reg_no, student_name, "Present", datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        send_attendance_email(student_name, reg_no, "Present", date)

    return jsonify({"message": "Attendance marked successfully", "status": 200}), 200

def get_face_encoding(image):
    if image is None or image.size == 0:
        return None

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)

    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    if len(faces) == 0:
        return None

    x, y, w, h = faces[0]
    dlib_rect = dlib.rectangle(x, y, x + w, y + h)
    shape = predictor(gray, dlib_rect)
    rgb_img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    face_encoding = np.array(face_rec.compute_face_descriptor(rgb_img, shape))

    return face_encoding

def load_faces(class_name):
    faces_path = os.path.join(FACES_DIR, class_name)
    if not os.path.exists(faces_path):
        return [], []

    encodings = []
    names = []
    for file in os.listdir(faces_path):
        img_path = os.path.join(faces_path, file)
        img = cv2.imread(img_path)
        face_enc = get_face_encoding(img)
        if face_enc is not None:
            encodings.append(face_enc)
            names.append(file)

    return encodings, names

def recognize_face(face_encoding, class_name):
    known_encodings, known_names = load_faces(class_name)
    if not known_encodings:
        return "unknown", ""

    distances = np.linalg.norm(known_encodings - face_encoding, axis=1)
    best_match_index = np.argmin(distances)

    if distances[best_match_index] > 0.4:
        return "unknown", ""

    student_name_with_regno = known_names[best_match_index]
    name, reg_no = process_student_name(student_name_with_regno)
    return name, reg_no

def save_student_details(student_name, reg_no, class_name, parent_email):
    students = []
    reg_nos = set()
    if os.path.exists(STUDENTS_CSV):
        with open(STUDENTS_CSV, "r", newline="") as file:
            reader = csv.reader(file)
            next(reader, None)
            students = [row for row in reader if row]
            reg_nos = {row[0] for row in students}

    if reg_no in reg_nos:
        return

    student_name = student_name.capitalize()
    students.append([reg_no, student_name, class_name, parent_email])
    students.sort(key=lambda x: x[0])

    with open(STUDENTS_CSV, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Reg No", "Name", "Class", "Parent Email"]) 
        writer.writerows(students)  

@teacher_bp.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "username" not in session or session.get("role") != "teacher":
        return redirect(url_for("auth.login"))

    assigned_classes = get_teacher_assigned_classes(session["username"])
    selected_class = request.form.get("class_name") if request.method == "POST" else None
    selected_date = request.form.get("date") if request.method == "POST" else None

    return render_template("teacher/dashboard.html", assigned_classes=assigned_classes, selected_class=selected_class, selected_date=selected_date)

@teacher_bp.route("/mark_attendance/<class_name>/<date>", methods=["GET", "POST"])
def mark_attendance(class_name, date):
    if "username" not in session or session.get("role") != "teacher":
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        student_name_with_reg = request.form.get("student_name")
        if student_name_with_reg:
            student_name, reg_no = process_student_name(student_name_with_reg)
            records = get_class_attendance(class_name, date)
            if not any(row[0] == student_name for row in records):
                file_path = os.path.join(ATTENDANCE_DIR, class_name, f"{date}.csv")
                file_exists = os.path.isfile(file_path)
                with open(file_path, "a", newline="") as file:
                    writer = csv.writer(file)
                    if not file_exists:
                        writer.writerow(["Student Name", "Reg No", "Status", "Time"])
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    writer.writerow([student_name, reg_no, "Present", current_time])
                send_attendance_email(student_name, "Present", date)

    return render_template("teacher/mark_attendance.html", class_name=class_name, date=date, attendance_records=get_class_attendance(class_name, date))

@teacher_bp.route("/view_attendance/<class_name>/<date>", methods=["GET", "POST"])
def view_attendance(class_name, date):
    if not class_name or not date:
        return render_template("dashboard.html")

    file_path = os.path.join(ATTENDANCE_DIR, class_name, f"{date}.csv")
    attendance_records = get_class_attendance(class_name, date)

    if os.path.isfile(file_path):
        with open(file_path, 'r') as file:
            reader = csv.reader(file)
            attendance_records = [
                {"reg_no": row[0], "student_name": row[1], "status": row[2], "time": row[3]}
                for row in list(reader)[1:]
            ]

    return render_template("teacher/view_attendance.html", attendance_records=attendance_records, class_name=class_name, date=date)

@teacher_bp.route("/add_student/<class_name>", methods=["GET", "POST"])
def add_student(class_name):
    student_dir = os.path.join(FACES_DIR, class_name)
    os.makedirs(student_dir, exist_ok=True)

    if request.method == "POST":
        student_name = request.form.get("student_name", "").strip()
        reg_no = request.form.get("reg_no", "").strip()
        image = request.files.get("image")

        if student_name and reg_no and image:
            image_filename = f"{student_name}_{reg_no}.jpg"
            image_path = os.path.join(student_dir, image_filename)
            image.save(image_path)
            flash(f"Student {student_name} ({reg_no}) image saved.", "success")

        return redirect(url_for("teacher.add_student", class_name=class_name))

    students = os.listdir(student_dir)
    return render_template("teacher/add_student.html", class_name=class_name, students=students)

@teacher_bp.route('/save_student_face', methods=['POST'])
def save_student_face():
    student_name = request.form.get('student_name')
    reg_no = request.form.get('reg_no')
    image = request.files.get('image')
    class_name = request.form.get('class_name')
    parent_email = request.form.get('parent_email')

    if not student_name or not reg_no or not image:
        return jsonify({'message': 'Missing required fields'}), 400

    try:
        image_filename = f"data/faces/{class_name}/{student_name}_{reg_no}.jpg"
        image.save(image_filename)
        save_student_details(student_name, reg_no, class_name, parent_email)
        return jsonify({'message': 'Student face saved successfully!'}), 200
    except Exception as e:
        return jsonify({'message': 'Error saving image: ' + str(e)}), 500

@teacher_bp.route("/scan_face", methods=["POST"])
def scan_face():
    try:
        data = request.json["image"]
        if not data:
            return jsonify({"status": 400, "message": "No image received!"})

        _, encoded = data.split(",", 1)
        img_data = base64.b64decode(encoded)
        img = cv2.imdecode(np.frombuffer(img_data, np.uint8), cv2.IMREAD_COLOR)

        if img is None:
            return jsonify({"status": 400, "message": "Image decoding failed!"})

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        if len(faces) == 0:
            return jsonify({"status": 400, "message": "No Face Detected!"})

        x, y, w, h = faces[0]
        dlib_rect = dlib.rectangle(x, y, x + w, y + h)
        shape = predictor(gray, dlib_rect)
        face_encoding = np.array(face_rec.compute_face_descriptor(img, shape))

        if face_encoding is None:
            return jsonify({"status": 400, "message": "Could not extract face encoding!"})

        class_name = request.json.get("class_name", "")
        student_name, reg_no = recognize_face(face_encoding, class_name)

        if student_name == "unknown":
            return jsonify({"status": 400, "message": "Student not recognized!"})

        return jsonify({"status": 200, "student_name": student_name, "reg_no": reg_no})

    except Exception as e:
        return jsonify({"status": 500, "message": str(e)})
    
@teacher_bp.route("/confirm_attendance", methods=["POST"])
def confirm_attendance():
    data = request.json
    student_name, reg_no, class_name, date = data.get("student_name"), data.get("reg_no"), data.get("class_name"), data.get("date")

    if not all([student_name, reg_no, class_name, date]):
        return jsonify({"message": "Missing required fields!", "status": 400})

    response = manage_attendance(class_name, student_name, reg_no, date)
    return response
