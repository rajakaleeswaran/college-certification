"""
ml/certificate_analyzer.py - 5-Factor Certificate Integrity Risk & Anomaly Analyzer
Evaluates credibility, metadata consistency, issuer trust levels, credential verification codes,
and duplicate anomalies to generate a scientific Integrity Risk Score (0-100).
"""

import json
from datetime import datetime
from ml.skill_extractor import extract_skills_from_text
from ml.duplicate_detector import check_duplicate_certificate

# Accredited Platforms with verified public registries
TRUSTED_ISSUERS = {
    "amazon web services": {"trust": 1.0, "name": "AWS"},
    "aws": {"trust": 1.0, "name": "AWS"},
    "google": {"trust": 1.0, "name": "Google Cloud"},
    "google cloud": {"trust": 1.0, "name": "Google Cloud"},
    "microsoft": {"trust": 1.0, "name": "Microsoft Azure"},
    "oracle": {"trust": 0.95, "name": "Oracle"},
    "cisco": {"trust": 0.95, "name": "Cisco Networking Academy"},
    "coursera": {"trust": 0.90, "name": "Coursera Partner University"},
    "edx": {"trust": 0.90, "name": "edX Institutional"},
    "datacamp": {"trust": 0.85, "name": "DataCamp"},
    "hackerrank": {"trust": 0.85, "name": "HackerRank Skill Certificate"},
    "leetcode": {"trust": 0.80, "name": "LeetCode"},
    "udemy": {"trust": 0.75, "name": "Udemy Academy"},
    "freecodecamp": {"trust": 0.85, "name": "freeCodeCamp"},
    "nptel": {"trust": 0.95, "name": "NPTEL / SWAYAM (Govt of India)"},
    "ibm": {"trust": 0.95, "name": "IBM Skills Network"},
    "stanford": {"trust": 1.0, "name": "Stanford University"},
    "mit": {"trust": 1.0, "name": "MIT OpenCourseWare"}
}


def compute_integrity_risk_score(certificate, user_existing_certs=None):
    """
    Computes a multi-dimensional AI Certificate Integrity Risk Score (0-100).
    Dimensions:
      1. Metadata Consistency (0-20)
      2. Skill Taxonomy Relevancy (0-20)
      3. Issuer Trust & Registry (0-20)
      4. Temporal Validity (0-20)
      5. Credential Verification Proof (0-20)
    """
    title = (certificate.get('title') or '').strip()
    description = (certificate.get('description') or '').strip()
    skills_str = (certificate.get('skills') or '').strip()
    issue_date_str = (certificate.get('issue_date') or '').strip()
    source_url = (certificate.get('source_url') or '').strip()
    file_path = (certificate.get('file_path') or '').strip()

    combined_text = f"{title} {description} {skills_str} {source_url}".lower()
    flags = []
    trust_signals = []

    # ── Dimension 1: Metadata Consistency (0-20) ────────────────────
    dim1_score = 20.0
    if not title or len(title) < 4:
        dim1_score -= 10
        flags.append("Missing or excessively brief certificate title")
    if not description or len(description) < 15:
        dim1_score -= 5
        flags.append("Brief curriculum description provided")
    if len(title) > 8 and len(description) > 40:
        trust_signals.append("Detailed syllabus and title provided")

    # ── Dimension 2: Skill Taxonomy Relevancy (0-20) ─────────────────
    dim2_score = 20.0
    extracted_skills = extract_skills_from_text(combined_text)
    if not extracted_skills["skills"]:
        dim2_score -= 12
        flags.append("No standardized technical skills mapped from text")
    elif len(extracted_skills["skills"]) >= 3:
        dim2_score = 20.0
        trust_signals.append(f"Mapped {len(extracted_skills['skills'])} industry taxonomy skills")
    else:
        dim2_score = 15.0

    # ── Dimension 3: Issuer Trust & Registry (0-20) ──────────────────
    dim3_score = 10.0 # baseline neutral
    matched_issuer = None
    for k, v in TRUSTED_ISSUERS.items():
        if k in combined_text:
            matched_issuer = v["name"]
            dim3_score = v["trust"] * 20.0
            trust_signals.append(f"Issued by accredited organization ({matched_issuer})")
            break

    if not matched_issuer:
        flags.append("Issuer not in top accredited registry (Manual review required)")

    # ── Dimension 4: Temporal Validity (0-20) ────────────────────────
    dim4_score = 20.0
    if issue_date_str:
        try:
            issue_date = datetime.fromisoformat(issue_date_str.replace('Z', ''))
            now = datetime.now()
            if issue_date > now:
                dim4_score -= 15
                flags.append("Future completion date reported")
            elif (now - issue_date).days > 365 * 6:
                dim4_score -= 6
                flags.append("Certificate completed over 6 years ago")
            else:
                trust_signals.append("Valid contemporary completion date")
        except Exception:
            dim4_score -= 5
            flags.append("Date format irregular")
    else:
        dim4_score -= 10
        flags.append("No issue date specified")

    # ── Dimension 5: Credential ID & Proof (0-20) ────────────────────
    dim5_score = 5.0
    if source_url and ('http://' in source_url or 'https://' in source_url):
        dim5_score += 10
        trust_signals.append("Public verification URL supplied")
    if file_path:
        dim5_score += 5
        trust_signals.append("Document/PDF attachment uploaded")

    # ── Check Duplicates Anomaly ─────────────────────────────────────
    duplicate_info = {"is_duplicate": False, "max_similarity": 0.0}
    if user_existing_certs:
        duplicate_info = check_duplicate_certificate(certificate, user_existing_certs)
        if duplicate_info["is_duplicate"]:
            dim1_score = max(dim1_score - 10, 0)
            flags.append(f"Duplicate Anomaly: {duplicate_info['reason']}")

    # Total Score
    total_score = max(0.0, min(100.0, dim1_score + dim2_score + dim3_score + dim4_score + dim5_score))
    total_score = round(total_score, 1)

    if total_score >= 80:
        risk_level = "Low"
        risk_color = "success"
    elif total_score >= 60:
        risk_level = "Medium"
        risk_color = "warning"
    elif total_score >= 40:
        risk_level = "High"
        risk_color = "danger"
    else:
        risk_level = "Critical"
        risk_color = "danger"

    return {
        "overall_score": total_score,
        "risk_level": risk_level,
        "risk_color": risk_color,
        "flags": flags,
        "trust_signals": trust_signals,
        "duplicate_detection": duplicate_info,
        "dimensions": {
            "metadata_consistency": {"score": round(dim1_score, 1), "max": 20, "pct": round((dim1_score/20)*100)},
            "skill_relevancy": {"score": round(dim2_score, 1), "max": 20, "pct": round((dim2_score/20)*100)},
            "issuer_trust": {"score": round(dim3_score, 1), "max": 20, "pct": round((dim3_score/20)*100)},
            "temporal_validity": {"score": round(dim4_score, 1), "max": 20, "pct": round((dim4_score/20)*100)},
            "credential_proof": {"score": round(dim5_score, 1), "max": 20, "pct": round((dim5_score/20)*100)}
        }
    }
