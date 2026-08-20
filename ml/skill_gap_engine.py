"""
ml/skill_gap_engine.py - Skill Gap Analyzer & 12-Week Roadmap Engine
Analyzes verified student credentials against industry profiles to calculate missing skills
and automatically generate a structured, phased 12-week personalized learning roadmap.
"""

from ml.career_predictor import CAREER_TRACKS, predict_career_readiness

RECOMMENDED_RESOURCES = {
    "Docker": {"platform": "Docker Official & freeCodeCamp", "duration": "2 Weeks", "level": "Intermediate"},
    "Kubernetes": {"platform": "Linux Foundation (edX)", "duration": "3 Weeks", "level": "Advanced"},
    "AWS": {"platform": "AWS Skill Builder & Cloud Practitioner", "duration": "4 Weeks", "level": "Foundational"},
    "Spring Boot": {"platform": "Java Brains & Spring Academy", "duration": "3 Weeks", "level": "Intermediate"},
    "System Design": {"platform": "Grokking the System Design Interview", "duration": "3 Weeks", "level": "Advanced"},
    "CI/CD": {"platform": "GitHub Actions Official Labs", "duration": "1 Week", "level": "Intermediate"},
    "Machine Learning": {"platform": "Coursera Andrew Ng DeepLearning.AI", "duration": "4 Weeks", "level": "Intermediate"},
    "Deep Learning": {"platform": "Fast.ai & PyTorch Tutorials", "duration": "4 Weeks", "level": "Advanced"},
    "React": {"platform": "Scrimba & React.dev Interactive", "duration": "2 Weeks", "level": "Intermediate"},
    "Node.js": {"platform": "The Odin Project & NodeSchool", "duration": "2 Weeks", "level": "Intermediate"},
    "TypeScript": {"platform": "TypeScript Handbook & Exercism", "duration": "1 Week", "level": "Intermediate"},
    "GraphQL": {"platform": "Apollo Odyssey Tutorials", "duration": "1 Week", "level": "Intermediate"},
    "Cybersecurity": {"platform": "TryHackMe & Cisco Academy", "duration": "3 Weeks", "level": "Intermediate"},
    "Ethical Hacking": {"platform": "PortSwigger Web Security Academy", "duration": "4 Weeks", "level": "Advanced"},
    "SQL": {"platform": "SQLZoo & Mode Analytics", "duration": "1 Week", "level": "Foundational"},
    "Terraform": {"platform": "HashiCorp Learn Portal", "duration": "2 Weeks", "level": "Intermediate"}
}


def get_skill_gaps(student_certificates, target_track_name=None):
    """
    Computes exact missing skills comparing student's verified skills against target industry track.
    Returns:
      - target_track
      - acquired_skills
      - missing_skills (ordered by priority)
      - recommendations (with courses and learning resources)
      - roadmap_12_weeks (phase-by-phase learning timeline)
    """
    career_summary = predict_career_readiness(student_certificates)
    if not target_track_name or target_track_name not in CAREER_TRACKS:
        target_track_name = career_summary["primary_track"]["name"]

    target_info = CAREER_TRACKS.get(target_track_name, list(CAREER_TRACKS.values())[0])
    target_keywords = [k.title() if len(k) > 4 else k.upper() for k in target_info["keywords"]]
    core_skills = target_info["core_skills"]

    verified_set = set(s.lower() for s in career_summary["verified_skills"])
    acquired_skills = []
    missing_skills = []

    for kw in target_keywords:
        if kw.lower() in verified_set:
            acquired_skills.append(kw)
        else:
            missing_skills.append(kw)

    # Prioritize core skills first in missing list
    prioritized_missing = []
    for cs in core_skills:
        if cs.lower() not in verified_set and cs not in prioritized_missing:
            prioritized_missing.append(cs)
    for ms in missing_skills:
        if ms not in prioritized_missing:
            prioritized_missing.append(ms)

    top_missing = prioritized_missing[:6]

    # Build recommendations
    recommendations = []
    for skill in top_missing:
        res = RECOMMENDED_RESOURCES.get(skill, {
            "platform": "Accredited MOOC / Official Documentation",
            "duration": "2 Weeks",
            "level": "Intermediate"
        })
        recommendations.append({
            "skill": skill,
            "resource": res["platform"],
            "duration": res["duration"],
            "level": res["level"]
        })

    # Generate 12-Week Roadmap
    roadmap = _generate_12_week_roadmap(top_missing, acquired_skills, target_track_name)

    return {
        "target_track": target_track_name,
        "track_readiness": career_summary["track_scores"].get(target_track_name, {}).get("score", 0),
        "acquired_skills": acquired_skills,
        "acquired_count": len(acquired_skills),
        "missing_skills": top_missing,
        "missing_count": len(prioritized_missing),
        "recommendations": recommendations,
        "roadmap_12_weeks": roadmap
    }


def _generate_12_week_roadmap(missing_skills, acquired_skills, track_name):
    """Builds a structured 4-phase 12-week study and project roadmap."""
    s1 = missing_skills[0] if len(missing_skills) > 0 else "Advanced Architectural Design"
    s2 = missing_skills[1] if len(missing_skills) > 1 else "Cloud Deployment & Microservices"
    s3 = missing_skills[2] if len(missing_skills) > 2 else "Scalable System Architecture"
    s4 = missing_skills[3] if len(missing_skills) > 3 else "End-to-End Capstone Deployment"

    return [
        {
            "weeks": "Week 1 – 3",
            "phase": "Phase 1: Core Fundamentals & Framework Mastery",
            "focus_skill": s1,
            "tasks": [
                f"Master core architecture & syntax of {s1}",
                "Build 2 mini-projects implementing foundational patterns",
                "Complete official hands-on certification assessment"
            ],
            "milestone": f"{s1} Proficiency Certificate"
        },
        {
            "weeks": "Week 4 – 6",
            "phase": "Phase 2: Cloud Infrastructure & Integration",
            "focus_skill": s2,
            "tasks": [
                f"Integrate {s2} with existing {acquired_skills[0] if acquired_skills else 'backend'} stack",
                "Implement automated CI/CD and container workflows",
                "Optimize performance benchmarks and query caching"
            ],
            "milestone": f"Integrated {s2} Production Pipeline"
        },
        {
            "weeks": "Week 7 – 9",
            "phase": "Phase 3: System Design & Enterprise Architecture",
            "focus_skill": s3,
            "tasks": [
                f"Deep dive into {s3} scalability and resilience",
                "Implement fault-tolerant patterns and telemetry logging",
                "Conduct code reviews with faculty mentor"
            ],
            "milestone": "Full Scalable System Proof-of-Concept"
        },
        {
            "weeks": "Week 10 – 12",
            "phase": "Phase 4: Capstone Project & Placement Interview Prep",
            "focus_skill": s4,
            "tasks": [
                f"Build full-stack production capstone leveraging {s1}, {s2}, and {s3}",
                "Submit project certificate to CertPortal for mentor sign-off",
                "Complete mock technical screening & AI resume booster"
            ],
            "milestone": f"100% Placement Ready in {track_name}"
        }
    ]
