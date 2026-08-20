"""
ml/job_matcher.py - AI Job Description Analyzer & Skill Matcher
Parses raw job descriptions, extracts required technologies using NLP,
compares against a student's verified credentials, and generates a match score with missing skill gaps.
"""

import re
from ml.skill_extractor import extract_skills_from_text


def match_job_description(job_description_text, student_verified_skills):
    """
    Analyzes job description and matches against student verified skills.
    Returns:
      - match_percentage (float 0-100%)
      - required_skills (list)
      - matched_skills (list)
      - missing_skills (list)
      - match_level (str)
      - recommendation (str)
    """
    if not job_description_text or not job_description_text.strip():
        return {
            "match_percentage": 0.0,
            "required_skills": [],
            "matched_skills": [],
            "missing_skills": [],
            "match_level": "No Text Provided",
            "recommendation": "Please paste a job description to analyze."
        }

    # Extract required skills from the Job Description
    extracted = extract_skills_from_text(job_description_text)
    required_skills = extracted["skills"]

    if not required_skills:
        return {
            "match_percentage": 50.0,
            "required_skills": ["General Engineering", "Problem Solving", "Communication"],
            "matched_skills": ["General Engineering"],
            "missing_skills": [],
            "match_level": "General Role",
            "recommendation": "Job description contains generic qualifications. Focus on fundamental problem solving."
        }

    # Normalize student skills for comparison
    student_skill_set = set(s.lower() for s in (student_verified_skills or []))

    matched = []
    missing = []

    for req in required_skills:
        if req.lower() in student_skill_set:
            matched.append(req)
        else:
            missing.append(req)

    match_ratio = len(matched) / float(len(required_skills)) if required_skills else 0
    match_pct = round(match_ratio * 100, 1)

    if match_pct >= 80:
        match_level = "Excellent Match (Strong Fit)"
        recommendation = "You satisfy the core technical requirements for this role! Tailor your resume to emphasize your verified projects."
    elif match_pct >= 60:
        match_level = "Good Match (Competitive Fit)"
        recommendation = f"You meet majority of requirements. Learning {missing[0] if missing else 'key frameworks'} will make your application stand out."
    elif match_pct >= 40:
        match_level = "Moderate Match (Partial Fit)"
        recommendation = f"You match some requirements. Focus on bridging the top missing skills: {', '.join(missing[:3])}."
    else:
        match_level = "Significant Skill Gap"
        recommendation = f"This position requires specific technologies not yet verified on your profile. Prioritize: {', '.join(missing[:3])}."

    return {
        "match_percentage": match_pct,
        "required_skills_count": len(required_skills),
        "required_skills": required_skills,
        "matched_skills": matched,
        "matched_count": len(matched),
        "missing_skills": missing,
        "missing_count": len(missing),
        "match_level": match_level,
        "recommendation": recommendation
    }
