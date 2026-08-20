"""
database.py - SQLite Database Layer for Student Certification Portal
Handles schema creation, seed data, and all CRUD operations.
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
    """Initialize database schema and seed data."""
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
        avatar_url TEXT,
        created_at TEXT DEFAULT (datetime('now'))
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
        target_department TEXT,
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

    # ── Safe Migrations for Existing DB ─────────────────────────
    existing_cols_notif = [row[1] for row in c.execute("PRAGMA table_info(notifications)").fetchall()]
    if 'target_department' not in existing_cols_notif:
        c.execute("ALTER TABLE notifications ADD COLUMN target_department TEXT DEFAULT 'All'")
    if 'author_id' not in existing_cols_notif:
        c.execute("ALTER TABLE notifications ADD COLUMN author_id INTEGER REFERENCES users(id)")

    existing_cols_cert = [row[1] for row in c.execute("PRAGMA table_info(certificates)").fetchall()]
    if 'verification_code' not in existing_cols_cert:
        c.execute("ALTER TABLE certificates ADD COLUMN verification_code TEXT")

    conn.commit()

    if c.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
        _seed_data(conn)

    conn.close()


def _seed_data(conn):
    """Insert realistic sample data."""
    c = conn.cursor()

    users = [
        ('2023CSE1234', hash_password('password123'), 'Raseena Fathima', 'raseena@college.edu', '+91-9876543210', 'Computer Science and Engineering', 'student'),
        ('2023CSE1235', hash_password('password123'), 'Arun Kumar', 'arun@college.edu', '+91-9876543211', 'Computer Science and Engineering', 'student'),
        ('2023ECE2001', hash_password('password123'), 'Priya Sharma', 'priya@college.edu', '+91-9876543212', 'Electronics and Communication', 'student'),
        ('2023MEC3001', hash_password('password123'), 'Mohammed Ashik', 'ashik@college.edu', '+91-9876543213', 'Mechanical Engineering', 'student'),
        ('2023CSE1236', hash_password('password123'), 'Sneha Raj', 'sneha@college.edu', '+91-9876543214', 'Computer Science and Engineering', 'student'),
        ('STAFF101', hash_password('staff123'), 'Dr. Anitha Menon', 'anitha.staff@college.edu', '+91-9876500001', 'Computer Science and Engineering', 'staff'),
        ('STAFF102', hash_password('staff123'), 'Prof. Rajesh Nair', 'rajesh.staff@college.edu', '+91-9876500002', 'Electronics and Communication', 'staff'),
        ('ADMIN001', hash_password('admin123'), 'Principal Dr. Suresh', 'admin@college.edu', '+91-9876500000', 'Administration', 'admin'),
    ]
    c.executemany("INSERT INTO users (username, password_hash, full_name, email, phone, department, role) VALUES (?,?,?,?,?,?,?)", users)

    now = datetime.now()
    cert_data = [
        # user_id=1 (Raseena)
        (1, 'Advanced Web Development', 'Full-stack web application development covering React, Node.js, RESTful microservices, and containerization.', '2025-05-12', 'Technical', 'HTML,CSS,JavaScript,React,Node.js,REST API', None, None, None, 'https://coursera.org/verify/WEB-DEV-892', 'approved', 6, 'Verified with official platform registry. Comprehensive curriculum demonstrated.', (now - timedelta(days=90)).isoformat(), 92.5, json.dumps({"metadata_consistency": {"score": 25, "max": 25, "pct": 100}, "skill_relevancy": {"score": 23, "max": 25, "pct": 92}, "issuer_trust": {"score": 18, "max": 20, "pct": 90}, "temporal_validity": {"score": 14.5, "max": 15, "pct": 96.7}, "content_authenticity": {"score": 12, "max": 15, "pct": 80}}), 'CERT-2025-CSE-9211'),
        (1, 'Python for Data Science', 'Comprehensive data analysis, statistical modeling, data visualization with Pandas, Matplotlib, and Scikit-Learn.', '2025-06-05', 'AI/ML', 'Python,NumPy,Pandas,Matplotlib,Machine Learning', None, None, None, 'https://datacamp.com/statement-of-accomplishment/cert/PY-883', 'approved', 6, 'Verified. Demonstrated strong foundational data analysis competency.', (now - timedelta(days=60)).isoformat(), 88.3, json.dumps({"metadata_consistency": {"score": 24, "max": 25, "pct": 96}, "skill_relevancy": {"score": 22, "max": 25, "pct": 88}, "issuer_trust": {"score": 17, "max": 20, "pct": 85}, "temporal_validity": {"score": 14, "max": 15, "pct": 93.3}, "content_authenticity": {"score": 11.3, "max": 15, "pct": 75.3}}), 'CERT-2025-CSE-8832'),
        (1, 'AWS Cloud Practitioner', 'Official Amazon Web Services foundational cloud computing architectural principles and services.', '2025-04-10', 'Cloud', 'AWS,Cloud Computing,EC2,S3,IAM', None, None, None, 'https://aws.amazon.com/verification/AWS-CP-1029', 'approved', 6, 'AWS official credential verified via Amazon CertMetrics registry.', (now - timedelta(days=120)).isoformat(), 97.1, json.dumps({"metadata_consistency": {"score": 25, "max": 25, "pct": 100}, "skill_relevancy": {"score": 24, "max": 25, "pct": 96}, "issuer_trust": {"score": 19.6, "max": 20, "pct": 98}, "temporal_validity": {"score": 14.5, "max": 15, "pct": 96.7}, "content_authenticity": {"score": 14, "max": 15, "pct": 93.3}}), 'CERT-2025-CSE-1029'),
        (1, 'Cybersecurity Fundamentals', 'Network defense, vulnerability assessments, security policy compliance, and threat mitigation.', '2025-03-28', 'Security', 'Cybersecurity,Networking,Ethical Hacking,Firewall', None, None, None, 'https://cisco.com/verify/sec-339', 'approved', 7, 'Cisco Networking Academy certificate verified.', (now - timedelta(days=150)).isoformat(), 85.0, json.dumps({"metadata_consistency": {"score": 22, "max": 25, "pct": 88}, "skill_relevancy": {"score": 21, "max": 25, "pct": 84}, "issuer_trust": {"score": 18, "max": 20, "pct": 90}, "temporal_validity": {"score": 13, "max": 15, "pct": 86.7}, "content_authenticity": {"score": 11, "max": 15, "pct": 73.3}}), 'CERT-2025-CSE-3391'),
        (1, 'UI/UX Design Principles', 'User experience methodologies, wireframing, and design system creation using Figma.', '2025-04-22', 'Design', 'UI/UX,Figma,Prototyping,User Research', None, None, None, None, 'approved', 6, 'Figma capstone project submitted and verified.', (now - timedelta(days=110)).isoformat(), 79.8, json.dumps({"metadata_consistency": {"score": 21, "max": 25, "pct": 84}, "skill_relevancy": {"score": 20, "max": 25, "pct": 80}, "issuer_trust": {"score": 15, "max": 20, "pct": 75}, "temporal_validity": {"score": 13.8, "max": 15, "pct": 92}, "content_authenticity": {"score": 10, "max": 15, "pct": 66.7}}), 'CERT-2025-CSE-7741'),
        (1, 'Docker & Kubernetes Essentials', 'Container orchestration, CI/CD automated deployments, and microservice mesh configurations.', '2025-06-28', 'DevOps', 'Docker,Kubernetes,DevOps,Microservices,CI/CD', None, None, None, 'https://edx.org/verify/dk-441', 'pending', None, None, None, 88.0, json.dumps({"metadata_consistency": {"score": 23, "max": 25, "pct": 92}, "skill_relevancy": {"score": 23, "max": 25, "pct": 92}, "issuer_trust": {"score": 17, "max": 20, "pct": 85}, "temporal_validity": {"score": 14, "max": 15, "pct": 93.3}, "content_authenticity": {"score": 11, "max": 15, "pct": 73.3}}), 'CERT-2025-CSE-4410'),
        (1, 'Machine Learning with TensorFlow', 'Deep learning architectures, convolutional networks, and natural language classification.', '2025-07-15', 'AI/ML', 'TensorFlow,Keras,Deep Learning,Neural Networks,Python', None, None, None, 'https://coursera.org/verify/tf-991', 'pending', None, None, None, 91.5, json.dumps({"metadata_consistency": {"score": 24, "max": 25, "pct": 96}, "skill_relevancy": {"score": 24, "max": 25, "pct": 96}, "issuer_trust": {"score": 18, "max": 20, "pct": 90}, "temporal_validity": {"score": 14.5, "max": 15, "pct": 96.7}, "content_authenticity": {"score": 11, "max": 15, "pct": 73.3}}), 'CERT-2025-CSE-9912'),
        (1, 'Blockchain Fundamentals', 'Decentralized smart contracts on Ethereum utilizing Solidity.', '2025-05-25', 'Technical', 'Blockchain,Smart Contracts,Ethereum,Solidity', None, None, None, None, 'rejected', 7, 'Certificate scan was corrupted and lacked verifiable issuer credential. Please resubmit clear copy.', (now - timedelta(days=80)).isoformat(), 34.2, json.dumps({"metadata_consistency": {"score": 10, "max": 25, "pct": 40}, "skill_relevancy": {"score": 12, "max": 25, "pct": 48}, "issuer_trust": {"score": 5, "max": 20, "pct": 25}, "temporal_validity": {"score": 4.2, "max": 15, "pct": 28}, "content_authenticity": {"score": 3, "max": 15, "pct": 20}}), None),

        # user_id=2 (Arun)
        (2, 'Java Enterprise Development', 'Spring Boot 3, Spring Security, Hibernate ORM, and enterprise architectural design patterns.', '2025-05-20', 'Technical', 'Java,Spring Boot,Hibernate,REST API,Microservices', None, None, None, 'https://oracle.com/verify/java-88', 'approved', 6, 'Verified against Oracle registry.', (now - timedelta(days=85)).isoformat(), 91.0, None, 'CERT-2025-CSE-2021'),
        (2, 'Google Cloud Associate', 'GCP Associate Cloud Engineer certification spanning Compute Engine, Kubernetes Engine, and IAM.', '2025-06-15', 'Cloud', 'GCP,Cloud Computing,BigQuery,Compute Engine', None, None, None, 'https://google.com/verify/gcp-44', 'approved', 7, 'Official Google certification confirmed.', (now - timedelta(days=50)).isoformat(), 96.5, None, 'CERT-2025-CSE-2022'),
        (2, 'React Native Mobile Dev', 'Cross-platform mobile application architecture, state management, and native bridge APIs.', '2025-07-01', 'Technical', 'React Native,JavaScript,Mobile,iOS,Android', None, None, None, None, 'pending', None, None, None, 78.5, None, 'CERT-2025-CSE-2023'),

        # user_id=3 (Priya)
        (3, 'VLSI Design Fundamentals', 'FPGA programming, Verilog HDL synthesis, and timing closure for digital circuits.', '2025-04-15', 'Technical', 'VLSI,FPGA,Verilog,Digital Design', None, None, None, None, 'approved', 7, 'ECE Department lab verification completed.', (now - timedelta(days=100)).isoformat(), 89.2, None, 'CERT-2025-ECE-3001'),
        (3, 'IoT Systems Development', 'Internet of Things sensor networks, MQTT protocols, and embedded Arduino integration.', '2025-05-30', 'Technical', 'IoT,Arduino,Raspberry Pi,Sensors,Embedded', None, None, None, None, 'approved', 7, 'Verified by Department IoT coordinator.', (now - timedelta(days=70)).isoformat(), 87.5, None, 'CERT-2025-ECE-3002'),

        # user_id=4 (Ashik)
        (4, 'AutoCAD Professional', 'Parametric 3D mechanical modeling, assembly drawing, and tolerance specifications.', '2025-03-10', 'Design', 'AutoCAD,3D Modeling,CAD,Mechanical Design', None, None, None, None, 'approved', 6, 'Autodesk accredited certification verified.', (now - timedelta(days=160)).isoformat(), 93.0, None, 'CERT-2025-MEC-4001'),

        # user_id=5 (Sneha)
        (5, 'Data Analytics with R', 'Statistical data modeling, exploratory data analysis, and publication-quality visualization with ggplot2.', '2025-06-20', 'AI/ML', 'R,Statistics,Data Visualization,ggplot2', None, None, None, 'https://datacamp.com/verify/r-102', 'approved', 6, 'DataCamp statement verified.', (now - timedelta(days=45)).isoformat(), 86.7, None, 'CERT-2025-CSE-5001'),
        (5, 'Natural Language Processing', 'Transformers, BERT embeddings, and semantic parsing with Hugging Face and spaCy.', '2025-07-10', 'AI/ML', 'NLP,spaCy,Transformers,Python,Text Mining', None, None, None, None, 'pending', None, None, None, 84.0, None, 'CERT-2025-CSE-5002'),
    ]
    c.executemany("""INSERT INTO certificates
        (user_id, title, description, issue_date, cert_type, skills, file_path, photo_path, additional_photos, source_url, status, reviewer_id, review_feedback, reviewed_at, integrity_score, integrity_details, verification_code)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", cert_data)

    notifs = [
        ('Submit April Certifications for Institutional Audit', 'Please ensure all professional certifications completed in April 2025 are uploaded by May 5th for institutional internal review and placement records.', 'deadline', 'high', 'student', 'All', None, 6, 0, (now - timedelta(days=112)).isoformat()),
        ('Best Wishes for Final Year Capstone Evaluations', 'Faculty and department heads extend best wishes to all final year engineering students for their upcoming project evaluations.', 'wishes', 'normal', 'all', 'All', None, 6, 0, (now - timedelta(days=114)).isoformat()),
        ('Technical Seminar: Cloud Security & Governance', 'Department seminar on AWS Cloud Security Architecture in Main Seminar Hall on May 10, 2025. Guest speaker: Mr. Arvind Rao (AWS Solutions Architect).', 'event', 'normal', 'all', 'All', None, 6, 0, (now - timedelta(days=117)).isoformat()),
        ('Scheduled System Maintenance Notice', 'The student certification repository will undergo scheduled database maintenance on May 3, 2025 from 12:00 AM to 02:00 AM IST.', 'reminder', 'low', 'all', 'All', None, 8, 0, (now - timedelta(days=118)).isoformat()),
        ('Applied AI & Deep Learning Masterclass Registration', 'Registration is now open for the hands-on Deep Learning Masterclass on August 25-27, 2025. Seats allocated on first-come basis.', 'event', 'high', 'student', 'Computer Science and Engineering', None, 6, 0, (now - timedelta(days=5)).isoformat()),
        ('Updated Certificate Verification Guidelines', 'All certifications uploaded must include a verifiable credentials URL or QR reference code for rapid faculty sign-off.', 'policy', 'high', 'all', 'All', None, 8, 0, (now - timedelta(days=3)).isoformat()),
        ('Campus Placement Technical Screening Schedule', 'Tier-1 tech placement drives commence next month. Ensure all verified credentials are up to date on your profile.', 'event', 'high', 'student', 'All', None, 6, 0, (now - timedelta(days=1)).isoformat()),
        ('Faculty Review Notice: Pending Submissions', 'Faculty reviewers: Please complete review cycles for all pending student certification submissions by Friday.', 'reminder', 'high', 'staff', 'All', None, 8, 0, now.isoformat()),
    ]
    c.executemany("INSERT INTO notifications (title, body, category, priority, target_role, target_department, target_user_id, author_id, is_read, created_at) VALUES (?,?,?,?,?,?,?,?,?,?)", notifs)

    conn.commit()


# ── CRUD Helpers ─────────────────────────────────────────────────

def authenticate_user(username, password):
    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE username = ? AND password_hash = ?",
        (username, hash_password(password))
    ).fetchone()
    conn.close()
    return dict(user) if user else None


def get_user_by_id(user_id):
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return dict(user) if user else None


def get_students_list():
    conn = get_db()
    rows = conn.execute("SELECT id, username, full_name, department, email FROM users WHERE role='student' ORDER BY full_name").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_departments_list():
    conn = get_db()
    rows = conn.execute("SELECT DISTINCT department FROM users WHERE department IS NOT NULL AND department != ''").fetchall()
    conn.close()
    return [r['department'] for r in rows]


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


def get_all_certificates(status=None):
    conn = get_db()
    if status:
        rows = conn.execute(
            """SELECT c.*, u.full_name as student_name, u.username as student_username, u.department as student_dept
               FROM certificates c JOIN users u ON c.user_id = u.id
               WHERE c.status = ? ORDER BY c.created_at DESC""",
            (status,)
        ).fetchall()
    else:
        rows = conn.execute(
            """SELECT c.*, u.full_name as student_name, u.username as student_username, u.department as student_dept
               FROM certificates c JOIN users u ON c.user_id = u.id
               ORDER BY c.created_at DESC"""
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_certificate_by_id(cert_id):
    conn = get_db()
    row = conn.execute(
        """SELECT c.*, u.full_name as student_name, u.username as student_username, u.department as student_dept
           FROM certificates c JOIN users u ON c.user_id = u.id
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
    print("[OK] Database initialized and seeded successfully.")
    stats = get_global_stats()
    print(f"   Students: {stats['total_students']}")
    print(f"   Certificates: {stats['total_certificates']}")
    print(f"   Pending reviews: {stats['pending_reviews']}")
