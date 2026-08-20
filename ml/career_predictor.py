"""
ml/career_predictor.py - Multi-Track Career Readiness Engine
Vectorizes student verified credentials using TF-IDF & Cosine Similarity
to compute career domain alignment percentages across 6 major technology tracks.
"""

from collections import Counter
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from ml.skill_extractor import extract_skills_from_text

CAREER_TRACKS = {
    "Full-Stack Web & Cloud Systems": {
        "keywords": [
            "html", "css", "javascript", "typescript", "react", "react.js", "angular", "vue",
            "next.js", "node.js", "express", "django", "flask", "spring boot", "rest api",
            "graphql", "sql", "mysql", "postgresql", "mongodb", "aws", "docker", "microservices", "git"
        ],
        "core_skills": ["React", "Node.js", "SQL", "REST API", "JavaScript", "Docker"],
        "icon": "globe",
        "description": "Enterprise web application development, microservices, and reactive full-stack engineering."
    },
    "Data Science, AI & Machine Learning": {
        "keywords": [
            "python", "r", "numpy", "pandas", "scipy", "matplotlib", "seaborn", "scikit-learn",
            "tensorflow", "keras", "pytorch", "deep learning", "machine learning", "nlp",
            "computer vision", "data analytics", "statistics", "sql", "transformers", "llm"
        ],
        "core_skills": ["Python", "Pandas", "Scikit-Learn", "Machine Learning", "SQL", "Deep Learning"],
        "icon": "brain",
        "description": "Predictive analytics, deep neural networks, statistical modeling, and NLP intelligence."
    },
    "Cloud Architecture & DevOps": {
        "keywords": [
            "aws", "azure", "gcp", "cloud computing", "ec2", "s3", "iam", "docker",
            "kubernetes", "ci/cd", "jenkins", "terraform", "ansible", "linux", "bash",
            "microservices", "serverless", "nginx", "monitoring"
        ],
        "core_skills": ["AWS", "Docker", "Kubernetes", "CI/CD", "Linux", "Terraform"],
        "icon": "cloud",
        "description": "Cloud native infrastructure design, Kubernetes container orchestration, and automated CI/CD pipelines."
    },
    "Cybersecurity & Network Defense": {
        "keywords": [
            "cybersecurity", "ethical hacking", "penetration testing", "network security",
            "cryptography", "firewall", "wireshark", "metasploit", "soc", "siem",
            "vulnerability assessment", "linux", "networking", "owasp"
        ],
        "core_skills": ["Cybersecurity", "Network Security", "Ethical Hacking", "Cryptography", "Linux"],
        "icon": "shield",
        "description": "Threat vulnerability mitigation, network hardening, cryptographic defense, and penetration testing."
    },
    "Mobile Application Engineering": {
        "keywords": [
            "react native", "flutter", "dart", "swift", "kotlin", "android", "ios",
            "mobile", "firebase", "rest api", "graphql", "ui/ux", "javascript", "typescript"
        ],
        "core_skills": ["React Native", "Flutter", "Kotlin", "Swift", "Firebase"],
        "icon": "smartphone",
        "description": "Native and cross-platform mobile application architecture for iOS and Android ecosystems."
    },
    "Embedded Systems & IoT": {
        "keywords": [
            "c", "c++", "embedded", "arduino", "raspberry pi", "iot", "sensors",
            "vlsi", "verilog", "microcontroller", "mqtt", "fpga", "rtos"
        ],
        "core_skills": ["C++", "IoT", "Embedded", "Arduino", "Sensors"],
        "icon": "cpu",
        "description": "Microcontroller firmware programming, sensor mesh telemetry, and hardware integration."
    }
}


def predict_career_readiness(student_certificates):
    """
    Computes career domain match scores (0-100%) for each industry track.
    Returns:
      - primary_track (dict)
      - track_scores (dict)
      - verified_skills (list)
      - skill_counts (dict)
    """
    all_text_tokens = []
    verified_skills = set()

    for cert in (student_certificates or []):
        t = f"{cert.get('title', '')} {cert.get('description', '')} {cert.get('skills', '')}".lower()
        all_text_tokens.append(t)
        if cert.get('skills'):
            for s in cert['skills'].split(','):
                if s.strip():
                    verified_skills.add(s.strip().title())

    student_corpus = " ".join(all_text_tokens) if all_text_tokens else ""
    track_scores = {}

    for track_name, track_info in CAREER_TRACKS.items():
        track_kw = track_info["keywords"]
        track_doc = " ".join(track_kw)

        if not student_corpus.strip():
            track_scores[track_name] = {
                "score": 0.0,
                "confidence": "Unranked",
                "matched_skills": [],
                "core_skills": track_info["core_skills"],
                "icon": track_info["icon"],
                "description": track_info["description"]
            }
            continue

        try:
            vec = TfidfVectorizer(ngram_range=(1, 2))
            tfidf = vec.fit_transform([student_corpus, track_doc])
            cos_sim = float(cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0])
        except Exception:
            cos_sim = 0.0

        # Exact matched keywords
        matched = []
        for kw in track_kw:
            if kw in student_corpus:
                matched.append(kw.title() if len(kw) > 4 else kw.upper())

        # Hybrid score (Cosine Sim + Coverage Bonus)
        coverage_ratio = len(matched) / len(track_kw) if track_kw else 0
        raw_score = (cos_sim * 0.65) + (coverage_ratio * 0.35)
        # Scale non-linearly to percentage (0 - 100)
        final_pct = min(100.0, round(raw_score * 170.0, 1))

        if final_pct >= 75: confidence = "High Readiness"
        elif final_pct >= 50: confidence = "Moderate Match"
        elif final_pct >= 25: confidence = "Developing Skillset"
        else: confidence = "Foundational"

        track_scores[track_name] = {
            "score": final_pct,
            "confidence": confidence,
            "matched_skills": list(set(matched))[:10],
            "core_skills": track_info["core_skills"],
            "icon": track_info["icon"],
            "description": track_info["description"]
        }

    # Identify primary top track
    sorted_tracks = sorted(track_scores.items(), key=lambda x: x[1]["score"], reverse=True)
    top_track_name = sorted_tracks[0][0] if sorted_tracks else "Full-Stack Web & Cloud Systems"
    primary_track = {
        "name": top_track_name,
        "score": track_scores[top_track_name]["score"],
        "confidence": track_scores[top_track_name]["confidence"],
        "matched_skills": track_scores[top_track_name]["matched_skills"],
        "description": track_scores[top_track_name]["description"],
        "icon": track_scores[top_track_name]["icon"]
    }

    return {
        "primary_track": primary_track,
        "track_scores": track_scores,
        "verified_skills": sorted(list(verified_skills)),
        "total_verified_skills": len(verified_skills)
    }
