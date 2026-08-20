"""
ml_engine.py - Unified Adapter for the Modular ml/ Subsystem
Delegates to specialized modules:
  - ml.certificate_analyzer
  - ml.career_predictor
  - ml.skill_gap_engine
  - ml.ocr_engine
  - ml.placement_predictor
  - ml.job_matcher
"""

from ml.certificate_analyzer import compute_integrity_risk_score
from ml.career_predictor import predict_career_readiness, CAREER_TRACKS
from ml.skill_gap_engine import get_skill_gaps as get_skill_recommendations
from ml.ocr_engine import extract_certificate_metadata
from ml.placement_predictor import compute_placement_readiness
from ml.job_matcher import match_job_description


def analyze_certificate_batch(certificates):
    """Batch analysis helper for analytics dashboards."""
    results = []
    for cert in certificates:
        scored = compute_integrity_risk_score(cert)
        results.append({
            "id": cert.get("id"),
            "title": cert.get("title"),
            "overall_score": scored["overall_score"],
            "risk_level": scored["risk_level"],
            "risk_color": scored["risk_color"],
            "status": cert.get("status")
        })
    return results
