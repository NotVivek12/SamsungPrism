from typing import List, Dict, Optional
import sqlite3
from collections import Counter

class DomainExpertiseAnalyzer:
    def __init__(self, db_path: str = "professors.db"):
        self.db_path = db_path
        
    def _get_connection(self) -> sqlite3.Connection:
        """Create a database connection"""
        return sqlite3.connect(self.db_path)

    def calculate_expertise_score(self, citations: int, h_index: int) -> float:
        """Calculate expertise score based on citations and h-index"""
        if not citations and not h_index:
            return 0.0
            
        # Normalize citation count (assuming max realistic citations is 100000)
        citation_score = min(citations, 100000) / 100000 * 0.6
        
        # Normalize h-index (assuming max realistic h-index is 100)
        h_index_score = min(h_index, 100) / 100 * 0.4
        
        return round(citation_score + h_index_score, 2)

    def get_expertise_level(self, score: float) -> str:
        """Convert score to expertise level"""
        if score >= 0.8:
            return "Expert"
        elif score >= 0.6:
            return "Advanced"
        elif score >= 0.3:
            return "Intermediate"
        else:
            return "Basic"

    def search_domain_experts(self, domain: str, min_expertise_level: str = "Advanced") -> List[Dict]:
        """
        Search for professors with high expertise in a specific domain
        
        Args:
            domain: The domain/field to search for
            min_expertise_level: Minimum expertise level (Expert, Advanced, Intermediate, Basic)
            
        Returns:
            List of professors with their expertise details
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Search with case-insensitive domain matching in research interests and publications
        query = """
        SELECT DISTINCT 
            p.id,
            p.name,
            p.email,
            p.research_interests,
            p.citations,
            p.h_index,
            p.google_scholar_url
        FROM professors p
        WHERE 
            LOWER(p.research_interests) LIKE LOWER(?) OR
            EXISTS (
                SELECT 1 
                FROM publications pub 
                WHERE pub.professor_id = p.id 
                AND LOWER(pub.title) LIKE LOWER(?)
            )
        """
        
        search_term = f"%{domain}%"
        cursor.execute(query, (search_term, search_term))
        professors = cursor.fetchall()
        
        # Calculate expertise scores and filter by minimum level
        expertise_levels = {
            "Expert": 0.8,
            "Advanced": 0.6,
            "Intermediate": 0.3,
            "Basic": 0.0
        }
        min_score = expertise_levels.get(min_expertise_level, 0.0)
        
        results = []
        for prof in professors:
            score = self.calculate_expertise_score(prof[4] or 0, prof[5] or 0)
            level = self.get_expertise_level(score)
            
            if score >= min_score:
                results.append({
                    "id": prof[0],
                    "name": prof[1],
                    "email": prof[2],
                    "research_interests": prof[3],
                    "citations": prof[4],
                    "h_index": prof[5],
                    "google_scholar_url": prof[6],
                    "expertise_score": score,
                    "expertise_level": level
                })
        
        # Sort by expertise score in descending order
        results.sort(key=lambda x: x["expertise_score"], reverse=True)
        conn.close()
        return results

    def get_domain_statistics(self, domain: str) -> Dict:
        """
        Get statistics about expertise levels in a specific domain
        
        Args:
            domain: The domain/field to analyze
            
        Returns:
            Dictionary with expertise level distribution and other statistics
        """
        experts = self.search_domain_experts(domain, "Basic")  # Get all levels
        if not experts:
            return {
                "total_experts": 0,
                "expertise_distribution": {},
                "average_citations": 0,
                "average_h_index": 0
            }
            
        expertise_counts = Counter(expert["expertise_level"] for expert in experts)
        total_citations = sum(expert["citations"] or 0 for expert in experts)
        total_h_index = sum(expert["h_index"] or 0 for expert in experts)
        
        return {
            "total_experts": len(experts),
            "expertise_distribution": dict(expertise_counts),
            "average_citations": round(total_citations / len(experts), 2),
            "average_h_index": round(total_h_index / len(experts), 2)
        }
