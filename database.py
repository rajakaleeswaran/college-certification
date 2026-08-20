"""
database.py - SQLite Database Layer for Student Certification Portal
Handles schema creation, migrations, seed data, and all CRUD operations
for Students, Mentors (Staff), HOD/Admin, Certificates, and Analytics.
"""

import sqlite3
import os
import json
from datetime import datetime, timedelta
import random
import hashlib

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'student_portal.db')


def get_db():
    """Get a database connection with row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def hash_password(password):
    """Simple SHA-256 password hashing."""
    return hashlib.sha256(password.encode()).hexdigest()


def init_db():
    """Initialize database schema and apply safe migrations."""
    conn = get_db()
    c = conn.cursor()

    # ── Users table ──────────────────────────────────────────────
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        department TEXT,
        role TEXT NOT NULL DEFAULT 'student',
        year INTEGER DEFAULT 1,
        mentor_id INTEGER,
        designation TEXT DEFAULT 'Assistant Professor',
        avatar_url TEXT,
        created_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (mentor_id) REFERENCES users(id)
    )''')

    # ── Certificates table ───────────────────────────────────────
    c.execute('''CREATE TABLE IF NOT EXISTS certificates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        issue_date TEXT,
        cert_type TEXT,
        skills TEXT,
        file_path TEXT,
        photo_path TEXT,
        additional_photos TEXT,
        source_url TEXT,
        status TEXT DEFAULT 'pending',
        reviewer_id INTEGER,
        review_feedback TEXT,
        reviewed_at TEXT,
        integrity_score REAL DEFAULT 0,
        integrity_details TEXT,
        verification_code TEXT,
        created_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (reviewer_id) REFERENCES users(id)
    )''')

    # ── Notifications table ──────────────────────────────────────
    c.execute('''CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        body TEXT NOT NULL,
        category TEXT DEFAULT 'general',
        priority TEXT DEFAULT 'normal',
        target_role TEXT DEFAULT 'all',
        target_department TEXT DEFAULT 'All',
        target_user_id INTEGER,
        author_id INTEGER,
        is_read INTEGER DEFAULT 0,
        created_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (author_id) REFERENCES users(id)
    )''')

    # ── ML Predictions table ─────────────────────────────────────
    c.execute('''CREATE TABLE IF NOT EXISTS ml_predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        prediction_type TEXT NOT NULL,
        result_json TEXT NOT NULL,
        created_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')

    conn.commit()

    # ── Safe Column Migrations ──────────────────────────────────
    user_cols = [row[1] for row in c.execute("PRAGMA table_info(users)").fetchall()]
    if 'year' not in user_cols:
        c.execute("ALTER TABLE users ADD COLUMN year INTEGER DEFAULT 1")
    if 'mentor_id' not in user_cols:
        c.execute("ALTER TABLE users ADD COLUMN mentor_id INTEGER REFERENCES users(id)")
    if 'designation' not in user_cols:
        c.execute("ALTER TABLE users ADD COLUMN designation TEXT DEFAULT 'Assistant Professor'")

    notif_cols = [row[1] for row in c.execute("PRAGMA table_info(notifications)").fetchall()]
    if 'target_department' not in notif_cols:
        c.execute("ALTER TABLE notifications ADD COLUMN target_department TEXT DEFAULT 'All'")
    if 'author_id' not in notif_cols:
        c.execute("ALTER TABLE notifications ADD COLUMN author_id INTEGER REFERENCES users(id)")

    cert_cols = [row[1] for row in c.execute("PRAGMA table_info(certificates)").fetchall()]
    if 'verification_code' not in cert_cols:
        c.execute("ALTER TABLE certificates ADD COLUMN verification_code TEXT")

    conn.commit()

    # If users table is empty, seed with initial realistic demo data
    if c.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
        _seed_data(conn)
    else:
        # Ensure existing sample students have mentors and years assigned
        _patch_seed_mentors_and_years(conn)

    conn.close()


def _patch_seed_mentors_and_years(conn):
    """Ensure existing seed students have mentors and realistic academic years."""
    c = conn.cursor()
    staff1 = c.execute("SELECT id FROM users WHERE username='STAFF101'").fetchone()
    staff2 = c.execute("SELECT id FROM users WHERE username='STAFF102'").fetchone()
    
    staff1_id = staff1[0] if staff1 else None
    staff2_id = staff2[0] if staff2 else None

    # Update staff designations
    if staff1_id:
        c.execute("UPDATE users SET designation='Associate Professor & Student Mentor' WHERE id=?", (staff1_id,))
    if staff2_id:
        c.execute("UPDATE users SET designation='Assistant Professor & Student Mentor' WHERE id=?", (staff2_id,))
    c.execute("UPDATE users SET designation='Head of Department (HOD)' WHERE username='ADMIN001'")

    # Assign student years and mentors if null or default
    student_updates = [
        ('2023CSE1234', 3, staff1_id), # Raseena - Year 3, Mentor: Dr. Anitha
        ('2023CSE1235', 2, staff1_id), # Arun - Year 2, Mentor: Dr. Anitha
        ('2023ECE2001', 4, staff2_id), # Priya - Year 4, Mentor: Prof. Rajesh
        ('2023MEC3001', 1, staff2_id), # Ashik - Year 1, Mentor: Prof. Rajesh
        ('2023CSE1236', 3, staff1_id), # Sneha - Year 3, Mentor: Dr. Anitha
    ]
    for uname, yr, mid in student_updates:
        if mid:
            c.execute("UPDATE users SET year=?, mentor_id=? WHERE username=? AND (mentor_id IS NULL OR year IS NULL OR year=1)", (yr, mid, uname))

    conn.commit()


def _seed_data(conn):
    """Insert comprehensive initial data."""
    c = conn.cursor()

    # 1. Staff & Admin users
    staff_users = [
        ('STAFF101', hash_password('staff123'), 'Dr. Anitha Menon', 'anitha.staff@college.edu', '+91-9876500001', 'Computer Science and Engineering', 'staff', 'Associate Professor & Student Mentor'),
        ('STAFF102', hash_password('staff123'), 'Prof. Rajesh Nair', 'rajesh.staff@college.edu', '+91-9876500002', 'Electronics and Communication', 'staff', 'Assistant Professor & Student Mentor'),
        ('ADMIN001', hash_password('admin123'), 'Dr. K. Suresh Kumar', 'hod.cse@college.edu', '+91-9876500000', 'Computer Science and Engineering', 'admin', 'Head of Department (HOD)'),
    ]
    c.executemany("INSERT INTO users (username, password_hash, full_name, email, phone, department, role, designation) VALUES (?,?,?,?,?,?,?,?)", staff_users)

    staff1_id = c.execute("SELECT id FROM users WHERE username='STAFF101'").fetchone()[0]
    staff2_id = c.execute("SELECT id FROM users WHERE username='STAFF102'").fetchone()[0]

    # 2. Students with distinct years & assigned mentors
    students = [
        ('2023CSE1234', hash_password('password123'), 'Raseena Fathima', 'raseena@college.edu', '+91-9876543210', 'Computer Science and Engineering', 'student', 3, staff1_id),
        ('2023CSE1235', hash_password('password123'), 'Arun Kumar', 'arun@college.edu', '+91-9876543211', 'Computer Science and Engineering', 'student', 2, staff1_id),
        ('2023ECE2001', hash_password('password123'), 'Priya Sharma', 'priya@college.edu', '+91-9876543212', 'Electronics and Communication', 'student', 4, staff2_id),
        ('2023MEC3001', hash_password('password123'), 'Mohammed Ashik', 'ashik@college.edu', '+91-9876543213', 'Mechanical Engineering', 'student', 1, staff2_id),
        ('2023CSE1236', hash_password('password123'), 'Sneha Raj', 'sneha@college.edu', '+91-9876543214', 'Computer Science and Engineering', 'student', 3, staff1_id),
    ]
    c.executemany("INSERT INTO users (username, password_hash, full_name, email, phone, department, role, year, mentor_id) VALUES (?,?,?,?,?,?,?,?,?)", students)

    u1_id = c.execute("SELECT id FROM users WHERE username='2023CSE1234'").fetchone()[0]
    u2_id = c.execute("SELECT id FROM users WHERE username='2023CSE1235'").fetchone()[0]
    u3_id = c.execute("SELECT id FROM users WHERE username='2023ECE2001'").fetchone()[0]
    u4_id = c.execute("SELECT id FROM users WHERE username='2023MEC3001'").fetchone()[0]
    u5_id = c.execute("SELECT id FROM users WHERE username='2023CSE1236'").fetchone()[0]

    now = datetime.now()
    cert_data = [
        # user 1 (Raseena, Year 3, Mentor: STAFF101)
        (u1_id, 'Advanced Web Development', 'Full-stack web application development covering React, Node.js, RESTful microservices, and containerization.', '2025-05-12', 'Technical', 'HTML,CSS,JavaScript,React,Node.js,REST API', None, None, None, 'https://coursera.org/verify/WEB-DEV-892', 'approved', staff1_id, 'Verified with official platform registry. Comprehensive curriculum demonstrated.', (now - timedelta(days=90)).isoformat(), 92.5, json.dumps({"metadata_consistency": {"score": 25, "max": 25, "pct": 100}, "skill_relevancy": {"score": 23, "max": 25, "pct": 92}, "issuer_trust": {"score": 18, "max": 20, "pct": 90}, "temporal_validity": {"score": 14.5, "max": 15, "pct": 96.7}, "content_authenticity": {"score": 12, "max": 15, "pct": 80}}), 'CERT-2025-CSE-9211'),
        (u1_id, 'Python for Data Science', 'Comprehensive data analysis, statistical modeling, data visualization with Pandas, Matplotlib, and Scikit-Learn.', '2025-06-05', 'AI/ML', 'Python,NumPy,Pandas,Matplotlib,Machine Learning', None, None, None, 'https://datacamp.com/statement-of-accomplishment/cert/PY-883', 'approved', staff1_id, 'Verified. Demonstrated strong foundational data analysis competency.', (now - timedelta(days=60)).isoformat(), 88.3, json.dumps({"metadata_consistency": {"score": 24, "max": 25, "pct": 96}, "skill_relevancy": {"score": 22, "max": 25, "pct": 88}, "issuer_trust": {"score": 17, "max": 20, "pct": 85}, "temporal_validity": {"score": 14, "max": 15, "pct": 93.3}, "content_authenticity": {"score": 11.3, "max": 15, "pct": 75.3}}), 'CERT-2025-CSE-8832'),
        (u1_id, 'AWS Cloud Practitioner', 'Official Amazon Web Services foundational cloud computing architectural principles and services.', '2025-04-10', 'Cloud', 'AWS,Cloud Computing,EC2,S3,IAM', None, None, None, 'https://aws.amazon.com/verification/AWS-CP-1029', 'approved', staff1_id, 'AWS official credential verified via Amazon CertMetrics registry.', (now - timedelta(days=120)).isoformat(), 97.1, json.dumps({"metadata_consistency": {"score": 25, "max": 25, "pct": 100}, "skill_relevancy": {"score": 24, "max": 25, "pct": 96}, "issuer_trust": {"score": 19.6, "max": 20, "pct": 98}, "temporal_validity": {"score": 14.5, "max": 15, "pct": 96.7}, "content_authenticity": {"score": 14, "max": 15, "pct": 93.3}}), 'CERT-2025-CSE-1029'),
        (u1_id, 'Docker & Kubernetes Essentials', 'Container orchestration, CI/CD automated deployments, and microservice mesh configurations.', '2025-06-28', 'DevOps', 'Docker,Kubernetes,DevOps,Microservices,CI/CD', None, None, None, 'https://edx.org/verify/dk-441', 'pending', None, None, None, 88.0, json.dumps({"metadata_consistency": {"score": 23, "max": 25, "pct": 92}, "skill_relevancy": {"score": 23, "max": 25, "pct": 92}, "issuer_trust": {"score": 17, "max": 20, "pct": 85}, "temporal_validity": {"score": 14, "max": 15, "pct": 93.3}, "content_authenticity": {"score": 11, "max": 15, "pct": 73.3}}), 'CERT-2025-CSE-4410'),
        (u1_id, 'Machine Learning with TensorFlow', 'Deep learning architectures, convolutional networks, and natural language classification.', '2025-07-15', 'AI/ML', 'TensorFlow,Keras,Deep Learning,Neural Networks,Python', None, None, None, 'https://coursera.org/verify/tf-991', 'pending', None, None, None, 91.5, json.dumps({"metadata_consistency": {"score": 24, "max": 25, "pct": 96}, "skill_relevancy": {"score": 24, "max": 25, "pct": 96}, "issuer_trust": {"score": 18, "max": 20, "pct": 90}, "temporal_validity": {"score": 14.5, "max": 15, "pct": 96.7}, "content_authenticity": {"score": 11, "max": 15, "pct": 73.3}}), 'CERT-2025-CSE-9912'),

        # user 2 (Arun, Year 2, Mentor: STAFF101)
        (u2_id, 'Java Enterprise Development', 'Spring Boot 3, Spring Security, Hibernate ORM, and enterprise architectural design patterns.', '2025-05-20', 'Technical', 'Java,Spring Boot,Hibernate,REST API,Microservices', None, None, None, 'https://oracle.com/verify/java-88', 'approved', staff1_id, 'Verified against Oracle registry.', (now - timedelta(days=85)).isoformat(), 91.0, None, 'CERT-2025-CSE-2021'),
        (u2_id, 'React Native Mobile Dev', 'Cross-platform mobile application architecture, state management, and native bridge APIs.', '2025-07-01', 'Technical', 'React Native,JavaScript,Mobile,iOS,Android', None, None, None, None, 'pending', None, None, None, 78.5, None, 'CERT-2025-CSE-2023'),

        # user 3 (Priya, Year 4, Mentor: STAFF102)
        (u3_id, 'VLSI Design Fundamentals', 'FPGA programming, Verilog HDL synthesis, and timing closure for digital circuits.', '2025-04-15', 'Technical', 'VLSI,FPGA,Verilog,Digital Design', None, None, None, None, 'approved', staff2_id, 'ECE Department lab verification completed.', (now - timedelta(days=100)).isoformat(), 89.2, None, 'CERT-2025-ECE-3001'),
        (u3_id, 'IoT Systems Development', 'Internet of Things sensor networks, MQTT protocols, and embedded Arduino integration.', '2025-05-30', 'Technical', 'IoT,Arduino,Raspberry Pi,Sensors,Embedded', None, None, None, None, 'pending', None, None, None, 87.5, None, 'CERT-2025-ECE-3002'),

        # user 4 (Ashik, Year 1, Mentor: STAFF102)
        (u4_id, 'AutoCAD Professional', 'Parametric 3D mechanical modeling, assembly drawing, and tolerance specifications.', '2025-03-10', 'Design', 'AutoCAD,3D Modeling,CAD,Mechanical Design', None, None, None, None, 'approved', staff2_id, 'Autodesk accredited certification verified.', (now - timedelta(days=160)).isoformat(), 93.0, None, 'CERT-2025-MEC-4001'),

        # user 5 (Sneha, Year 3, Mentor: STAFF101)
        (u5_id, 'Data Analytics with R', 'Statistical data modeling, exploratory data analysis, and publication-quality visualization with ggplot2.', '2025-06-20', 'AI/ML', 'R,Statistics,Data Visualization,ggplot2', None, None, None, 'https://datacamp.com/verify/r-102', 'approved', staff1_id, 'DataCamp statement verified.', (now - timedelta(days=45)).isoformat(), 86.7, None, 'CERT-2025-CSE-5001'),
        (u5_id, 'Natural Language Processing', 'Transformers, BERT embeddings, and semantic parsing with Hugging Face and spaCy.', '2025-07-10', 'AI/ML', 'NLP,spaCy,Transformers,Python,Text Mining', None, None, None, None, 'pending', None, None, None, 84.0, None, 'CERT-2025-CSE-5002'),
    ]
    c.executemany("""INSERT INTO certificates
        (user_id, title, description, issue_date, cert_type, skills, file_path, photo_path, additional_photos, source_url, status, reviewer_id, review_feedback, reviewed_at, integrity_score, integrity_details, verification_code)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", cert_data)

    notifs = [
        ('Submit April Certifications for Institutional Audit', 'Please ensure all professional certifications completed in April 2025 are uploaded by May 5th for institutional internal review and placement records.', 'deadline', 'high', 'student', 'All', None, staff1_id, 0, (now - timedelta(days=112)).isoformat()),
        ('Best Wishes for Final Year Capstone Evaluations', 'Faculty and department heads extend best wishes to all final year engineering students for their upcoming project evaluations.', 'wishes', 'normal', 'all', 'All', None, staff1_id, 0, (now - timedelta(days=114)).isoformat()),
        ('Technical Seminar: Cloud Security & Governance', 'Department seminar on AWS Cloud Security Architecture in Main Seminar Hall on May 10, 2025. Guest speaker: Mr. Arvind Rao (AWS Solutions Architect).', 'event', 'normal', 'all', 'All', None, staff1_id, 0, (now - timedelta(days=117)).isoformat()),
        ('Scheduled System Maintenance Notice', 'The student certification repository will undergo scheduled database maintenance on May 3, 2025 from 12:00 AM to 02:00 AM IST.', 'reminder', 'low', 'all', 'All', None, 3, 0, (now - timedelta(days=118)).isoformat()),
        ('Faculty Review Notice: Mentor Verification Queue', 'All faculty mentors: Please review your assigned students submissions for the current academic cycle.', 'reminder', 'high', 'staff', 'All', None, 3, 0, now.isoformat()),
    ]
    c.executemany("INSERT INTO notifications (title, body, category, priority, target_role, target_department, target_user_id, author_id, is_read, created_at) VALUES (?,?,?,?,?,?,?,?,?,?)", notifs)

    conn.commit()


# ── User & Auth Operations ────────────────────────────────────────

def authenticate_user(username, password):
    conn = get_db()
    user = conn.execute(
        """SELECT u.*, m.full_name as mentor_name, m.email as mentor_email
           FROM users u
           LEFT JOIN users m ON u.mentor_id = m.id
           WHERE u.username = ? AND u.password_hash = ?""",
        (username, hash_password(password))
    ).fetchone()
    conn.close()
    return dict(user) if user else None


def get_user_by_id(user_id):
    conn = get_db()
    user = conn.execute(
        """SELECT u.*, m.full_name as mentor_name, m.email as mentor_email, m.department as mentor_dept
           FROM users u
           LEFT JOIN users m ON u.mentor_id = m.id
           WHERE u.id = ?""",
        (user_id,)
    ).fetchone()
    conn.close()
    return dict(user) if user else None


def update_user_profile(user_id, full_name, email, phone, department):
    conn = get_db()
    conn.execute(
        "UPDATE users SET full_name=?, email=?, phone=?, department=? WHERE id=?",
        (full_name, email, phone, department, user_id)
    )
    conn.commit()
    conn.close()


def change_password(user_id, new_password):
    conn = get_db()
    conn.execute("UPDATE users SET password_hash=? WHERE id=?", (hash_password(new_password), user_id))
    conn.commit()
    conn.close()


def get_departments_list():
    conn = get_db()
    rows = conn.execute("SELECT DISTINCT department FROM users WHERE department IS NOT NULL AND department != ''").fetchall()
    conn.close()
    return [r['department'] for r in rows]


# ── Mentor & Mentee Operations ───────────────────────────────────

def get_students_by_mentor(mentor_id):
    """Fetch all students assigned to a specific mentor with certificate statistics."""
    conn = get_db()
    query = """
        SELECT u.id, u.username, u.full_name, u.email, u.phone, u.department, u.year, u.avatar_url,
               COUNT(c.id) as total_certs,
               SUM(CASE WHEN c.status = 'approved' THEN 1 ELSE 0 END) as approved_certs,
               SUM(CASE WHEN c.status = 'pending' THEN 1 ELSE 0 END) as pending_certs,
               SUM(CASE WHEN c.status = 'rejected' THEN 1 ELSE 0 END) as rejected_certs,
               ROUND(AVG(CASE WHEN c.integrity_score > 0 THEN c.integrity_score ELSE NULL END), 1) as avg_integrity
        FROM users u
        LEFT JOIN certificates c ON u.id = c.user_id
        WHERE u.role = 'student' AND u.mentor_id = ?
        GROUP BY u.id
        ORDER BY u.year ASC, u.full_name ASC
    """
    rows = conn.execute(query, (mentor_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_mentor_stats(mentor_id):
    """Fetch aggregated statistics strictly for a mentor's assigned students."""
    conn = get_db()
    stats = {}
    stats['total_mentees'] = conn.execute(
        "SELECT COUNT(*) FROM users WHERE role='student' AND mentor_id=?", (mentor_id,)
    ).fetchone()[0]

    stats['total_certs'] = conn.execute(
        """SELECT COUNT(c.id) FROM certificates c
           JOIN users u ON c.user_id = u.id
           WHERE u.mentor_id = ?""", (mentor_id,)
    ).fetchone()[0]

    stats['pending_reviews'] = conn.execute(
        """SELECT COUNT(c.id) FROM certificates c
           JOIN users u ON c.user_id = u.id
           WHERE u.mentor_id = ? AND c.status = 'pending'""", (mentor_id,)
    ).fetchone()[0]

    stats['approved_certs'] = conn.execute(
        """SELECT COUNT(c.id) FROM certificates c
           JOIN users u ON c.user_id = u.id
           WHERE u.mentor_id = ? AND c.status = 'approved'""", (mentor_id,)
    ).fetchone()[0]

    avg_row = conn.execute(
        """SELECT AVG(c.integrity_score) FROM certificates c
           JOIN users u ON c.user_id = u.id
           WHERE u.mentor_id = ? AND c.integrity_score > 0""", (mentor_id,)
    ).fetchone()
    stats['avg_integrity'] = round(avg_row[0], 1) if avg_row[0] else 0

    # Year breakdown for mentor's mentees
    year_rows = conn.execute(
        """SELECT year, COUNT(*) as count FROM users
           WHERE role='student' AND mentor_id=?
           GROUP BY year ORDER BY year""", (mentor_id,)
    ).fetchall()
    stats['mentees_by_year'] = {f"Year {r['year']}": r['count'] for r in year_rows}

    conn.close()
    return stats


# ── HOD / Admin Student & Staff Management (CRUD) ─────────────────

def get_all_mentors():
    """Fetch list of all staff/mentors along with their assigned mentee counts."""
    conn = get_db()
    query = """
        SELECT u.id, u.username, u.full_name, u.email, u.phone, u.department, u.designation, u.role,
               COUNT(s.id) as mentee_count
        FROM users u
        LEFT JOIN users s ON s.mentor_id = u.id AND s.role = 'student'
        WHERE u.role IN ('staff', 'admin')
        GROUP BY u.id
        ORDER BY u.department ASC, u.full_name ASC
    """
    rows = conn.execute(query).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_students_yearwise(dept=None, year=None, mentor_id=None, search=None):
    """Fetch students categorized year-wise with mentor details and certificates metrics."""
    conn = get_db()
    query = """
        SELECT u.id, u.username, u.full_name, u.email, u.phone, u.department, u.year, u.mentor_id,
               m.full_name as mentor_name, m.username as mentor_username, m.designation as mentor_designation,
               COUNT(c.id) as total_certs,
               SUM(CASE WHEN c.status = 'approved' THEN 1 ELSE 0 END) as approved_certs,
               SUM(CASE WHEN c.status = 'pending' THEN 1 ELSE 0 END) as pending_certs,
               ROUND(AVG(CASE WHEN c.integrity_score > 0 THEN c.integrity_score ELSE NULL END), 1) as avg_integrity
        FROM users u
        LEFT JOIN users m ON u.mentor_id = m.id
        LEFT JOIN certificates c ON u.id = c.user_id
        WHERE u.role = 'student'
    """
    params = []
    if dept and dept != 'All':
        query += " AND u.department = ?"
        params.append(dept)
    if year and str(year) != 'All' and str(year).isdigit():
        query += " AND u.year = ?"
        params.append(int(year))
    if mentor_id and str(mentor_id) != 'All':
        query += " AND u.mentor_id = ?"
        params.append(int(mentor_id))
    if search:
        query += " AND (u.full_name LIKE ? OR u.username LIKE ? OR u.email LIKE ?)"
        s = f"%{search}%"
        params.extend([s, s, s])

    query += " GROUP BY u.id ORDER BY u.year ASC, u.full_name ASC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_student_full_profile(student_id):
    """Fetch complete profile dossier for a student including mentor & all certificates."""
    conn = get_db()
    student = conn.execute(
        """SELECT u.*, m.full_name as mentor_name, m.username as mentor_username,
                  m.email as mentor_email, m.phone as mentor_phone, m.designation as mentor_designation
           FROM users u
           LEFT JOIN users m ON u.mentor_id = m.id
           WHERE u.id = ? AND u.role = 'student'""",
        (student_id,)
    ).fetchone()

    if not student:
        conn.close()
        return None

    certs = conn.execute(
        """SELECT c.*, r.full_name as reviewer_name
           FROM certificates c
           LEFT JOIN users r ON c.reviewer_id = r.id
           WHERE c.user_id = ?
           ORDER BY c.created_at DESC""",
        (student_id,)
    ).fetchall()

    result = dict(student)
    result['certificates'] = [dict(c) for c in certs]
    conn.close()
    return result


def create_student(username, password, full_name, email, phone, department, year=1, mentor_id=None):
    """Create a new student with year and mentor assignment."""
    conn = get_db()
    c = conn.cursor()
    c.execute(
        """INSERT INTO users (username, password_hash, full_name, email, phone, department, role, year, mentor_id)
           VALUES (?,?,?,?,?,?,?,?,?)""",
        (username.strip(), hash_password(password.strip()), full_name.strip(), email.strip() if email else None,
         phone.strip() if phone else None, department.strip() if department else None, 'student', int(year), mentor_id)
    )
    student_id = c.lastrowid
    conn.commit()
    conn.close()
    return student_id


def update_student(student_id, full_name, email, phone, department, year, mentor_id=None, password=None):
    """Update student record including year and mentor reassignment."""
    conn = get_db()
    if password and password.strip():
        conn.execute(
            """UPDATE users SET full_name=?, email=?, phone=?, department=?, year=?, mentor_id=?, password_hash=?
               WHERE id=? AND role='student'""",
            (full_name.strip(), email.strip() if email else None, phone.strip() if phone else None,
             department.strip() if department else None, int(year), mentor_id, hash_password(password.strip()), student_id)
        )
    else:
        conn.execute(
            """UPDATE users SET full_name=?, email=?, phone=?, department=?, year=?, mentor_id=?
               WHERE id=? AND role='student'""",
            (full_name.strip(), email.strip() if email else None, phone.strip() if phone else None,
             department.strip() if department else None, int(year), mentor_id, student_id)
        )
    conn.commit()
    conn.close()


def delete_student(student_id):
    """Delete a student and clean up all associated certificates and ML entries."""
    conn = get_db()
    conn.execute("DELETE FROM certificates WHERE user_id=?", (student_id,))
    conn.execute("DELETE FROM ml_predictions WHERE user_id=?", (student_id,))
    conn.execute("DELETE FROM users WHERE id=? AND role='student'", (student_id,))
    conn.commit()
    conn.close()


def create_staff(username, password, full_name, email, phone, department, designation='Assistant Professor', role='staff'):
    """Create a new staff / mentor / HOD."""
    conn = get_db()
    c = conn.cursor()
    c.execute(
        """INSERT INTO users (username, password_hash, full_name, email, phone, department, designation, role)
           VALUES (?,?,?,?,?,?,?,?)""",
        (username.strip(), hash_password(password.strip()), full_name.strip(), email.strip() if email else None,
         phone.strip() if phone else None, department.strip() if department else None, designation.strip(), role)
    )
    staff_id = c.lastrowid
    conn.commit()
    conn.close()
    return staff_id


def update_staff(staff_id, full_name, email, phone, department, designation, role='staff', password=None):
    """Update staff details."""
    conn = get_db()
    if password and password.strip():
        conn.execute(
            """UPDATE users SET full_name=?, email=?, phone=?, department=?, designation=?, role=?, password_hash=?
               WHERE id=?""",
            (full_name.strip(), email.strip() if email else None, phone.strip() if phone else None,
             department.strip() if department else None, designation.strip(), role, hash_password(password.strip()), staff_id)
        )
    else:
        conn.execute(
            """UPDATE users SET full_name=?, email=?, phone=?, department=?, designation=?, role=?
               WHERE id=?""",
            (full_name.strip(), email.strip() if email else None, phone.strip() if phone else None,
             department.strip() if department else None, designation.strip(), role, staff_id)
        )
    conn.commit()
    conn.close()


def delete_staff(staff_id):
    """Delete a staff member and unassign any mentees they have."""
    conn = get_db()
    # Unassign mentees
    conn.execute("UPDATE users SET mentor_id=NULL WHERE mentor_id=?", (staff_id,))
    conn.execute("DELETE FROM users WHERE id=? AND role IN ('staff', 'admin')", (staff_id,))
    conn.commit()
    conn.close()


def assign_student_mentor(student_id, mentor_id):
    """Assign or reassign a student to a specific mentor."""
    conn = get_db()
    conn.execute("UPDATE users SET mentor_id=? WHERE id=? AND role='student'", (mentor_id, student_id))
    conn.commit()
    conn.close()


# ── Certificate CRUD ─────────────────────────────────────────────

def get_certificates_for_user(user_id, status=None):
    conn = get_db()
    if status:
        rows = conn.execute(
            "SELECT * FROM certificates WHERE user_id = ? AND status = ? ORDER BY created_at DESC",
            (user_id, status)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM certificates WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_certificates(status=None, reviewer_id=None, role='admin'):
    """
    Fetch certificates.
    If role == 'staff', strictly filters certificates to only those from students
    assigned to this mentor (reviewer_id).
    If role in ('admin', 'hod'), returns campus/department wide.
    """
    conn = get_db()
    query = """
        SELECT c.*, u.full_name as student_name, u.username as student_username,
               u.department as student_dept, u.year as student_year,
               m.full_name as mentor_name
        FROM certificates c
        JOIN users u ON c.user_id = u.id
        LEFT JOIN users m ON u.mentor_id = m.id
        WHERE 1=1
    """
    params = []

    # Mentor scoping: Only show students assigned to this mentor
    if role == 'staff' and reviewer_id:
        query += " AND u.mentor_id = ?"
        params.append(reviewer_id)

    if status:
        query += " AND c.status = ?"
        params.append(status)

    query += " ORDER BY c.created_at DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_certificate_by_id(cert_id):
    conn = get_db()
    row = conn.execute(
        """SELECT c.*, u.full_name as student_name, u.username as student_username,
                  u.department as student_dept, u.year as student_year,
                  m.full_name as mentor_name
           FROM certificates c
           JOIN users u ON c.user_id = u.id
           LEFT JOIN users m ON u.mentor_id = m.id
           WHERE c.id = ?""",
        (cert_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def add_certificate(user_id, title, description, issue_date, cert_type, skills, file_path=None, photo_path=None, additional_photos=None, source_url=None):
    conn = get_db()
    c = conn.cursor()
    # Generate verification code
    dept_tag = "ENG"
    user = conn.execute("SELECT department FROM users WHERE id = ?", (user_id,)).fetchone()
    if user and user['department']:
        dept_tag = "".join([w[0] for w in user['department'].split() if w]).upper()[:3]
    rand_num = random.randint(1000, 9999)
    vcode = f"CERT-{datetime.now().year}-{dept_tag}-{rand_num}"

    c.execute(
        """INSERT INTO certificates (user_id, title, description, issue_date, cert_type, skills, file_path, photo_path, additional_photos, source_url, verification_code)
           VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        (user_id, title, description, issue_date, cert_type, skills, file_path, photo_path, additional_photos, source_url, vcode)
    )
    cert_id = c.lastrowid
    conn.commit()
    conn.close()
    return cert_id


def update_certificate_integrity(cert_id, score, details_json):
    conn = get_db()
    conn.execute(
        "UPDATE certificates SET integrity_score=?, integrity_details=? WHERE id=?",
        (score, details_json, cert_id)
    )
    conn.commit()
    conn.close()


def review_certificate(cert_id, reviewer_id, status, feedback):
    conn = get_db()
    conn.execute(
        "UPDATE certificates SET status=?, reviewer_id=?, review_feedback=?, reviewed_at=? WHERE id=?",
        (status, reviewer_id, feedback, datetime.now().isoformat(), cert_id)
    )
    conn.commit()
    conn.close()


# ── Notifications CRUD ───────────────────────────────────────────

def get_notifications(role='all', user_id=None, department=None):
    conn = get_db()
    query = """SELECT n.*, u.full_name as author_name
               FROM notifications n
               LEFT JOIN users u ON n.author_id = u.id
               WHERE (n.target_role = 'all' OR n.target_role = ? OR n.target_user_id = ?)"""
    params = [role, user_id or 0]

    if department:
        query += " AND (n.target_department IS NULL OR n.target_department = 'All' OR n.target_department = ?)"
        params.append(department)

    query += " ORDER BY n.created_at DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_notification(title, body, category='general', priority='normal', target_role='all', target_department='All', target_user_id=None, author_id=None):
    conn = get_db()
    c = conn.cursor()
    c.execute(
        """INSERT INTO notifications (title, body, category, priority, target_role, target_department, target_user_id, author_id)
           VALUES (?,?,?,?,?,?,?,?)""",
        (title, body, category, priority, target_role, target_department, target_user_id, author_id)
    )
    notif_id = c.lastrowid
    conn.commit()
    conn.close()
    return notif_id


def get_sent_broadcasts(author_id=None):
    conn = get_db()
    if author_id:
        rows = conn.execute(
            """SELECT n.*, u.full_name as author_name,
                      (SELECT COUNT(*) FROM users WHERE (n.target_role='all' OR role=n.target_role)
                                                   AND (n.target_department='All' OR department=n.target_department)) as audience_count
               FROM notifications n
               JOIN users u ON n.author_id = u.id
               WHERE n.author_id = ?
               ORDER BY n.created_at DESC""",
            (author_id,)
        ).fetchall()
    else:
        rows = conn.execute(
            """SELECT n.*, u.full_name as author_name,
                      (SELECT COUNT(*) FROM users WHERE (n.target_role='all' OR role=n.target_role)
                                                   AND (n.target_department='All' OR department=n.target_department)) as audience_count
               FROM notifications n
               LEFT JOIN users u ON n.author_id = u.id
               ORDER BY n.created_at DESC"""
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def mark_notification_read(notif_id):
    conn = get_db()
    conn.execute("UPDATE notifications SET is_read = 1 WHERE id = ?", (notif_id,))
    conn.commit()
    conn.close()


# ── Analytics Helpers ────────────────────────────────────────────

def get_user_stats(user_id):
    conn = get_db()
    stats = {}
    stats['total'] = conn.execute("SELECT COUNT(*) FROM certificates WHERE user_id=?", (user_id,)).fetchone()[0]
    stats['approved'] = conn.execute("SELECT COUNT(*) FROM certificates WHERE user_id=? AND status='approved'", (user_id,)).fetchone()[0]
    stats['pending'] = conn.execute("SELECT COUNT(*) FROM certificates WHERE user_id=? AND status='pending'", (user_id,)).fetchone()[0]
    stats['rejected'] = conn.execute("SELECT COUNT(*) FROM certificates WHERE user_id=? AND status='rejected'", (user_id,)).fetchone()[0]

    avg_row = conn.execute("SELECT AVG(integrity_score) FROM certificates WHERE user_id=? AND status='approved' AND integrity_score > 0", (user_id,)).fetchone()
    stats['avg_integrity'] = round(avg_row[0], 1) if avg_row[0] else 0

    monthly = conn.execute(
        """SELECT strftime('%Y-%m', issue_date) as month, COUNT(*) as count
           FROM certificates WHERE user_id=?
           GROUP BY month ORDER BY month""",
        (user_id,)
    ).fetchall()
    stats['monthly'] = [dict(m) for m in monthly]

    skills_rows = conn.execute("SELECT skills FROM certificates WHERE user_id=? AND skills IS NOT NULL", (user_id,)).fetchall()
    all_skills = []
    for row in skills_rows:
        if row['skills']:
            all_skills.extend([s.strip().title() for s in row['skills'].split(',') if s.strip()])
    skill_freq = {}
    for s in all_skills:
        skill_freq[s] = skill_freq.get(s, 0) + 1
    stats['skill_frequency'] = dict(sorted(skill_freq.items(), key=lambda x: x[1], reverse=True))

    integrity_rows = conn.execute(
        "SELECT id, title, integrity_score, integrity_details, status, verification_code FROM certificates WHERE user_id=? AND integrity_score > 0 ORDER BY integrity_score DESC",
        (user_id,)
    ).fetchall()
    stats['integrity_scores'] = [dict(r) for r in integrity_rows]

    conn.close()
    return stats


def get_global_stats():
    conn = get_db()
    stats = {}
    stats['total_students'] = conn.execute("SELECT COUNT(*) FROM users WHERE role='student'").fetchone()[0]
    stats['total_staff'] = conn.execute("SELECT COUNT(*) FROM users WHERE role IN ('staff', 'admin')").fetchone()[0]
    stats['total_certificates'] = conn.execute("SELECT COUNT(*) FROM certificates").fetchone()[0]
    stats['pending_reviews'] = conn.execute("SELECT COUNT(*) FROM certificates WHERE status='pending'").fetchone()[0]
    stats['approved'] = conn.execute("SELECT COUNT(*) FROM certificates WHERE status='approved'").fetchone()[0]
    stats['rejected'] = conn.execute("SELECT COUNT(*) FROM certificates WHERE status='rejected'").fetchone()[0]

    avg_row = conn.execute("SELECT AVG(integrity_score) FROM certificates WHERE integrity_score > 0").fetchone()
    stats['avg_integrity'] = round(avg_row[0], 1) if avg_row[0] else 0

    dept_rows = conn.execute(
        """SELECT u.department, COUNT(c.id) as cert_count
           FROM certificates c JOIN users u ON c.user_id = u.id
           GROUP BY u.department ORDER BY cert_count DESC"""
    ).fetchall()
    stats['by_department'] = [dict(r) for r in dept_rows]

    year_rows = conn.execute(
        """SELECT u.year, COUNT(c.id) as cert_count, COUNT(DISTINCT u.id) as student_count
           FROM users u LEFT JOIN certificates c ON u.id = c.user_id
           WHERE u.role = 'student'
           GROUP BY u.year ORDER BY u.year ASC"""
    ).fetchall()
    stats['by_year'] = [dict(r) for r in year_rows]

    monthly = conn.execute(
        """SELECT strftime('%Y-%m', issue_date) as month, COUNT(*) as count
           FROM certificates GROUP BY month ORDER BY month"""
    ).fetchall()
    stats['monthly_trend'] = [dict(m) for m in monthly]

    skills_rows = conn.execute("SELECT skills FROM certificates WHERE skills IS NOT NULL").fetchall()
    all_skills = []
    for row in skills_rows:
        if row['skills']:
            all_skills.extend([s.strip().title() for s in row['skills'].split(',') if s.strip()])
    skill_freq = {}
    for s in all_skills:
        skill_freq[s] = skill_freq.get(s, 0) + 1
    stats['top_skills'] = dict(sorted(skill_freq.items(), key=lambda x: x[1], reverse=True)[:15])

    conn.close()
    return stats


if __name__ == '__main__':
    init_db()
    print("[OK] Database initialized, migrated and seeded successfully.")
    stats = get_global_stats()
    print(f"   Students: {stats['total_students']}")
    print(f"   Faculty / Staff: {stats['total_staff']}")
    print(f"   Certificates: {stats['total_certificates']}")
    print(f"   Pending reviews: {stats['pending_reviews']}")
