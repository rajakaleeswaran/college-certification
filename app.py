"""
app.py - Flask Backend for Student Certification Portal
Features:
  - Role-based Authentication & Session Management
  - RESTful APIs for Certificates, Analytics, Notifications
  - Machine Learning & NLP Endpoints (Integrity Score, Career Radar, OCR Metadata Extractor)
  - Dedicated Staff Review & Broadcast Notification Endpoints
"""

import os
import json
from datetime import datetime
from functools import wraps

from flask import (
    Flask, request, jsonify, session, redirect, url_for,
    send_from_directory
)
from werkzeug.utils import secure_filename

import database
import ml_engine

# ── App Configuration ────────────────────────────────────────────
app = Flask(__name__, static_folder='static', static_url_path='/static', template_folder='templates')
app.secret_key = 'student-portal-secret-key-2025'
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'webp'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ── Auth Decorators ──────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({"error": "Authentication required"}), 401
            return redirect('/')
        return f(*args, **kwargs)
    return decorated


def staff_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({"error": "Authentication required"}), 401
            return redirect('/')
        if session.get('role') not in ('staff', 'admin'):
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({"error": "Staff access required"}), 403
            return redirect('/student_dashboard.html')
        return f(*args, **kwargs)
    return decorated


# ── Page Routes ──────────────────────────────────────────────────
@app.route('/')
def index():
    return send_from_directory(TEMPLATES_DIR, 'index.html')


@app.route('/student_dashboard.html')
@login_required
def student_dashboard():
    return send_from_directory(TEMPLATES_DIR, 'student_dashboard.html')


@app.route('/ai_insights.html')
@login_required
def ai_insights_page():
    return send_from_directory(TEMPLATES_DIR, 'ai_insights.html')


@app.route('/add_certificate.html')
@login_required
def add_certificate_page():
    return send_from_directory(TEMPLATES_DIR, 'add_certificate.html')


@app.route('/certificates.html')
@login_required
def certificates_page():
    return send_from_directory(TEMPLATES_DIR, 'certificates.html')


@app.route('/gallery.html')
@login_required
def gallery_page():
    return send_from_directory(TEMPLATES_DIR, 'gallery.html')


@app.route('/notifications.html')
@login_required
def notifications_page():
    return send_from_directory(TEMPLATES_DIR, 'notifications.html')


@app.route('/settings.html')
@login_required
def settings_page():
    return send_from_directory(TEMPLATES_DIR, 'settings.html')


@app.route('/staff_dashboard.html')
@staff_required
def staff_dashboard_page():
    return send_from_directory(TEMPLATES_DIR, 'staff_dashboard.html')


@app.route('/staff_reviews.html')
@staff_required
def staff_reviews_page():
    return send_from_directory(TEMPLATES_DIR, 'staff_reviews.html')


@app.route('/staff_notifications.html')
@staff_required
def staff_notifications_page():
    return send_from_directory(TEMPLATES_DIR, 'staff_notifications.html')


# ── Serve Uploaded Files & Root Static ────────────────────────────
@app.route('/uploads/<path:filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/<path:filename>')
def serve_root_file(filename):
    if filename.endswith('.html'):
        if os.path.exists(os.path.join(TEMPLATES_DIR, filename)):
            return send_from_directory(TEMPLATES_DIR, filename)
    if filename.endswith(('.jpg', '.jpeg', '.png', '.ico', '.svg', '.webp')):
        images_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'images')
        if os.path.exists(os.path.join(images_dir, filename)):
            return send_from_directory(images_dir, filename)
    if filename.endswith(('.jpg', '.jpeg', '.png', '.ico', '.svg', '.css', '.js')):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        if os.path.exists(os.path.join(base_dir, filename)):
            return send_from_directory(base_dir, filename)
    return jsonify({"error": "File not found"}), 404


# ═══════════════════════════════════════════════════════════════════
#  AUTH API
# ═══════════════════════════════════════════════════════════════════

@app.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    user = database.authenticate_user(username, password)
    if not user:
        return jsonify({"error": "Invalid registration number or password"}), 401

    session['user_id'] = user['id']
    session['username'] = user['username']
    session['role'] = user['role']
    session['full_name'] = user['full_name']
    session['department'] = user['department']

    redirect_url = '/staff_dashboard.html' if user['role'] in ('staff', 'admin') else '/student_dashboard.html'

    return jsonify({
        "success": True,
        "user": {
            "id": user['id'],
            "username": user['username'],
            "full_name": user['full_name'],
            "role": user['role'],
            "department": user['department']
        },
        "redirect": redirect_url
    })


@app.route('/api/auth/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({"success": True})


@app.route('/api/auth/me')
@login_required
def api_me():
    user = database.get_user_by_id(session['user_id'])
    if not user:
        session.clear()
        return jsonify({"error": "User not found"}), 401
    return jsonify({
        "id": user['id'],
        "username": user['username'],
        "full_name": user['full_name'],
        "email": user['email'],
        "phone": user['phone'],
        "department": user['department'],
        "role": user['role']
    })


@app.route('/api/auth/update-profile', methods=['PUT'])
@login_required
def api_update_profile():
    data = request.get_json() or {}
    database.update_user_profile(
        session['user_id'],
        data.get('full_name', ''),
        data.get('email', ''),
        data.get('phone', ''),
        data.get('department', '')
    )
    session['full_name'] = data.get('full_name', session['full_name'])
    return jsonify({"success": True})


@app.route('/api/auth/change-password', methods=['PUT'])
@login_required
def api_change_password():
    data = request.get_json() or {}
    new_password = data.get('new_password', '').strip()
    if len(new_password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400
    database.change_password(session['user_id'], new_password)
    return jsonify({"success": True})


# ═══════════════════════════════════════════════════════════════════
#  CERTIFICATES API
# ═══════════════════════════════════════════════════════════════════

@app.route('/api/certificates', methods=['GET'])
@login_required
def api_get_certificates():
    status = request.args.get('status')
    if session.get('role') in ('staff', 'admin'):
        certs = database.get_all_certificates(status)
    else:
        certs = database.get_certificates_for_user(session['user_id'], status)

    for cert in certs:
        if cert.get('integrity_details') and isinstance(cert['integrity_details'], str):
            try:
                cert['integrity_details'] = json.loads(cert['integrity_details'])
            except:
                pass

    return jsonify(certs)


@app.route('/api/certificates/<int:cert_id>', methods=['GET'])
@login_required
def api_get_certificate(cert_id):
    cert = database.get_certificate_by_id(cert_id)
    if not cert:
        return jsonify({"error": "Certificate record not found"}), 404
    if cert.get('integrity_details') and isinstance(cert['integrity_details'], str):
        try:
            cert['integrity_details'] = json.loads(cert['integrity_details'])
        except:
            pass
    return jsonify(cert)


@app.route('/api/certificates', methods=['POST'])
@login_required
def api_add_certificate():
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    issue_date = request.form.get('issue_date', '').strip()
    cert_type = request.form.get('cert_type', '').strip()
    skills = request.form.get('skills', '').strip()
    source_url = request.form.get('source_url', '').strip()

    if not title:
        return jsonify({"error": "Certificate title is required"}), 400

    file_path = None
    photo_path = None
    additional_photos_str = None

    if 'cert_file' in request.files:
        f = request.files['cert_file']
        if f and f.filename and allowed_file(f.filename):
            fname = secure_filename(f"{session['user_id']}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{f.filename}")
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], fname))
            file_path = f"uploads/{fname}"

    if 'cert_photo' in request.files:
        f = request.files['cert_photo']
        if f and f.filename and allowed_file(f.filename):
            fname = secure_filename(f"{session['user_id']}_photo_{datetime.now().strftime('%Y%m%d%H%M%S')}_{f.filename}")
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], fname))
            photo_path = f"uploads/{fname}"

    if 'additional_photos' in request.files:
        photos = request.files.getlist('additional_photos')
        photo_paths = []
        for f in photos:
            if f and f.filename and allowed_file(f.filename):
                fname = secure_filename(f"{session['user_id']}_add_{datetime.now().strftime('%Y%m%d%H%M%S')}_{f.filename}")
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], fname))
                photo_paths.append(f"uploads/{fname}")
        if photo_paths:
            additional_photos_str = json.dumps(photo_paths)

    cert_id = database.add_certificate(
        session['user_id'], title, description, issue_date, cert_type,
        skills, file_path, photo_path, additional_photos_str, source_url
    )

    cert = database.get_certificate_by_id(cert_id)
    if cert:
        integrity_result = ml_engine.compute_integrity_risk_score(cert)
        database.update_certificate_integrity(
            cert_id,
            integrity_result['overall_score'],
            json.dumps(integrity_result['dimensions'])
        )

    # Notify faculty
    database.add_notification(
        title=f"New Submission: {title}",
        body=f"Student {session.get('full_name', 'Student')} uploaded '{title}'. AI Confidence Index: {integrity_result['overall_score']}/100 ({integrity_result['risk_level']} Risk).",
        category='submission',
        priority='normal',
        target_role='staff',
        author_id=session['user_id']
    )

    return jsonify({
        "success": True,
        "cert_id": cert_id,
        "verification_code": cert.get('verification_code') if cert else None,
        "integrity": integrity_result
    })


@app.route('/api/certificates/<int:cert_id>/review', methods=['PUT'])
@staff_required
def api_review_certificate(cert_id):
    data = request.get_json() or {}
    status = data.get('status', '').strip()
    feedback = data.get('feedback', '').strip()

    if status not in ('approved', 'rejected'):
        return jsonify({"error": "Status must be 'approved' or 'rejected'"}), 400

    cert = database.get_certificate_by_id(cert_id)
    if not cert:
        return jsonify({"error": "Certificate record not found"}), 404

    database.review_certificate(cert_id, session['user_id'], status, feedback)

    database.add_notification(
        title=f"Certificate Review: {cert['title']} - {status.upper()}",
        body=f"Your submission for '{cert['title']}' was reviewed by {session.get('full_name', 'Faculty')}. Status: {status.title()}. Comments: {feedback or 'Verified according to institutional guidelines.'}",
        category='review',
        priority='high',
        target_role='student',
        target_user_id=cert['user_id'],
        author_id=session['user_id']
    )

    return jsonify({"success": True})


@app.route('/api/certificates/<int:cert_id>/integrity', methods=['GET'])
@login_required
def api_certificate_integrity(cert_id):
    cert = database.get_certificate_by_id(cert_id)
    if not cert:
        return jsonify({"error": "Certificate record not found"}), 404

    result = ml_engine.compute_integrity_risk_score(cert)
    return jsonify(result)


# ═══════════════════════════════════════════════════════════════════
#  MACHINE LEARNING & INTELLIGENCE API
# ═══════════════════════════════════════════════════════════════════

@app.route('/api/ml/predict-career')
@login_required
def api_predict_career():
    user_id = session['user_id']
    if session.get('role') in ('staff', 'admin'):
        user_id = request.args.get('user_id', user_id, type=int)

    certs = database.get_certificates_for_user(user_id, status='approved')
    if not certs:
        certs = database.get_certificates_for_user(user_id)

    result = ml_engine.predict_career_readiness(certs)
    return jsonify(result)


@app.route('/api/ml/skill-recommendations')
@login_required
def api_skill_recommendations():
    user_id = session['user_id']
    target_track = request.args.get('track')
    certs = database.get_certificates_for_user(user_id)
    result = ml_engine.get_skill_recommendations(certs, target_track)
    return jsonify(result)


@app.route('/api/ml/integrity-score', methods=['POST'])
@login_required
def api_integrity_score():
    data = request.get_json() or {}
    result = ml_engine.compute_integrity_risk_score(data)
    return jsonify(result)


@app.route('/api/ml/extract-metadata', methods=['POST'])
@login_required
def api_extract_metadata():
    data = request.get_json() or {}
    raw_text = data.get('text', '')
    result = ml_engine.extract_certificate_metadata(raw_text)
    return jsonify(result)


# ═══════════════════════════════════════════════════════════════════
#  ANALYTICS API
# ═══════════════════════════════════════════════════════════════════

@app.route('/api/analytics/summary')
@login_required
def api_analytics_summary():
    if session.get('role') in ('staff', 'admin'):
        return jsonify(database.get_global_stats())
    else:
        return jsonify(database.get_user_stats(session['user_id']))


@app.route('/api/analytics/integrity-overview')
@login_required
def api_integrity_overview():
    if session.get('role') in ('staff', 'admin'):
        certs = database.get_all_certificates()
    else:
        certs = database.get_certificates_for_user(session['user_id'])

    results = ml_engine.analyze_certificate_batch(certs)

    scores = [r['overall_score'] for r in results if r['overall_score'] > 0]
    summary = {
        "certificates": results,
        "total_analyzed": len(scores),
        "avg_score": round(sum(scores) / len(scores), 1) if scores else 0,
        "low_risk": sum(1 for r in results if r['risk_level'] == 'Low'),
        "medium_risk": sum(1 for r in results if r['risk_level'] == 'Medium'),
        "high_risk": sum(1 for r in results if r['risk_level'] == 'High'),
        "critical_risk": sum(1 for r in results if r['risk_level'] == 'Critical'),
        "not_analyzed": sum(1 for r in results if r['overall_score'] == 0)
    }

    return jsonify(summary)


# ═══════════════════════════════════════════════════════════════════
#  NOTIFICATIONS & STAFF BROADCAST API
# ═══════════════════════════════════════════════════════════════════

@app.route('/api/notifications')
@login_required
def api_get_notifications():
    role = session.get('role', 'student')
    dept = session.get('department')
    notifs = database.get_notifications(role, session['user_id'], dept)
    return jsonify(notifs)


@app.route('/api/notifications/broadcast', methods=['POST'])
@staff_required
def api_broadcast_notification():
    data = request.get_json() or {}
    title = data.get('title', '').strip()
    body = data.get('body', '').strip()
    category = data.get('category', 'general')
    priority = data.get('priority', 'normal')
    target_role = data.get('target_role', 'all')
    target_dept = data.get('target_department', 'All')
    target_user_id = data.get('target_user_id')

    if not title or not body:
        return jsonify({"error": "Title and announcement content are required"}), 400

    notif_id = database.add_notification(
        title=title,
        body=body,
        category=category,
        priority=priority,
        target_role=target_role,
        target_department=target_dept,
        target_user_id=target_user_id,
        author_id=session['user_id']
    )

    return jsonify({"success": True, "notif_id": notif_id})


@app.route('/api/notifications/broadcast-history')
@staff_required
def api_broadcast_history():
    history = database.get_sent_broadcasts(session['user_id'])
    return jsonify(history)


@app.route('/api/notifications/<int:notif_id>/read', methods=['PUT'])
@login_required
def api_mark_notification_read(notif_id):
    database.mark_notification_read(notif_id)
    return jsonify({"success": True})


@app.route('/api/students/list')
@staff_required
def api_students_list():
    students = database.get_students_list()
    return jsonify(students)


@app.route('/api/departments/list')
@login_required
def api_departments_list():
    depts = database.get_departments_list()
    return jsonify(depts)


# ── Application Entrypoint ───────────────────────────────────────
if __name__ == '__main__':
    database.init_db()
    print("[START] CertPortal Professional Campus Server starting...")
    print("   Server URL: http://localhost:5000")
    print("   Student Demo: 2023CSE1234 / password123")
    print("   Staff Demo:   STAFF101 / staff123")
    app.run(debug=True, host='0.0.0.0', port=5000)
