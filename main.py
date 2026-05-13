import requests
from flask import Flask, render_template, request, redirect
from datetime import datetime

app = Flask(__name__)

    # ====================================
    # FIREBASE CONFIG
    # ====================================
FIREBASE_URL = "https://jpotta-attendance-default-rtdb.asia-southeast1.firebasedatabase.app/"

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
                'index.html',
                students=students
            )

        except Exception as e:
            return f"Error: {e}"

    # ====================================
    # ADD STUDENT
    # ====================================
@app.route('/add', methods=['POST'])
def add_student():

        uid = request.form.get('uid').upper()

        name = request.form.get('name')

        sessions = int(
            request.form.get('sessions')
        )

        student_data = {
            "name": name,
            "sessions": sessions,
            "plan": sessions,
            "lastScan": "Never"
        }

        requests.patch(
            f"{FIREBASE_URL}/cards/{uid}.json",
            json=student_data
        )

        return redirect('/')

    # ====================================
    # RENEW PLAN
    # ====================================
@app.route('/renew/<uid>')
def renew_student(uid):

        response = requests.get(
            f"{FIREBASE_URL}/cards/{uid}.json"
        )

        student = response.json()

        if student:

            plan = student.get("plan", 0)

            update_data = {
                "sessions": plan
            }

            requests.patch(
                f"{FIREBASE_URL}/cards/{uid}.json",
                json=update_data
            )

        return redirect('/')

    # ====================================
    # DELETE STUDENT
    # ====================================
@app.route('/delete/<uid>')
def delete_student(uid):

        requests.delete(
            f"{FIREBASE_URL}/cards/{uid}.json"
        )

        return redirect('/')

    # ====================================
    # MANUAL SESSION EDIT
    # ====================================
@app.route('/update_sessions/<uid>', methods=['POST'])
def update_sessions(uid):

        sessions = int(
            request.form.get('sessions')
        )

        requests.patch(
            f"{FIREBASE_URL}/cards/{uid}.json",
            json={
                "sessions": sessions
            }
        )

        return redirect('/')

    # ====================================
    # UPDATE LAST SCAN
    # (CALLED BY ESP8266 LATER)
    # ====================================
@app.route('/mark_scan/<uid>')
def mark_scan(uid):

        current_time = datetime.now().strftime(
            "%d-%m-%Y %H:%M:%S"
        )

        requests.patch(
            f"{FIREBASE_URL}/cards/{uid}.json",
            json={
                "lastScan": current_time
            }
        )

        return "OK"

    # ====================================
    # RUN APP
    # ====================================
if __name__ == '__main__':

        app.run(
            host='0.0.0.0',
            port=8080,
            debug=True
        )