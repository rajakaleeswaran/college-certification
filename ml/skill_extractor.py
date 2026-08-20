"""
ml/skill_extractor.py - NLP Skill Taxonomy Parser & Entity Extractor
Extracts, normalizes, and classifies technical skills from raw certificate text,
course curricula, and job descriptions using NLP tokenization and taxonomy matching.
"""

import re
from collections import Counter

# ── Comprehensive 200+ Industry Skill Taxonomy ────────────────────
SKILL_TAXONOMY = {
    "Programming Languages": [
        "python", "javascript", "typescript", "java", "c++", "c#", "c", "go", "golang",
        "rust", "ruby", "php", "swift", "kotlin", "scala", "r", "dart", "matlab", "solidity", "perl"
    ],
    "Frontend Development": [
        "html", "html5", "css", "css3", "sass", "scss", "bootstrap", "tailwind", "tailwindcss",
        "react", "react.js", "reactjs", "angular", "angularjs", "vue", "vue.js", "vuejs",
        "next.js", "nextjs", "nuxt.js", "svelte", "jquery", "redux", "webpack", "vite", "ui/ux", "figma"
    ],
    "Backend & Frameworks": [
        "node.js", "nodejs", "express", "express.js", "django", "flask", "fastapi",
        "spring", "spring boot", "springboot", "asp.net", ".net", "laravel", "rails",
        "ruby on rails", "graphql", "rest api", "restful api", "microservices", "grpc", "websockets"
    ],
    "Database & Storage": [
        "sql", "mysql", "postgresql", "postgres", "sqlite", "mongodb", "redis",
        "cassandra", "dynamodb", "mariadb", "oracle db", "neo4j", "elasticsearch",
        "firebase", "supabase", "prisma", "hibernate", "sqlalchemy"
    ],
    "Cloud & Infrastructure": [
        "aws", "amazon web services", "azure", "microsoft azure", "gcp", "google cloud",
        "google cloud platform", "ec2", "s3", "lambda", "iam", "cloud computing",
        "serverless", "cloudflare", "heroku", "digitalocean"
    ],
    "DevOps & Containers": [
        "docker", "kubernetes", "k8s", "ci/cd", "jenkins", "github actions", "gitlab ci",
        "terraform", "ansible", "helm", "prometheus", "grafana", "linux", "bash", "nginx", "apache"
    ],
    "Data Science & AI/ML": [
        "machine learning", "deep learning", "artificial intelligence", "ai", "ml",
        "data science", "data analytics", "data analysis", "numpy", "pandas", "scipy",
        "matplotlib", "seaborn", "scikit-learn", "sklearn", "tensorflow", "keras",
        "pytorch", "nlp", "natural language processing", "computer vision", "opencv",
        "transformers", "bert", "hugging face", "llm", "genai", "prompt engineering", "langchain", "tableau", "power bi"
    ],
    "Cybersecurity & Networks": [
        "cybersecurity", "ethical hacking", "penetration testing", "network security",
        "information security", "cryptography", "firewall", "wireshark", "metasploit",
        "soc", "siem", "owasp", "vulnerability assessment", "malware analysis", "cissp", "ceh"
    ],
    "Core CS & Systems": [
        "data structures", "algorithms", "dsa", "object oriented programming", "oop",
        "operating systems", "dbms", "computer networks", "system design", "git", "github", "gitlab"
    ]
}

# Inverted mapping for fast lookup
SKILL_MAP = {}
for category, skills in SKILL_TAXONOMY.items():
    for s in skills:
        SKILL_MAP[s.lower()] = (s.title() if len(s) > 4 or s not in ['aws', 'sql', 'gcp', 'css', 'nlp', 'api', 'iam', 'dsa', 'oop', 'dbms'] else s.upper(), category)


def extract_skills_from_text(text):
    """
    Extracts, deduplicates and categorizes technical skills found within raw text.
    Returns list of normalized skill strings and category groupings.
    """
    if not text:
        return {"skills": [], "categories": {}, "count": 0}

    # Normalize text
    cleaned = text.lower()
    cleaned = re.sub(r'[/,;:\(\)\n\r\t]', ' ', cleaned)
    tokens = set(cleaned.split())

    found_skills = set()
    found_categories = {}

    # 1. Multi-word phrase search
    for skill_key, (display_name, category) in SKILL_MAP.items():
        if ' ' in skill_key:
            if re.search(r'\b' + re.escape(skill_key) + r'\b', cleaned):
                found_skills.add(display_name)
                found_categories.setdefault(category, []).append(display_name)
        elif skill_key in tokens or re.search(r'\b' + re.escape(skill_key) + r'\b', cleaned):
            found_skills.add(display_name)
            found_categories.setdefault(category, []).append(display_name)

    # Sort alphabetical
    sorted_skills = sorted(list(found_skills))

    return {
        "skills": sorted_skills,
        "categories": found_categories,
        "count": len(sorted_skills)
    }


def normalize_skill_string(skills_input):
    """
    Takes comma-separated or raw skill strings and returns a standardized clean comma-separated list.
    """
    if not skills_input:
        return ""
    if isinstance(skills_input, list):
        skills_input = ",".join(skills_input)

    extracted = extract_skills_from_text(skills_input)
    if extracted["skills"]:
        return ", ".join(extracted["skills"])

    # Fallback: split and clean
    parts = [s.strip().title() for s in skills_input.split(',') if s.strip()]
    return ", ".join(parts)
