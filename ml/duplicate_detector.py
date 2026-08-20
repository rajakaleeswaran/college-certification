"""
ml/duplicate_detector.py - TF-IDF & Cosine Similarity Duplicate Anomaly Engine
Detects duplicate or near-identical certificate submissions by comparing
text payloads, credential URLs, and title vectors across a student's history.
"""

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def check_duplicate_certificate(new_cert, existing_certs, similarity_threshold=0.85):
    """
    Compares a newly submitted certificate against existing records for the same user.
    Returns:
      - is_duplicate (bool)
      - max_similarity (float 0.0 - 1.0)
      - matched_certificate (dict or None)
      - reason (str)
    """
    if not existing_certs:
        return {
            "is_duplicate": False,
            "max_similarity": 0.0,
            "matched_cert_id": None,
            "matched_cert_title": None,
            "reason": "No previous certificates on record"
        }

    new_title = (new_cert.get('title') or '').strip().lower()
    new_desc = (new_cert.get('description') or '').strip().lower()
    new_url = (new_cert.get('source_url') or '').strip().lower()
    new_skills = (new_cert.get('skills') or '').strip().lower()

    # Exact URL Match
    if new_url:
        for ec in existing_certs:
            e_url = (ec.get('source_url') or '').strip().lower()
            if e_url and e_url == new_url and ec.get('id') != new_cert.get('id'):
                return {
                    "is_duplicate": True,
                    "max_similarity": 1.0,
                    "matched_cert_id": ec.get('id'),
                    "matched_cert_title": ec.get('title'),
                    "reason": f"Exact matching credential URL with previous submission '{ec.get('title')}'"
                }

    # Vector text comparison (Title + Desc + Skills)
    new_text = f"{new_title} {new_desc} {new_skills}".strip()
    if not new_text:
        return {"is_duplicate": False, "max_similarity": 0.0, "matched_cert_id": None, "reason": "Insufficient text"}

    corpus = [new_text]
    valid_existing = []

    for ec in existing_certs:
        if ec.get('id') == new_cert.get('id'):
            continue
        e_text = f"{(ec.get('title') or '').lower()} {(ec.get('description') or '').lower()} {(ec.get('skills') or '').lower()}".strip()
        if e_text:
            corpus.append(e_text)
            valid_existing.append(ec)

    if len(corpus) <= 1:
        return {"is_duplicate": False, "max_similarity": 0.0, "matched_cert_id": None, "reason": "No other records to compare"}

    try:
        vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(corpus)
        sim_scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

        max_idx = int(np.argmax(sim_scores))
        max_score = float(sim_scores[max_idx])

        if max_score >= similarity_threshold:
            matched = valid_existing[max_idx]
            return {
                "is_duplicate": True,
                "max_similarity": round(max_score * 100, 1),
                "matched_cert_id": matched.get('id'),
                "matched_cert_title": matched.get('title'),
                "reason": f"High text & skill similarity ({round(max_score*100, 1)}%) with '{matched.get('title')}'"
            }
        else:
            return {
                "is_duplicate": False,
                "max_similarity": round(max_score * 100, 1),
                "matched_cert_id": None,
                "matched_cert_title": None,
                "reason": "Unique submission verified"
            }
    except Exception as e:
        return {
            "is_duplicate": False,
            "max_similarity": 0.0,
            "matched_cert_id": None,
            "reason": f"Vector analysis fallback: {str(e)}"
        }
