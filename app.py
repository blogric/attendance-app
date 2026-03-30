from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)

DB = "attendance.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS attendance (
        date TEXT PRIMARY KEY,
        status TEXT
    )''')

    conn.commit()
    conn.close()

init_db()

def get_present_count():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM attendance WHERE status='Present'")
    count = c.fetchone()[0]
    conn.close()
    return count

def calculate_rl():
    present = get_present_count()
    if present > 20:
        return (present - 20) // 2
    return 0

@app.route("/")
def index():
    today = datetime.now().strftime("%Y-%m-%d")

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT status FROM attendance WHERE date=?", (today,))
    data = c.fetchone()
    conn.close()

    status = data[0] if data else None

    return render_template("index.html",
                           today=today,
                           status=status,
                           rl=calculate_rl())

@app.route("/mark", methods=["POST"])
def mark():
    status = request.form["status"]
    date = request.form["date"]

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("INSERT OR REPLACE INTO attendance (date, status) VALUES (?,?)",
              (date, status))

    conn.commit()
    conn.close()

    return redirect("/")

@app.route("/leave", methods=["POST"])
def leave():
    leave_type = request.form["type"]
    start = datetime.strptime(request.form["start"], "%Y-%m-%d")
    end = datetime.strptime(request.form["end"], "%Y-%m-%d")

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    while start <= end:
        c.execute("INSERT OR REPLACE INTO attendance (date, status) VALUES (?,?)",
                  (start.strftime("%Y-%m-%d"), leave_type))
        start += timedelta(days=1)

    conn.commit()
    conn.close()

    return redirect("/")

@app.route("/calendar")
def calendar():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM attendance")
    data = c.fetchall()
    conn.close()

    return render_template("calendar.html", data=data)

if __name__ == "__main__":
    app.run(debug=True)
