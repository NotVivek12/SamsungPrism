import os
import re
import json
import logging
from typing import Dict, Any, List

import requests


def analyze_project_description(description: str) -> Dict[str, Any]:
    """
    Analyze a project description and extract required expertise domains.
    This function uses Gemma to analyze the project and identify the key expertise 
    areas needed to complete the project successfully.
    
    Args:
        description: The project description to analyze
        
    Returns:
        Dictionary containing identified expertise areas and skills
    """
    api_key = os.getenv("GEMMA_API_KEY")
    model = os.getenv("GEMMA_MODEL", "gemma-2-9b-it")
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    if not description or not api_key:
        if not api_key:
            logging.warning("GEMMA_API_KEY not set; using fallback analysis")
        return _fallback_project_analysis(description or "")

    prompt = f"""
You are an AI analyzing research projects to identify required expertise areas. Given a project description, extract the key technical domains and skills needed to successfully complete the project.

Project Description: "{description}"

Provide your analysis as a JSON object with these keys:
- "required_expertise": [array of 3-7 technical domains/fields most relevant to this project]
- "key_skills": [array of specific technical skills needed]
- "summary": A one-sentence summary of the project's technical requirements

Focus on identifying academic and research domains like "machine learning", "data science", "cybersecurity", etc. rather than soft skills or general terms. The goal is to match the project with professors who have expertise in these domains.

Return ONLY the JSON object and nothing else.
"""

    try:
        resp = requests.post(
            f"{api_url}?key={api_key}",
            headers={"Content-Type": "application/json"},
            json={
                "contents": [{
                    "parts": [{"text": prompt}]
                }]
            },
            timeout=20,
        )
        resp.raise_for_status()
        data = resp.json()

        # Extract text from response
        text = None
        try:
            text = data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            pass

        if not text:
            return _fallback_project_analysis(description)

        # Extract JSON blob
        m = re.search(r"\{[\s\S]*\}", text)
        if m:
            try:
                return json.loads(m.group(0))
            except Exception:
                pass

        # If already JSON encoded
        if isinstance(text, str):
            try:
                return json.loads(text)
            except Exception:
                pass

        return _fallback_project_analysis(description)
    except Exception as e:
        logging.warning(f"Gemma API call failed for project analysis, using fallback: {e}")
        return _fallback_project_analysis(description)


def _fallback_project_analysis(description: str) -> Dict[str, Any]:
    """
    Fallback method for project description analysis when Gemma API is unavailable.
    Uses keyword matching to extract likely expertise areas from the description.
    """
    description = (description or "").lower()
    
    # Domain keyword mapping for simple text matching
    domain_keywords = {
        "artificial intelligence": ["ai", "artificial intelligence", "machine learning", "neural network", "deep learning", "model"],
        "machine learning": ["machine learning", "ml", "model", "algorithm", "train", "classification", "regression", "cluster"],
        "data science": ["data science", "big data", "data analysis", "analytics", "data mining", "statistics", "statistical"],
        "computer vision": ["computer vision", "image processing", "object detection", "facial recognition", "opencv"],
        "natural language processing": ["nlp", "natural language", "text analysis", "sentiment analysis", "language model", "transformer"],
        "robotics": ["robot", "robotics", "automation", "autonomous", "control system"],
        "cybersecurity": ["security", "cyber", "encryption", "cryptography", "network security", "vulnerability"],
        "web development": ["web", "frontend", "backend", "full-stack", "javascript", "html", "css", "react", "node"],
        "mobile development": ["mobile", "android", "ios", "app development", "flutter", "react native"],
        "blockchain": ["blockchain", "crypto", "distributed ledger", "smart contract", "token"],
        "internet of things": ["iot", "internet of things", "embedded system", "sensor", "arduino"],
        "database systems": ["database", "sql", "nosql", "data storage", "data management"],
        "cloud computing": ["cloud", "aws", "azure", "google cloud", "serverless", "microservice"],
        "augmented reality": ["ar", "augmented reality", "virtual reality", "vr", "mixed reality", "xr"],
        "quantum computing": ["quantum", "qubit", "quantum algorithm", "quantum machine learning"],
        "bioinformatics": ["bioinformatics", "genomics", "gene", "dna", "biological data"],
        "high performance computing": ["hpc", "high performance", "parallel computing", "gpu"],
        "game development": ["game", "gaming", "unity", "unreal engine", "3d design"],
    }
    
    found_domains = {}
    
    # Count matches for each domain
    for domain, keywords in domain_keywords.items():
        matches = sum(1 for keyword in keywords if keyword in description)
        if matches > 0:
            found_domains[domain] = matches
    
    # Sort domains by number of matches
    sorted_domains = sorted(found_domains.items(), key=lambda x: x[1], reverse=True)
    
    # Extract top domains (up to 5)
    top_domains = [domain for domain, _ in sorted_domains[:5]]
    
    # Extract skills by looking for technical terms
    skills = set()
    for domain, keywords in domain_keywords.items():
        for keyword in keywords:
            if keyword in description and len(keyword) > 3:  # Avoid short terms
                skills.add(keyword)
    
    # If we didn't find any domains, try extracting key nouns
    if not top_domains:
        words = description.split()
        # Get longer words that might be technical terms
        potential_terms = [word for word in words if len(word) > 5]
        top_domains = potential_terms[:3]  # Just use top 3 longest words as domains
    
    return {
        "required_expertise": top_domains,
        "key_skills": list(skills)[:7],
        "summary": "Project requires expertise in " + ", ".join(top_domains[:3] or ["technical fields"])
    }


def _fallback_parsing(query: str) -> Dict[str, Any]:
    q = (query or "").lower()

    keyword_map = {
        'artificial intelligence': ['ai', 'artificial intelligence', 'machine learning', 'neural networks', 'deep learning'],
        'ai': ['ai', 'artificial intelligence', 'machine learning', 'neural networks', 'deep learning'],
        'machine learning': ['machine learning', 'ml', 'artificial intelligence', 'data science', 'deep learning'],
        'data science': ['data science', 'statistics', 'analytics', 'big data'],
        'computer vision': ['computer vision', 'image processing', 'opencv', 'deep learning'],
        'natural language processing': ['nlp', 'natural language processing', 'text mining', 'language models'],
        'deep learning': ['deep learning', 'neural networks', 'tensorflow', 'pytorch'],
        'cybersecurity': ['cybersecurity', 'security', 'cryptography', 'network security'],
        'blockchain': ['blockchain', 'cryptocurrency', 'distributed systems'],
        'robotics': ['robotics', 'automation', 'control systems'],
        'database': ['database', 'sql', 'nosql', 'data management'],
        'web development': ['web development', 'javascript', 'react', 'node.js'],
        'mobile development': ['mobile development', 'android', 'ios', 'react native']
    }

    keywords = []
    domains = []
    experience_level = 'any'

    if any(x in q for x in ['expert', 'good at', 'skilled', 'experienced', 'professional']):
        experience_level = 'high'

    for key, values in keyword_map.items():
        if key in q:
            keywords.extend(values)
            domains.append(key)

    if not keywords:
        keywords = [w for w in q.split() if len(w) > 2]

    return {
        'keywords': sorted(list(set(keywords))),
        'domains': sorted(list(set(domains))),
        'intent': f"Looking for faculty with expertise in: {', '.join(domains) or query}",
        'searchType': 'expertise' if experience_level == 'high' else 'general',
        'filters': {
            'experience_level': experience_level,
            'specialization': domains[0] if domains else None
        }
    }


def parse_search_query_with_gemma(query: str) -> Dict[str, Any]:
    api_key = os.getenv("GEMMA_API_KEY")
    model = os.getenv("GEMMA_MODEL", "gemma-2-9b-it")
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    if not query or not api_key:
        if not api_key:
            logging.warning("GEMMA_API_KEY not set; using fallback parsing")
        return _fallback_parsing(query or "")

    prompt = f"""
You are a search assistant for a faculty research directory. Analyze the following search query and extract relevant information in JSON only with no extra text.

Query: "{query}"

Return strictly a JSON object with keys: keywords (array), domains (array), intent (string), searchType (one of expertise|general|specific), filters (object with keys experience_level in [high|medium|any], specialization string or null).

Examples mapping:
- artificial intelligence -> include related terms like ai, machine learning, deep learning, neural networks
- good at AI -> experience_level=high, domains include ai
- data science experts -> data science, statistics, analytics, experience_level=high
- computer vision researchers -> computer vision, image processing, ai
"""

    try:
        resp = requests.post(
            f"{api_url}?key={api_key}",
            headers={"Content-Type": "application/json"},
            json={
                "contents": [{
                    "parts": [{"text": prompt}]
                }]
            },
            timeout=20,
        )
        resp.raise_for_status()
        data = resp.json()

        # Try to pull text from candidates
        text = None
        try:
            text = data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            pass

        if not text:
            return _fallback_parsing(query)

        # Extract JSON blob
        m = re.search(r"\{[\s\S]*\}", text)
        if m:
            try:
                return json.loads(m.group(0))
            except Exception:
                pass

        # If already JSON encoded
        if isinstance(text, str):
            try:
                return json.loads(text)
            except Exception:
                pass

        return _fallback_parsing(query)
    except Exception as e:
        logging.warning(f"Gemma API call failed, using fallback: {e}")
        return _fallback_parsing(query)
