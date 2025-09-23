import pytest
from domain_expertise_analyzer import DomainExpertiseAnalyzer
import sqlite3
import os

@pytest.fixture
def test_db():
    """Create a test database with sample data"""
    db_path = "test_professors.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS professors (
            id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            research_interests TEXT,
            citations INTEGER,
            h_index INTEGER,
            google_scholar_url TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS publications (
            id INTEGER PRIMARY KEY,
            professor_id INTEGER,
            title TEXT,
            FOREIGN KEY (professor_id) REFERENCES professors (id)
        )
    """)
    
    # Insert sample data
    cursor.execute("""
        INSERT INTO professors (name, email, research_interests, citations, h_index)
        VALUES 
            ('Dr. Smith', 'smith@example.com', 'Artificial Intelligence, Machine Learning', 5000, 30),
            ('Dr. Jones', 'jones@example.com', 'Natural Language Processing, Deep Learning', 10000, 45),
            ('Dr. Wilson', 'wilson@example.com', 'Computer Vision, Pattern Recognition', 2000, 20)
    """)
    
    cursor.execute("""
        INSERT INTO publications (professor_id, title)
        VALUES 
            (1, 'Advanced Machine Learning Techniques'),
            (1, 'AI in Healthcare'),
            (2, 'Deep Learning for NLP'),
            (3, 'Computer Vision Applications')
    """)
    
    conn.commit()
    conn.close()
    
    yield db_path
    
    # Cleanup
    os.remove(db_path)

def test_calculate_expertise_score():
    analyzer = DomainExpertiseAnalyzer()
    
    # Test cases
    assert analyzer.calculate_expertise_score(50000, 50) == 0.5  # Mid-level
    assert analyzer.calculate_expertise_score(100000, 100) == 1.0  # Max score
    assert analyzer.calculate_expertise_score(0, 0) == 0.0  # Min score
    assert analyzer.calculate_expertise_score(25000, 25) == 0.25  # Quarter score

def test_get_expertise_level():
    analyzer = DomainExpertiseAnalyzer()
    
    assert analyzer.get_expertise_level(0.9) == "Expert"
    assert analyzer.get_expertise_level(0.7) == "Advanced"
    assert analyzer.get_expertise_level(0.4) == "Intermediate"
    assert analyzer.get_expertise_level(0.2) == "Basic"

def test_search_domain_experts(test_db):
    analyzer = DomainExpertiseAnalyzer(test_db)
    
    # Test searching for AI experts
    ai_experts = analyzer.search_domain_experts("Artificial Intelligence")
    assert len(ai_experts) > 0
    assert any(expert["name"] == "Dr. Smith" for expert in ai_experts)
    
    # Test searching for NLP experts
    nlp_experts = analyzer.search_domain_experts("Natural Language Processing")
    assert len(nlp_experts) > 0
    assert any(expert["name"] == "Dr. Jones" for expert in nlp_experts)
    
    # Test minimum expertise level filtering
    advanced_experts = analyzer.search_domain_experts("Machine Learning", "Expert")
    basic_experts = analyzer.search_domain_experts("Machine Learning", "Basic")
    assert len(advanced_experts) <= len(basic_experts)

def test_get_domain_statistics(test_db):
    analyzer = DomainExpertiseAnalyzer(test_db)
    
    # Test statistics for AI domain
    ai_stats = analyzer.get_domain_statistics("Artificial Intelligence")
    assert ai_stats["total_experts"] > 0
    assert "expertise_distribution" in ai_stats
    assert "average_citations" in ai_stats
    assert "average_h_index" in ai_stats
    
    # Test statistics for non-existent domain
    empty_stats = analyzer.get_domain_statistics("Non Existent Domain")
    assert empty_stats["total_experts"] == 0
    assert empty_stats["expertise_distribution"] == {}