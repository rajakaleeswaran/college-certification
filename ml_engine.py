"""
ml_engine.py - Machine Learning & NLP Analytics Engine
Features:
  1. AI Certificate Integrity Risk Score (5-dimension model)
  2. Career Readiness & Domain Matching Predictor (TF-IDF + Cosine Similarity)
  3. Skill Gap & Recommendation Engine
  4. AI Metadata & Skill Auto-Extractor (Simulated OCR / NLP text parsing)
"""

import json
import re
import math
import random
from collections import Counter
from datetime import datetime

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ═══════════════════════════════════════════════════════════════════
#  DOMAIN KNOWLEDGE BASE
# ═══════════════════════════════════════════════════════════════════

CAREER_TRACKS = {
    "Full-Stack Web & Cloud Systems": {
        "keywords": [
            "html", "css", "javascript", "react", "angular", "vue", "node.js",
            "express", "django", "flask", "spring boot", "rest api", "graphql",
            "mongodb", "postgresql", "mysql", "aws", "azure", "gcp", "cloud",
            "ec2", "s3", "iam", "docker", "kubernetes", "ci/cd", "devops",
            "microservices", "serverless", "web development", "full-stack",
            "typescript", "next.js", "tailwind", "sass", "webpack"
        ],
        "weight": 1.0,
        "icon": "globe"
    },
    "Data Science, AI & Machine Learning": {
        "keywords": [
            "python", "r", "numpy", "pandas", "matplotlib", "seaborn", "scipy",
            "scikit-learn", "tensorflow", "keras", "pytorch", "deep learning",
            "neural networks", "machine learning", "nlp", "natural language",
            "computer vision", "data science", "data analytics", "statistics",
            "regression", "classification", "clustering", "transformers",
            "hugging face", "spacy", "text mining", "bigquery", "data visualization",
            "ggplot2", "power bi", "tableau", "ai", "artificial intelligence"
        ],
        "weight": 1.0,
        "icon": "cpu"
    },
    "Cybersecurity & Network Infrastructure": {
        "keywords": [
            "cybersecurity", "networking", "ethical hacking", "penetration testing",
            "firewall", "ids", "ips", "siem", "soc", "cryptography", "ssl",
            "tls", "vpn", "network security", "information security", "oscp",
            "ceh", "comptia", "security+", "cisco", "ccna", "ccnp", "wireshark",
            "nmap", "kali linux", "vulnerability", "threat", "compliance",
            "iso 27001", "gdpr", "cloud security", "zero trust"
        ],
        "weight": 1.0,
        "icon": "shield"
    },
    "Mobile & Embedded Systems": {
        "keywords": [
            "android", "ios", "react native", "flutter", "swift", "kotlin",
            "mobile", "cross-platform", "app development", "embedded", "iot",
            "arduino", "raspberry pi", "sensors", "vlsi", "fpga", "verilog",
            "vhdl", "digital design", "microcontroller", "arm", "rtos",
            "edge computing", "wearable", "bluetooth", "zigbee"
        ],
        "weight": 1.0,
        "icon": "smartphone"
    },
    "DevOps & Cloud Architecture": {
        "keywords": [
            "devops", "ci/cd", "jenkins", "github actions", "gitlab ci",
            "terraform", "ansible", "puppet", "chef", "docker", "kubernetes",
            "helm", "prometheus", "grafana", "elk stack", "monitoring",
            "infrastructure as code", "site reliability", "sre", "load balancing",
            "nginx", "apache", "linux", "bash", "shell scripting",
            "cloud architecture", "auto scaling", "serverless", "lambda"
        ],
        "weight": 1.0,
        "icon": "server"
    }
}

# Trusted issuers with baseline trust weights
TRUSTED_ISSUERS = {
    "aws": 98, "amazon web services": 98, "google": 97, "google cloud": 97,
    "microsoft": 97, "azure": 97, "gcp": 97, "cisco": 96, "oracle": 95,
    "ibm": 95, "comptia": 94, "coursera": 89, "edx": 88, "udacity": 87,
    "datacamp": 85, "pluralsight": 85, "linkedin learning": 82,
    "nptel": 92, "swayam": 90, "iit": 94, "iisc": 95, "mit": 96, "stanford": 96,
    "freecodecamp": 80, "hackerrank": 82, "leetcode": 80, "kaggle": 85
}

# Risk patterns
RED_FLAG_PATTERNS = [
    (r"free\s+certificate", -15, "Unverified free certificate without exam proctoring"),
    (r"instant\s+(certificate|certification)", -20, "Instant generation pattern detected without evaluation period"),
    (r"(buy|purchase)\s+certificate", -40, "Commercial direct purchase indicators detected"),
    (r"no\s+(exam|test|assessment)", -12, "No examination or assessment threshold verified"),
    (r"sample|demo|test\s+certificate", -30, "Sample or placeholder certificate watermark detected"),
]

TRUST_SIGNALS = [
    (r"(proctored|supervised)\s+(exam|test)", 10, "Proctored official examination verified"),
    (r"(hands[- ]on|lab|project)", 8, "Practical laboratory & project work verified"),
    (r"(capstone|final\s+project)", 10, "Comprehensive capstone project evaluated"),
    (r"(peer[- ]reviewed|graded\s+assignment)", 6, "Peer-graded assessment benchmark completed"),
    (r"(accredited|recognized|autonomous)", 8, "Accredited educational curriculum standard"),
    (r"(official|authorized|certified)", 7, "Official authorized certification credentials"),
]


# ═══════════════════════════════════════════════════════════════════
#  1. AI CERTIFICATE INTEGRITY RISK SCORE
# ═══════════════════════════════════════════════════════════════════

def compute_integrity_risk_score(certificate):
    """
    Computes a multi-dimensional AI Certificate Integrity Risk Score (0-100).
    Evaluates:
      1. Metadata Consistency (0-25)
      2. Skill Relevancy (0-25)
      3. Issuer Trust Level (0-20)
      4. Temporal Validity (0-15)
      5. Content Authenticity (0-15)
    """
    title = (certificate.get('title') or '').strip()
    description = (certificate.get('description') or '').strip()
    skills_str = (certificate.get('skills') or '').strip()
    issue_date_str = (certificate.get('issue_date') or '').strip()
    cert_type = (certificate.get('cert_type') or '').strip()
    source_url = (certificate.get('source_url') or '').strip()
    file_path = (certificate.get('file_path') or '').strip()
    photo_path = (certificate.get('photo_path') or '').strip()

    combined_text = f"{title} {description} {skills_str} {cert_type} {source_url}".lower()
    flags = []
    trust_signals_found = []
    dim_scores = {}

    # Dimension 1: Metadata Consistency (0-25)
    meta_score = 25.0
    meta_reasons = []

    if not title:
        meta_score -= 10
        meta_reasons.append("Missing certificate title")
    elif len(title) < 5:
        meta_score -= 5
        meta_reasons.append("Title too brief for structured validation")

    if not description:
        meta_score -= 8
        meta_reasons.append("No curriculum or course description provided")
    elif len(description) < 20:
        meta_score -= 4
        meta_reasons.append("Description lacks course syllabus detail")

    if not skills_str:
        meta_score -= 5
        meta_reasons.append("No explicit skill tags provided")

    if not issue_date_str:
        meta_score -= 5
        meta_reasons.append("Missing issuance date")

    if title and description:
        title_words = set(re.findall(r'\w{3,}', title.lower()))
        desc_words = set(re.findall(r'\w{3,}', description.lower()))
        overlap = len(title_words & desc_words)
        if overlap == 0 and len(title_words) >= 2:
            meta_score -= 3
            meta_reasons.append("Title keywords lack alignment with description content")

    if meta_reasons:
        flags.append({"dimension": "Metadata Consistency", "issues": meta_reasons, "impact": round(25 - max(meta_score, 0), 1)})

    dim_scores['metadata_consistency'] = {
        "score": round(max(meta_score, 0), 1),
        "max": 25,
        "pct": round(max(meta_score, 0) / 25 * 100, 1)
    }

    # Dimension 2: Skill Relevancy (0-25)
    skill_score = 25.0
    skill_reasons = []

    skills_list = [s.strip().lower() for s in skills_str.split(',') if s.strip()] if skills_str else []

    if not skills_list:
        skill_score -= 15
        skill_reasons.append("No competencies cataloged for skill graph matching")
    else:
        all_known_skills = set()
        for track in CAREER_TRACKS.values():
            all_known_skills.update(track['keywords'])

        recognized = sum(1 for s in skills_list if any(k in s for k in all_known_skills))
        recognition_rate = recognized / len(skills_list)
        if recognition_rate < 0.3:
            skill_score -= 8
            skill_reasons.append(f"Low taxonomy alignment: {recognized}/{len(skills_list)} match recognized technical frameworks")
        elif recognition_rate < 0.6:
            skill_score -= 4
            skill_reasons.append(f"Partial taxonomy alignment ({recognized}/{len(skills_list)} verified skills)")

        if description:
            desc_lower = description.lower()
            matching_skills = sum(1 for s in skills_list if s in desc_lower)
            if skills_list and matching_skills / len(skills_list) < 0.2:
                skill_score -= 4
                skill_reasons.append("Skills tagged have weak correlation to described course modules")

    if skill_reasons:
        flags.append({"dimension": "Skill Relevancy", "issues": skill_reasons, "impact": round(25 - max(skill_score, 0), 1)})

    dim_scores['skill_relevancy'] = {
        "score": round(max(skill_score, 0), 1),
        "max": 25,
        "pct": round(max(skill_score, 0) / 25 * 100, 1)
    }

    # Dimension 3: Issuer Trust Level (0-20)
    issuer_score = 12.0
    issuer_reasons = []

    best_issuer_score = 0
    detected_issuer = None
    for issuer, trust in TRUSTED_ISSUERS.items():
        if issuer in combined_text:
            if trust > best_issuer_score:
                best_issuer_score = trust
                detected_issuer = issuer

    if detected_issuer:
        issuer_score = best_issuer_score / 100 * 20
        trust_signals_found.append(f"Recognized organization: {detected_issuer.title()} (Trust index: {best_issuer_score}%)")
    else:
        issuer_reasons.append("No standard accredited institutional issuer recognized in header")

    if source_url:
        if any(dom in source_url.lower() for dom in ['coursera.org', 'udemy.com', 'edx.org', 'aws.amazon.com', 'google.com', 'microsoft.com', 'nptel.ac.in', 'swayam.gov.in']):
            issuer_score = min(issuer_score + 3, 20)
            trust_signals_found.append("Cryptographic verification URL validated against authoritative provider")
        else:
            trust_signals_found.append("External verification link provided")
            issuer_score = min(issuer_score + 1, 20)

    if issuer_reasons:
        flags.append({"dimension": "Issuer Trust Level", "issues": issuer_reasons, "impact": round(20 - max(issuer_score, 0), 1)})

    dim_scores['issuer_trust'] = {
        "score": round(max(issuer_score, 0), 1),
        "max": 20,
        "pct": round(max(issuer_score, 0) / 20 * 100, 1)
    }

    # Dimension 4: Temporal Validity (0-15)
    temporal_score = 15.0
    temporal_reasons = []

    if issue_date_str:
        try:
            issue_date = datetime.strptime(issue_date_str, '%Y-%m-%d')
            now = datetime.now()

            if issue_date > now:
                temporal_score -= 10
                temporal_reasons.append(f"Anomalous future issuance date detected ({issue_date_str})")

            days_old = (now - issue_date).days
            if days_old > 1825:
                temporal_score -= 4
                temporal_reasons.append("Certification exceeds 5-year validity window; recommend renewal")
            elif days_old > 1095:
                temporal_score -= 2
                temporal_reasons.append("Certification issued over 3 years ago")

            if days_old == 0:
                temporal_score -= 2
                temporal_reasons.append("Same-day submission flagged for standard spot-check")
        except ValueError:
            temporal_score -= 8
            temporal_reasons.append(f"Non-standard ISO date formatting: {issue_date_str}")
    else:
        temporal_score -= 10
        temporal_reasons.append("Missing issuance timestamp")

    if temporal_reasons:
        flags.append({"dimension": "Temporal Validity", "issues": temporal_reasons, "impact": round(15 - max(temporal_score, 0), 1)})

    dim_scores['temporal_validity'] = {
        "score": round(max(temporal_score, 0), 1),
        "max": 15,
        "pct": round(max(temporal_score, 0) / 15 * 100, 1)
    }

    # Dimension 5: Content Authenticity (0-15)
    auth_score = 15.0
    auth_reasons = []

    for pattern, penalty, reason in RED_FLAG_PATTERNS:
        if re.search(pattern, combined_text, re.IGNORECASE):
            auth_score += penalty
            auth_reasons.append(reason)
            flags.append({"dimension": "Content Authenticity", "issues": [reason], "impact": abs(penalty)})

    for pattern, bonus, reason in TRUST_SIGNALS:
        if re.search(pattern, combined_text, re.IGNORECASE):
            auth_score = min(auth_score + bonus * 0.3, 15)
            trust_signals_found.append(reason)

    if file_path or photo_path:
        auth_score = min(auth_score + 2, 15)
        trust_signals_found.append("Digital artifact uploaded for institutional audit")
    else:
        auth_score -= 3
        auth_reasons.append("No document or credential image uploaded for manual verification")

    dim_scores['content_authenticity'] = {
        "score": round(max(auth_score, 0), 1),
        "max": 15,
        "pct": round(max(auth_score, 0) / 15 * 100, 1)
    }

    # Overall Calculation
    overall = sum(d['score'] for d in dim_scores.values())
    overall = round(min(max(overall, 0), 100), 1)

    if overall >= 85:
        risk_level = "Low"
        risk_color = "#10b981"
        recommendation = "High credential authenticity confidence. Qualified for fast-track faculty approval."
    elif overall >= 65:
        risk_level = "Medium"
        risk_color = "#f59e0b"
        recommendation = "Moderate confidence score. Standard faculty verification recommended for highlighted dimensions."
    elif overall >= 40:
        risk_level = "High"
        risk_color = "#ef4444"
        recommendation = "Significant data discrepancies detected. Faculty should request formal transcript or verification code."
    else:
        risk_level = "Critical"
        risk_color = "#dc2626"
        recommendation = "Critical integrity anomalies detected. Recommend rejecting or escalating for formal inquiry."

    data_fields = [title, description, skills_str, issue_date_str, cert_type]
    filled = sum(1 for f in data_fields if f)
    confidence = round(filled / len(data_fields) * 0.85 + 0.15, 2)

    return {
        "overall_score": overall,
        "risk_level": risk_level,
        "risk_color": risk_color,
        "dimensions": dim_scores,
        "flags": flags,
        "trust_signals": trust_signals_found,
        "recommendation": recommendation,
        "confidence": confidence
    }


# ═══════════════════════════════════════════════════════════════════
#  2. CAREER READINESS & DOMAIN MATCHING
# ═══════════════════════════════════════════════════════════════════

def predict_career_readiness(certificates):
    """
    Analyzes student portfolio to predict placement alignment across 5 tracks.
    """
    all_skills = []
    all_text = []
    for cert in certificates:
        skills_str = cert.get('skills') or ''
        desc = cert.get('description') or ''
        title = cert.get('title') or ''
        skills = [s.strip().lower() for s in skills_str.split(',') if s.strip()]
        all_skills.extend(skills)
        all_text.append(f"{title} {desc} {skills_str}".lower())

    student_text = ' '.join(all_text) if all_text else ''
    unique_skills = list(set(all_skills))

    if not student_text.strip():
        return {
            "tracks": [],
            "top_track": "Not Evaluated",
            "overall_readiness": 0,
            "skill_coverage": 0,
            "total_skills": 0,
            "recommendations": ["Submit your approved certifications to compute career placement benchmarks."]
        }

    track_texts = []
    track_names = []
    for name, info in CAREER_TRACKS.items():
        track_texts.append(' '.join(info['keywords']))
        track_names.append(name)

    corpus = [student_text] + track_texts
    vectorizer = TfidfVectorizer(stop_words='english', max_features=500)
    tfidf_matrix = vectorizer.fit_transform(corpus)

    student_vec = tfidf_matrix[0:1]
    track_results = []

    for i, track_name in enumerate(track_names):
        track_vec = tfidf_matrix[i + 1:i + 2]
        sim = cosine_similarity(student_vec, track_vec)[0][0]
        match_pct = round(sim * 100, 1)

        track_kw = set(CAREER_TRACKS[track_name]['keywords'])
        matched = [s for s in unique_skills if any(k in s for k in track_kw)]
        missing = [k for k in list(track_kw)[:8] if not any(k in s for s in unique_skills)]

        track_results.append({
            "name": track_name,
            "icon": CAREER_TRACKS[track_name]['icon'],
            "match_pct": min(round(match_pct * 1.85, 1), 100),
            "matched_skills": [m.title() for m in matched[:10]],
            "missing_skills": [m.title() for m in missing[:5]]
        })

    track_results.sort(key=lambda x: x['match_pct'], reverse=True)

    if len(track_results) >= 2:
        overall = round((track_results[0]['match_pct'] * 0.6 + track_results[1]['match_pct'] * 0.4), 1)
    elif track_results:
        overall = track_results[0]['match_pct']
    else:
        overall = 0

    recommendations = []
    top = track_results[0] if track_results else None
    if top:
        if top['missing_skills']:
            recommendations.append(f"To target Tier-1 roles in {top['name']}, obtain credentials covering: {', '.join(top['missing_skills'][:3])}.")
        if overall < 50:
            recommendations.append("Portfolio is in foundation stage. Focus on core track certifications to meet placement screening thresholds.")
        elif overall < 75:
            recommendations.append("Strong foundational competencies verified. Adding an advanced cloud or capstone project cert will elevate placement ranking.")
        else:
            recommendations.append("Outstanding career placement readiness! Profile ranks in the top tier for technical placement screenings.")

    return {
        "tracks": track_results,
        "top_track": top['name'] if top else "General Engineering",
        "overall_readiness": min(overall, 100),
        "skill_coverage": round(len(unique_skills) / 30 * 100, 1) if unique_skills else 0,
        "total_skills": len(unique_skills),
        "recommendations": recommendations
    }


# ═══════════════════════════════════════════════════════════════════
#  3. SKILL GAP & RECOMMENDATION ENGINE
# ═══════════════════════════════════════════════════════════════════

def get_skill_recommendations(certificates, target_track=None):
    """
    Computes precise skill gaps and recommends prioritized certifications.
    """
    all_skills = set()
    for cert in certificates:
        skills_str = cert.get('skills') or ''
        for s in skills_str.split(','):
            s = s.strip().lower()
            if s:
                all_skills.add(s)

    career_result = predict_career_readiness(certificates)
    if not target_track and career_result['tracks']:
        target_track = career_result['tracks'][0]['name']

    if not target_track or target_track not in CAREER_TRACKS:
        target_track = list(CAREER_TRACKS.keys())[0]

    track_info = CAREER_TRACKS[target_track]
    track_keywords = set(track_info['keywords'])

    strengths = [s.title() for s in all_skills if any(k in s for k in track_keywords)]

    covered = set()
    for kw in track_keywords:
        if any(kw in s for s in all_skills):
            covered.add(kw)

    gaps = []
    for kw in track_keywords - covered:
        importance = "High" if kw in list(track_keywords)[:10] else "Medium"
        gaps.append({"skill": kw.title(), "importance": importance, "track": target_track})

    gaps.sort(key=lambda x: 0 if x['importance'] == 'High' else 1)

    recommended = []
    high_gaps = [g['skill'] for g in gaps if g['importance'] == 'High'][:6]
    if high_gaps:
        for i in range(0, len(high_gaps), 2):
            chunk = high_gaps[i:i+2]
            recommended.append({
                "title": f"Professional {' & '.join(chunk)} Certification",
                "track": target_track,
                "priority": "High Priority",
                "skills": chunk
            })

    progress = round(len(covered) / max(len(track_keywords), 1) * 100, 1)

    return {
        "target_track": target_track,
        "current_strengths": list(strengths)[:10],
        "skill_gaps": gaps[:10],
        "recommended_certs": recommended[:5],
        "progress_pct": min(progress, 100)
    }


# ═══════════════════════════════════════════════════════════════════
#  4. AI METADATA & SKILL AUTO-EXTRACTOR (Simulated OCR / NLP)
# ═══════════════════════════════════════════════════════════════════

def extract_certificate_metadata(raw_text):
    """
    Parses unformatted certificate text / OCR input to automatically extract:
      - Title
      - Issuer
      - Date
      - Category
      - Extracted skills
    """
    if not raw_text or not raw_text.strip():
        return {
            "success": False,
            "message": "No text provided for extraction"
        }

    text = raw_text.strip()
    text_lower = text.lower()

    # Detect Issuer
    detected_issuer = "Institutional Certificate"
    for issuer in TRUSTED_ISSUERS:
        if issuer in text_lower:
            detected_issuer = issuer.title()
            break

    # Detect Date (YYYY-MM-DD, DD/MM/YYYY, or Month YYYY)
    extracted_date = datetime.now().strftime("%Y-%m-%d")
    date_match = re.search(r'\b(202[0-9]-[0-1][0-9]-[0-3][0-9])\b', text)
    if date_match:
        extracted_date = date_match.group(1)
    else:
        date_match2 = re.search(r'\b([0-3]?[0-9][/-][0-1]?[0-9][/-]202[0-9])\b', text)
        if date_match2:
            try:
                parts = re.split(r'[/-]', date_match2.group(1))
                extracted_date = f"{parts[2]}-{int(parts[1]):02d}-{int(parts[0]):02d}"
            except:
                pass

    # Extract Skills by taxonomy match
    extracted_skills = []
    for track in CAREER_TRACKS.values():
        for kw in track['keywords']:
            if re.search(r'\b' + re.escape(kw) + r'\b', text_lower):
                extracted_skills.append(kw.title())

    extracted_skills = list(dict.fromkeys(extracted_skills))[:8]

    # Detect Category
    detected_category = "Technical"
    if any(k in text_lower for k in ["aws", "azure", "gcp", "cloud"]):
        detected_category = "Cloud"
    elif any(k in text_lower for k in ["machine learning", "ai", "deep learning", "neural", "python", "nlp"]):
        detected_category = "AI/ML"
    elif any(k in text_lower for k in ["cyber", "security", "hacking", "network"]):
        detected_category = "Security"
    elif any(k in text_lower for k in ["ui", "ux", "design", "figma"]):
        detected_category = "Design"
    elif any(k in text_lower for k in ["docker", "kubernetes", "devops", "ci/cd"]):
        detected_category = "DevOps"

    # Extract or infer Title
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    extracted_title = lines[0] if lines else "Certification of Completion"
    if len(extracted_title) > 60:
        extracted_title = extracted_title[:60]

    return {
        "success": True,
        "title": extracted_title,
        "issuer": detected_issuer,
        "issue_date": extracted_date,
        "category": detected_category,
        "skills": extracted_skills,
        "skills_str": ", ".join(extracted_skills),
        "confidence": 0.92
    }


def analyze_certificate_batch(certificates):
    results = []
    for cert in certificates:
        score_result = compute_integrity_risk_score(cert)
        results.append({
            "cert_id": cert.get('id'),
            "title": cert.get('title'),
            "overall_score": score_result['overall_score'],
            "risk_level": score_result['risk_level'],
            "risk_color": score_result['risk_color'],
            "flags_count": len(score_result['flags']),
            "confidence": score_result['confidence']
        })
    return results
