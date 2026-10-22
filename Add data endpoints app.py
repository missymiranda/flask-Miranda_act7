import sqlite3
import os
from pathlib import Path
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)
DB_PATH = Path(__file__).with_name("students.db")


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_database():
    """Create the database if it does not exist yet (useful for local testing/deployment)."""
    conn = get_db_connection()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                name TEXT NOT NULL,
                program TEXT NOT NULL,
                year INTEGER NOT NULL,
                section TEXT NOT NULL
            )
        """)
        count = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
        if count == 0:
            sample_students = [
                ("2024-1001", "Karol Vincent Pedregosa", "BSA", 4, "ANSCI"),
                ("2024-1002", "Liza Java", "BEED", 1, "D"),
                ("2024-1003", "Paul Joseph Miranda", "BSCS", 2, "A"),
                ("2024-1004", "Issa Kailah Javier", "BSHM", 3, "C"),
                ("2024-1005", "Rizza Anthea Malacad", "BSED-Filipino", 4, "B"),
            ]
            conn.executemany("""
                INSERT INTO students (student_id, name, program, year, section)
                VALUES (?, ?, ?, ?, ?)
            """, sample_students)
        conn.commit()
    finally:
        conn.close()


@app.route("/")
def home():
    ensure_database()
    return render_template("index.html")


@app.route("/student")
def student():
    return jsonify({
        "student_id": "2024-00076",
        "name": "Missy Miranda",
        "program": "BSIT",
        "year": 3,
        "section": "3B"
    })


@app.route("/hello")
def hello():
    name = request.args.get("name", "Student")
    return jsonify({"message": f"Hello, {name}!"})


@app.route("/campus")
def campus():
    return jsonify({
        "campus": "San Enrique-Campus",
        "location": "Iloilo",
        "status": "Open",
        "type": "University Campus"
    })


@app.route("/grade")
def grade():
    score = request.args.get("score", type=float)
    if score is None:
        return jsonify({"error": "Please provide a valid score."}), 400
    if not 0 <= score <= 100:
        return jsonify({"error": "Score must be between 0 and 100."}), 400
    if score >= 90:
        remarks = "Excellent"
    elif score >= 80:
        remarks = "Very Good"
    elif score >= 75:
        remarks = "Passed"
    else:
        remarks = "Needs Improvement"
    return jsonify({"subject": "IT 3120", "grade": score, "remarks": remarks})


@app.route("/students")
def get_students():
    ensure_database()
    conn = get_db_connection()
    try:
        rows = conn.execute("SELECT * FROM students ORDER BY id").fetchall()
        return jsonify([dict(row) for row in rows])
    except sqlite3.Error:
        app.logger.exception("Could not retrieve students")
        return jsonify({"error": "Could not retrieve students"}), 500
    finally:
        conn.close()


@app.route("/students/<int:id>")
def get_student_by_id(id):
    ensure_database()
    conn = get_db_connection()
    try:
        row = conn.execute("SELECT * FROM students WHERE id = ?", (id,)).fetchone()
        if row is None:
            return jsonify({"error": "Student not found"}), 404
        return jsonify(dict(row))
    except sqlite3.Error:
        app.logger.exception("Could not retrieve student")
        return jsonify({"error": "Could not retrieve student"}), 500
    finally:
        conn.close()


@app.route("/students/section/<section>")
def get_students_by_section(section):
    ensure_database()
    conn = get_db_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM students WHERE UPPER(section) = UPPER(?) ORDER BY id",
            (section,)
        ).fetchall()
        return jsonify([dict(row) for row in rows])
    except sqlite3.Error:
        app.logger.exception("Could not retrieve students by section")
        return jsonify({"error": "Could not retrieve students by section"}), 500
    finally:
        conn.close()


if __name__ == "__main__":
    ensure_database()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
