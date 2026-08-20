"""
ml/placement_predictor.py - Multi-Metric Placement Readiness Index
Evaluates student technical skill density, verified certificate count, AI integrity history,
academic cohort velocity, and domain focus to calculate an actionable Placement Readiness Score (0-100%).
"""

from ml.career_predictor import predict_career_readiness


def compute_placement_readiness(student_profile, student_certificates):
    """
    Computes overall placement readiness % and dimension breakdown.
    Dimensions:
      1. Technical Skills Breadth (0-30%)
      2. Verified Certifications & Authenticity (0-25%)
      3. Domain Focus & Track Mastery (0-20%)
      4. Academic Year Velocity (0-15%)
      5. Portfolio Diversity (0-10%)
    """
    career_data = predict_career_readiness(student_certificates)
    verified_skills = career_data.get("verified_skills", [])
    primary_track = career_data.get("primary_track", {})
    track_score = primary_track.get("score", 0)

    certs = student_certificates or []
    approved_certs = [c for c in certs if c.get('status') == 'approved']
    total_certs_count = len(certs)
    approved_count = len(approved_certs)

    # 1. Technical Skills Breadth (0-30%)
    # Target benchmark: 8+ industry skills for 100%
    skill_count = len(verified_skills)
    dim_tech = min(30.0, (skill_count / 8.0) * 30.0)

    # 2. Verified Certifications & Authenticity (0-25%)
    # Target benchmark: 4+ verified credentials with high integrity
    avg_integrity = 0
    if approved_certs:
        scores = [c.get('integrity_score', 0) for c in approved_certs if c.get('integrity_score', 0) > 0]
        avg_integrity = sum(scores) / len(scores) if scores else 85
    dim_certs = min(25.0, (approved_count / 4.0) * 20.0 + (avg_integrity / 100.0) * 5.0)

    # 3. Domain Focus & Track Mastery (0-20%)
    dim_domain = (track_score / 100.0) * 20.0

    # 4. Academic Year Velocity (0-15%)
    year = student_profile.get('year', 1) if student_profile else 1
    # Higher expected velocity for Year 3/4
    expected_certs_by_year = {1: 1, 2: 2, 3: 4, 4: 5}
    exp = expected_certs_by_year.get(year, 3)
    dim_velocity = min(15.0, (approved_count / float(exp)) * 15.0)

    # 5. Portfolio Diversity (0-10%)
    categories = set()
    for c in approved_certs:
        if c.get('cert_type'): categories.add(c['cert_type'])
    dim_diversity = min(10.0, (len(categories) / 3.0) * 10.0)

    # Final Overall Placement Score
    overall_readiness = round(dim_tech + dim_certs + dim_domain + dim_velocity + dim_diversity, 1)
    overall_readiness = max(0.0, min(100.0, overall_readiness))

    if overall_readiness >= 80:
        badge_label = "Tier-1 Placement Ready"
        badge_color = "success"
    elif overall_readiness >= 65:
        badge_label = "Placement Competitive"
        badge_color = "brand"
    elif overall_readiness >= 45:
        badge_label = "Developing Profile"
        badge_color = "warning"
    else:
        badge_label = "Early Stage"
        badge_color = "neutral"

    # Actionable Improvement Tips
    tips = []
    if skill_count < 6:
        tips.append(f"Add 2 more technical skills to your portfolio to gain +{round((2/8)*30, 1)}% in Technical Breadth.")
    if approved_count < 3:
        tips.append("Submit 1 new technical capstone or certification for faculty mentor verification.")
    if track_score < 70:
        tips.append(f"Focus on core {primary_track.get('name', 'domain')} frameworks to sharpen your primary career track.")

    if not tips:
        tips.append("Excellent profile! Focus on mock technical interviews and system design challenges.")

    return {
        "overall_score": overall_readiness,
        "badge_label": badge_label,
        "badge_color": badge_color,
        "primary_domain": primary_track.get("name", "Engineering"),
        "domain_match_pct": track_score,
        "verified_skills_count": skill_count,
        "approved_credentials_count": approved_count,
        "dimensions": {
            "technical_breadth": {"score": round(dim_tech, 1), "max": 30, "pct": round((dim_tech/30)*100)},
            "verified_credentials": {"score": round(dim_certs, 1), "max": 25, "pct": round((dim_certs/25)*100)},
            "domain_mastery": {"score": round(dim_domain, 1), "max": 20, "pct": round((dim_domain/20)*100)},
            "academic_velocity": {"score": round(dim_velocity, 1), "max": 15, "pct": round((dim_velocity/15)*100)},
            "portfolio_diversity": {"score": round(dim_diversity, 1), "max": 10, "pct": round((dim_diversity/10)*100)}
        },
        "improvement_tips": tips
    }
