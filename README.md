<<<<<<< HEAD

# Face Recognition-Based Attendance System

## 📌 Project Overview
This is a web-based attendance system for schools (Class 1 to 10) using face recognition. It allows teachers to mark attendance automatically using OpenCV and Face-Recognition, while the principal has full control over attendance and user management.

## 🔥 Features
### **1️⃣ User Authentication**
- Login system with separate access for **Principal** and **Teacher**
- Credentials stored in `users.csv`

### **2️⃣ Teacher Dashboard**
- **Slot Selection** before proceeding
- **Student Management**: Capture and store student face data
- **Attendance Marking**: Automatic face recognition
- **Attendance Viewing**: Normal & percentage-wise
- **Attendance Editing**: Modify past records

### **3️⃣ Principal Dashboard**
- **User Management**: Add/remove teachers & students
- **Slot Management**: Add/remove slots
- **Attendance Control**: Manually take attendance
- **Attendance Viewing**: Normal & percentage-wise
- **Attendance Editing**: Modify past records

### **4️⃣ Face Recognition System**
- Uses **OpenCV & face-recognition** for real-time attendance marking

### **5️⃣ Attendance Storage**
- Attendance stored in structured format:
  ```
  data/attendance/{teacher_name}/{class_name}/{date}/attendance.csv
  ```

### **6️⃣ Email Notifications**
- Sends automated emails to parents for daily attendance

### **7️⃣ Web-Based Interface**
- **Flask-based web app**
- **HTML, CSS, Bootstrap** for responsive UI

## 📂 Project Structure
```
attendance_system/
│── app.py                    # Main Flask App
│── config.py                 # Configuration settings
│── helper.py                 # Utility functions
│── requirements.txt          # Dependencies
│  
├── routes/                   # Backend logic
│   ├── auth.py               # Authentication
│   ├── teacher.py            # Teacher functionalities
│   ├── principal.py          # Principal functionalities
│  
├── templates/                # Frontend HTML Pages
│   ├── base.html             # Common layout
│   ├── navbar.html           # Navigation bar
│   ├── footer.html           # Footer
│   ├── login.html            # Login Page
│   ├── teacher_dashboard.html # Teacher Dashboard
│   ├── principal_dashboard.html # Principal Dashboard
│   ├── attendance.html       # View Attendance
│   ├── select_slot.html      # Slot Selection
│   ├── manage_slots.html     # Slot Management
│  
├── static/                   # CSS, JS, Images
│   ├── images/               # Icons/Logos
│   ├── style.css             # Stylesheet
│   ├── script.js             # JavaScript
│  
├── data/                     # Storage
│   ├── users.csv             # User Credentials
│   ├── database.json         # User Details
│   ├── attendance/           # Attendance Records
│  
├── face_recognition/         # Face Recognition
│   ├── capture_faces.py      # Capture & Store Faces
│   ├── recognize_faces.py    # Detect & Mark Attendance
│  
├── email_notification.py     # Send Emails to Parents
```

## 🚀 Installation & Setup
### **1️⃣ Install Dependencies**
```bash
pip install -r requirements.txt
```

### **2️⃣ Run the Application**
```bash
python app.py
```

### **3️⃣ Access Web App**
Open browser and go to:  
🔗 `http://127.0.0.1:5000/`

## 🤝 Contribution & Support
For any issues, feel free to **report bugs or suggest features!**

---
**Made for Schools | Automated & Secure Attendance System** 🎓 ✅
=======
# face-recognition-attendance-system
>>>>>>> 4494959d369b09e32ba50d3bdb7c8d0c1fdfb58a
