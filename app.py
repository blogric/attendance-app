from flask import Flask, render_template, request, redirect, jsonify
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
    return (present - 20) // 2 if present > 20 else 0

@app.route("/")
def index():
    today = datetime.now().strftime("%Y-%m-%d")

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT status FROM attendance WHERE date=?", (today,))
    row = c.fetchone()
    conn.close()

    status = row[0] if row else None

    return render_template("index.html",
                           today=today,
                           status=status,
                           rl=calculate_rl(),
                           present=get_present_count())

@app.route("/mark", methods=["POST"])
def mark():
    date = request.form["date"]
    status = request.form["status"]

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO attendance VALUES (?,?)", (date, status))
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
        c.execute("INSERT OR REPLACE INTO attendance VALUES (?,?)",
                  (start.strftime("%Y-%m-%d"), leave_type))
        start += timedelta(days=1)

    conn.commit()
    conn.close()

    return redirect("/calendar")

@app.route("/calendar-data")
def calendar_data():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM attendance")
    data = c.fetchall()
    conn.close()
    return jsonify(data)

if __name__ == "__main__":
    app.run()
