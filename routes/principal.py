from flask import Blueprint, render_template, request, redirect, url_for, session, send_file, jsonify
import os
import csv
import random
import string

principal_bp = Blueprint('principal', __name__, template_folder='../templates/principal')
USER_CSV = os.path.join(os.getcwd(), 'data', 'users.csv')
ATTENDANCE_DIR = os.path.join(os.getcwd(), 'data', 'attendance')

def ensure_users_csv():
    os.makedirs(os.path.dirname(USER_CSV), exist_ok=True)
    if not os.path.exists(USER_CSV):
        with open(USER_CSV, 'w', newline='') as file:
            csv.writer(file).writerow(['unique_code', 'username', 'password', 'role', 'assigned_class'])

def generate_password(length=10):
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choices(characters, k=length))

def generate_unique_code(role):
    prefix = "PR-" if role == "principal" else "T-"
    last_code = 1000
    if os.path.exists(USER_CSV):
        with open(USER_CSV, 'r') as file:
            reader = list(csv.reader(file))[1:]
            codes = [int(row[0].split('-')[1]) for row in reader if row[0].startswith(prefix)]
            if codes:
                last_code = max(codes) + 1
    return f"{prefix}{last_code}"

def update_assigned_classes(user_code, new_classes):
    updated_rows, found = [], False
    with open(USER_CSV, "r") as file:
        rows = list(csv.reader(file))
    for row in rows:
        if row[0] == user_code and row[3] == "teacher":
            row[4] = new_classes
            found = True
        updated_rows.append(row)
    if found:
        with open(USER_CSV, "w", newline="") as file:
            csv.writer(file).writerows(updated_rows)
    return found

@principal_bp.route('/dashboard')
def dashboard():
    if session.get('role') != 'principal':
        return redirect(url_for('auth.login'))
    available_classes = [d for d in os.listdir(ATTENDANCE_DIR) if os.path.isdir(os.path.join(ATTENDANCE_DIR, d))]
    return render_template('principal/dashboard.html', available_classes=available_classes)

@principal_bp.route('/update_classes', methods=['POST'])
def update_classes():
    if session.get('role') != 'principal':
        return jsonify({"success": False, "message": "Unauthorized access!"})

    data = request.json
    user_code = data.get("user_code", "").strip()
    assigned_classes = data.get("assigned_classes", "")

    if not user_code or not assigned_classes:
        return jsonify({"success": False, "message": "Invalid data!"})

    success = update_assigned_classes(user_code, assigned_classes)
    if success:
        return jsonify({"success": True, "message": "Classes updated successfully!"})
    else:
        return jsonify({"success": False, "message": "Teacher not found!"})


@principal_bp.route('/manage_users', methods=['GET', 'POST'])
def manage_users():
    if session.get('role') != 'principal':
        return redirect(url_for('auth.login'))
    
    ensure_users_csv()

    if request.method == 'POST':
        data = request.json
        action = data.get('action')

        if action == "add":
            username = data.get('username', '').strip()
            role = data.get('role', '')
            assigned_classes = ";".join(data.get('assigned_classes', [])) if role == "teacher" else "N/A"

            if not username or not role:
                return jsonify({"success": False, "message": "Invalid data!"})

            unique_code = generate_unique_code(role)
            password = generate_password()

            with open(USER_CSV, 'a', newline='') as file:
                csv.writer(file).writerow([unique_code, username, password, role, assigned_classes])

            return jsonify({"success": True, "message": f"Faculty {username} added successfully!"})


        elif action == "remove":
            user_code = data.get('user_code', '').strip()
            if not user_code:
                return jsonify({"success": False, "message": "Invalid user code!"})

            updated_rows, found = [], False
            with open(USER_CSV, "r") as file:
                rows = list(csv.reader(file))

            for row in rows:
                if row[0] == user_code:
                    found = True
                else:
                    updated_rows.append(row)

            if found:
                with open(USER_CSV, "w", newline="") as file:
                    csv.writer(file).writerows(updated_rows)
                return jsonify({"success": True, "message": "User removed successfully!"})
            else:
                return jsonify({"success": False, "message": "User not found!"})

    users = []
    if os.path.exists(USER_CSV):
        with open(USER_CSV, 'r') as file:
            users = list(csv.reader(file))[1:]

    available_classes = [d for d in os.listdir(ATTENDANCE_DIR) if os.path.isdir(os.path.join(ATTENDANCE_DIR, d))]

    return render_template('principal/manage_users.html', users=users, available_classes=available_classes)

@principal_bp.route('/attendance', methods=['GET', 'POST'])
def attendance():
    if session.get('role') != 'principal':
        return redirect(url_for('auth.login'))
    
    selected_class, date = request.args.get('class_name'), request.args.get('date')
    attendance_records, classes = [], []
    if os.path.exists(ATTENDANCE_DIR):
        classes = [d for d in os.listdir(ATTENDANCE_DIR) if os.path.isdir(os.path.join(ATTENDANCE_DIR, d))]
        if selected_class and date:
            file_path = os.path.join(ATTENDANCE_DIR, selected_class, f"{date}.csv")
            if os.path.isfile(file_path):
                with open(file_path, 'r') as file:
                    attendance_records = [dict(zip(["student_name", "reg_no", "status", "time"], row)) for row in list(csv.reader(file))[1:]]
    
    if request.method == 'POST' and selected_class and date:
        updated_attendance = {k: v for k, v in request.form.items() if k != 'csrf_token'}
        file_path = os.path.join(ATTENDANCE_DIR, selected_class, f"{date}.csv")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Student Name", "Reg No", "Status", "Time"])
            for row in attendance_records:
                writer.writerow([row['student_name'], row['reg_no'], updated_attendance.get(row['student_name'], row['status']), row['time']])
        return redirect(url_for('principal.attendance', class_name=selected_class, date=date))
    
    return render_template('principal/attendance.html', classes=classes, selected_class=selected_class, date=date, attendance_records=attendance_records)

@principal_bp.route('/download_attendance')
def download_attendance():
    if session.get('role') != 'principal':
        return redirect(url_for('auth.login'))
    file_path = os.path.join(ATTENDANCE_DIR, request.args.get('class_name', ''), f"{request.args.get('date', '')}.csv")
    return send_file(file_path, as_attachment=True, download_name=f"{os.path.basename(file_path)}", mimetype="text/csv") if os.path.isfile(file_path) else redirect(url_for('principal.attendance'))
