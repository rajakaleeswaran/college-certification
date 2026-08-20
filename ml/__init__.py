"""
ml package - Modular Machine Learning, NLP, OCR & Career Intelligence Subsystem
"""

from ml.skill_extractor import extract_skills_from_text, normalize_skill_string
from ml.ocr_engine import extract_text_from_file, extract_certificate_metadata
from ml.duplicate_detector import check_duplicate_certificate
from ml.certificate_analyzer import compute_integrity_risk_score
from ml.career_predictor import predict_career_readiness, CAREER_TRACKS
from ml.skill_gap_engine import get_skill_gaps
from ml.placement_predictor import compute_placement_readiness
from ml.job_matcher import match_job_description
