from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import os
import csv

auth_bp = Blueprint("auth", __name__, template_folder="templates/auth")
USER_CSV = os.path.join("data", "users.csv")

# Ensure users.csv exists with the proper structure
def ensure_users_csv():
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(USER_CSV):
        with open(USER_CSV, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["user_code", "username", "password", "role", "assigned_class"])

# Login route
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    ensure_users_csv()
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        with open(USER_CSV, "r") as file:
            reader = csv.DictReader(file)
            user_found = False
            for row in reader:
                if row["username"] == username:
                    user_found = True
                    if row["password"] == password:
                        session["username"] = username
                        session["role"] = row["role"]
                        session["assigned_class"] = row.get("assigned_class", "").split(";")
                        session["user_code"] = row["user_code"]
                        session.permanent = True

                        if row["role"] == "teacher":
                            return redirect(url_for("teacher.dashboard"))
                        elif row["role"] == "principal":
                            return redirect(url_for("principal.dashboard"))
                    else:
                        flash("Incorrect password. Please try again.", "danger")
                        return redirect(url_for("auth.login"))
            
            if not user_found:
                flash("User does not exist. Please check your username.", "danger")
                return redirect(url_for("auth.login"))

    return render_template("auth/login.html")

# Logout route
@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
