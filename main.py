from flask import Flask, render_template, request, redirect
from datetime import datetime
import requests
import calendar

app = Flask(__name__)

# ====================================
# FIREBASE CONFIG
# ====================================
FIREBASE_URL = "https://jpotta-attendance-default-rtdb.asia-southeast1.firebasedatabase.app"

# ====================================
# HOME DASHBOARD
# ====================================
@app.route('/')
def dashboard():

    try:

        response = requests.get(
            f"{FIREBASE_URL}/cards.json"
        )

        data = response.json()

        students = []

        if data:

            for uid, details in data.items():

                if not isinstance(details, dict):
                    continue

                student = {
                    "uid": uid,
                    "name": details.get("name", "Unknown"),
                    "sessions": details.get("sessions", 0),
                    "plan": details.get("plan", 0),
                    "lastScan": details.get(
                        "lastScan",
                        "Never"
                    )
                }

                students.append(student)

        return render_template(
            "index.html",
            students=students
        )

    except Exception as e:
        return f"Error: {e}"

# ====================================
# ATTENDANCE PAGE
# ====================================
@app.route('/attendance')
def attendance():

    response = requests.get(
        f"{FIREBASE_URL}/cards.json"
    )

    data = response.json()

    students = []

    now = datetime.now()

    current_month = now.month
    current_year = now.year

    total_days = calendar.monthrange(
        current_year,
        current_month
    )[1]

    month_days = []

    for d in range(1, total_days + 1):

        day_string = (
            f"{d:02d}-"
            f"{current_month:02d}-"
            f"{current_year}"
        )

        month_days.append(day_string)

    if data:

        for uid, details in data.items():

            if not isinstance(details, dict):
                continue

            attendance_data = details.get(
                "attendance",
                {}
            )

            if not isinstance(
                attendance_data,
                dict
            ):
                attendance_data = {}

            last_scan = details.get(
                "lastScan",
                "Never"
            )

            # =========================
            # AUTO UPDATE ATTENDANCE
            # =========================
            if last_scan != "Never":

                scan_date = last_scan.split(" ")[0]

                if scan_date not in attendance_data:

                    attendance_data[
                        scan_date
                    ] = "P"

                    requests.patch(
                        f"{FIREBASE_URL}/cards/{uid}/attendance.json",
                        json={
                            scan_date: "P"
                        }
                    )

            present_count = len(attendance_data)

            students.append({

                "uid": uid,

                "name": details.get(
                    "name",
                    "Unknown"
                ),

                "attendance": attendance_data,

                "present_count": present_count
            })

    return render_template(
        "attendance.html",
        students=students,
        month_days=month_days,
        current_month=calendar.month_name[current_month],
        current_year=current_year
    )

# ====================================
# ADD STUDENT
# ====================================
@app.route('/add', methods=['POST'])
def add_student():

    uid = request.form.get(
        'uid'
    ).upper()

    name = request.form.get(
        'name'
    )

    sessions = int(
        request.form.get(
            'sessions'
        )
    )

    student_data = {

        "name": name,

        "sessions": sessions,

        "plan": sessions,

        "lastScan": "Never",

        "attendance": {}
    }

    requests.patch(
        f"{FIREBASE_URL}/cards/{uid}.json",
        json=student_data
    )

    return redirect('/')

# ====================================
# RENEW
# ====================================
@app.route('/renew/<uid>')
def renew_student(uid):

    response = requests.get(
        f"{FIREBASE_URL}/cards/{uid}.json"
    )

    student = response.json()

    if student:

        plan = student.get(
            "plan",
            0
        )

        requests.patch(
            f"{FIREBASE_URL}/cards/{uid}.json",
            json={
                "sessions": plan
            }
        )

    return redirect('/')

# ====================================
# DELETE
# ====================================
@app.route('/delete/<uid>')
def delete_student(uid):

    requests.delete(
        f"{FIREBASE_URL}/cards/{uid}.json"
    )

    return redirect('/')

# ====================================
# UPDATE SESSIONS
# ====================================
@app.route('/update_sessions/<uid>', methods=['POST'])
def update_sessions(uid):

    sessions = int(
        request.form.get(
            'sessions'
        )
    )

    requests.patch(
        f"{FIREBASE_URL}/cards/{uid}.json",
        json={
            "sessions": sessions
        }
    )

    return redirect('/')

# ====================================
# RUN APP
# ====================================
if __name__ == '__main__':

    app.run(
        host='0.0.0.0',
        port=8080,
        debug=True
    )