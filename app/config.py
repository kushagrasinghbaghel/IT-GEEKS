"""
Application Configuration for Medi-Caps Academic Regulations QA System
"""
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPUS_DIR = os.path.join(BASE_DIR, "corpus")
STATIC_DIR = os.path.join(BASE_DIR, "static")

# University Details
UNIVERSITY_NAME = "Medi-Caps University, Indore"
CAMPUS_LOCATION = "A.B. Road, Pigdambar, Rau, Indore, Madhya Pradesh - 453331"

# Retrieval & Decision Thresholds
SIMILARITY_THRESHOLD_COVERED = 0.22  # Minimum similarity to be considered covered
MIN_KEYWORD_MATCH_RATIO = 0.20       # Minimum meaningful term overlap

# Auth Settings
SECRET_KEY = "medicaps_regulations_secure_jwt_secret_key_2024"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 24 hours
