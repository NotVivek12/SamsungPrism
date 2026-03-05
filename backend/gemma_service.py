import os
import re
import json
import logging
from typing import Dict, Any, List

import requests

# Ollama configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b")

# Google Gemini configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"


def _is_ollama_available() -> bool:
    """Check if the local Ollama server is reachable."""
    try:
        resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=3)
        return resp.status_code == 200
    except Exception:
        return False


def _call_ollama(prompt: str) -> str | None:
    """Send a prompt to Ollama and return the response text, or None on failure."""
    try:
        resp = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            headers={"Content-Type": "application/json"},
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.7, "top_p": 0.9},
            },
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json().get("response", "")
    except Exception as e:
        logging.warning(f"Ollama API call failed: {e}")
        return None


def _call_gemini(prompt: str) -> str | None:
    """Send a prompt to Google Gemini API and return the response text, or None on failure."""
    if not GOOGLE_API_KEY:
        logging.warning("GOOGLE_API_KEY not set; skipping Gemini fallback")
        return None
    try:
        resp = requests.post(
            f"{GEMINI_API_URL}?key={GOOGLE_API_KEY}",
            headers={"Content-Type": "application/json"},
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.7,
                    "topP": 0.9,
                    "maxOutputTokens": 1024,
                },
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        # Extract text from Gemini response structure
        candidates = data.get("candidates", [])
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
            if parts:
                return parts[0].get("text", "")
        return None
    except Exception as e:
        logging.warning(f"Gemini API call failed: {e}")
        return None


def _call_llm(prompt: str) -> str | None:
    """Try Ollama first, then Gemini, return the LLM response text or None."""
    if _is_ollama_available():
        text = _call_ollama(prompt)
        if text:
            return text

    # Fallback to Gemini
    text = _call_gemini(prompt)
    if text:
        return text

    return None


def _extract_json(text: str) -> dict | None:
    """Try to parse a JSON object out of an LLM response string."""
    if not text:
        return None
    # Look for a JSON block (possibly wrapped in ```json ... ```)
    cleaned = re.sub(r"```json\s*", "", text)
    cleaned = re.sub(r"```\s*$", "", cleaned)
    m = re.search(r"\{[\s\S]*\}", cleaned)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            pass
    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def analyze_project_description(description: str) -> Dict[str, Any]:
    """
    Analyze a project description and extract required expertise domains.
    Falls back through: Ollama -> Gemini -> keyword matching.
    """
    if not description:
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

    text = _call_llm(prompt)
    result = _extract_json(text)
    if result and "required_expertise" in result:
        return result

    return _fallback_project_analysis(description)


def parse_search_query_with_gemma(query: str) -> Dict[str, Any]:
    """
    Parse a natural-language search query into structured search parameters.
    Falls back through: Ollama -> Gemini -> keyword matching.
    """
    if not query:
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

    text = _call_llm(prompt)
    result = _extract_json(text)
    if result and "keywords" in result:
        return result

    return _fallback_parsing(query)


# ---------------------------------------------------------------------------
# Fallback helpers (keyword matching, no LLM needed)
# ---------------------------------------------------------------------------

def _fallback_project_analysis(description: str) -> Dict[str, Any]:
    """
    Fallback method for project description analysis when no LLM is available.
    Uses keyword matching to extract likely expertise areas from the description.
    """
    description = (description or "").lower()

    domain_keywords = {
        "artificial intelligence": ["artificial intelligence", "machine learning", "neural network", "deep learning"],
        "machine learning": ["machine learning", "classification", "regression", "clustering", "supervised", "unsupervised"],
        "data science": ["data science", "big data", "data analysis", "analytics", "data mining", "statistics"],
        "computer vision": ["computer vision", "image processing", "object detection", "facial recognition"],
        "natural language processing": ["natural language", "text analysis", "sentiment analysis", "language model", "transformer"],
        "robotics": ["robotics", "automation", "autonomous", "control system"],
        "cybersecurity": ["cybersecurity", "encryption", "cryptography", "network security", "vulnerability"],
        "web development": ["frontend", "backend", "full-stack", "javascript", "react"],
        "mobile development": ["mobile development", "android", "app development", "flutter"],
        "blockchain": ["blockchain", "distributed ledger", "smart contract"],
        "internet of things": ["internet of things", "embedded system", "sensor network", "arduino", "smart city", "monitoring system", "real-time monitoring"],
        "IoT": ["iot", "sensor", "smart home", "smart grid", "edge computing", "wearable"],
        "embedded systems": ["embedded", "microcontroller", "firmware", "fpga", "rtos"],
        "signal processing": ["signal processing", "digital signal", "filtering", "frequency", "spectrum"],
        "renewable energy": ["solar", "renewable energy", "photovoltaic", "wind energy", "power output", "inverter", "energy utilization", "panel", "energy harvesting"],
        "power systems": ["voltage", "current", "power", "electrical", "power system", "fault detection", "power grid", "smart grid"],
        "VLSI": ["vlsi", "semiconductor", "circuit design", "ic design"],
        "wireless communication": ["wireless", "5g", "communication", "antenna", "mimo", "ofdm"],
        "database systems": ["database", "sql", "nosql", "data storage", "data management"],
        "cloud computing": ["cloud", "distributed system", "serverless", "microservice"],
        "augmented reality": ["augmented reality", "virtual reality", "mixed reality"],
        "quantum computing": ["quantum", "qubit", "quantum algorithm"],
        "bioinformatics": ["bioinformatics", "genomics", "biological data"],
        "high performance computing": ["high performance computing", "parallel computing", "gpu computing"],
    }

    found_domains = {}
    # Use word-boundary matching to avoid partial matches like 'ar' in 'solar'
    for domain, keywords in domain_keywords.items():
        matches = 0
        for keyword in keywords:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, description):
                matches += 1
        if matches > 0:
            found_domains[domain] = matches

    sorted_domains = sorted(found_domains.items(), key=lambda x: x[1], reverse=True)
    top_domains = [domain for domain, _ in sorted_domains[:5]]

    skills = set()
    for domain, keywords in domain_keywords.items():
        for keyword in keywords:
            if keyword in description and len(keyword) > 3:
                skills.add(keyword)

    if not top_domains:
        words = description.split()
        potential_terms = [word for word in words if len(word) > 5]
        top_domains = potential_terms[:3]

    return {
        "required_expertise": top_domains,
        "key_skills": list(skills)[:7],
        "summary": "Project requires expertise in " + ", ".join(top_domains[:3] or ["technical fields"]),
    }


def _fallback_parsing(query: str) -> Dict[str, Any]:
    q = (query or "").lower()

    keyword_map = {
        "artificial intelligence": ["ai", "artificial intelligence", "machine learning", "neural networks", "deep learning"],
        "ai": ["ai", "artificial intelligence", "machine learning", "neural networks", "deep learning"],
        "machine learning": ["machine learning", "ml", "artificial intelligence", "data science", "deep learning"],
        "data science": ["data science", "statistics", "analytics", "big data"],
        "computer vision": ["computer vision", "image processing", "opencv", "deep learning"],
        "natural language processing": ["nlp", "natural language processing", "text mining", "language models"],
        "deep learning": ["deep learning", "neural networks", "tensorflow", "pytorch"],
        "cybersecurity": ["cybersecurity", "security", "cryptography", "network security"],
        "blockchain": ["blockchain", "cryptocurrency", "distributed systems"],
        "robotics": ["robotics", "automation", "control systems"],
        "database": ["database", "sql", "nosql", "data management"],
        "web development": ["web development", "javascript", "react", "node.js"],
        "mobile development": ["mobile development", "android", "ios", "react native"],
    }

    keywords = []
    domains = []
    experience_level = "any"

    if any(x in q for x in ["expert", "good at", "skilled", "experienced", "professional"]):
        experience_level = "high"

    for key, values in keyword_map.items():
        if key in q:
            keywords.extend(values)
            domains.append(key)

    if not keywords:
        keywords = [w for w in q.split() if len(w) > 2]

    return {
        "keywords": sorted(list(set(keywords))),
        "domains": sorted(list(set(domains))),
        "intent": f"Looking for faculty with expertise in: {', '.join(domains) or query}",
        "searchType": "expertise" if experience_level == "high" else "general",
        "filters": {
            "experience_level": experience_level,
            "specialization": domains[0] if domains else None,
        },
    }
