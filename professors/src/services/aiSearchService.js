// AI-powered search service using Gemini API for faculty search and project analysis
class AISearchService {
  constructor() {
    this.BACKEND_URL = process.env.REACT_APP_API_BASE || 'http://localhost:5000';
  }

  // Extract search intent and keywords from natural language query
  async parseSearchQuery(query) {
    // eslint-disable-next-line no-unused-vars
    const prompt = `
You are a search assistant for a faculty research directory. Analyze the following search query and extract relevant information:

Query: "${query}"

Please respond with a JSON object containing:
{
  "keywords": ["keyword1", "keyword2", ...],
  "domains": ["domain1", "domain2", ...],
  "intent": "description of what user is looking for",
  "searchType": "expertise" | "general" | "specific",
  "filters": {
    "experience_level": "high" | "medium" | "any",
    "specialization": "specific area if mentioned"
  }
}

Focus on extracting:
- Technical keywords and research areas
- Academic domains (AI, Machine Learning, Computer Science, etc.)
- Experience level indicators (expert, good at, skilled, experienced)
- Specific technologies or methodologies

Examples:
- "artificial intelligence" → AI, machine learning, neural networks, deep learning
- "good at AI" → high experience level in AI
- "data science experts" → data science, statistics, analytics, high experience
- "computer vision researchers" → computer vision, image processing, AI
`;

    try {
      const response = await fetch(`${this.BACKEND_URL}/api/ai/parse-search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
      });
      if (!response.ok) throw new Error(`Backend AI parse failed: ${response.status}`);
      const data = await response.json();
      if (data && data.success && data.result) return data.result;
      return this.fallbackParsing(query);
    } catch (error) {
      console.warn('AI search parsing failed, using fallback:', error);
      return this.fallbackParsing(query);
    }
  }

  // Fallback parsing for when AI service is unavailable
  fallbackParsing(query) {
    const lowercaseQuery = query.toLowerCase();
    
    // Common AI/CS keywords mapping
    const keywordMap = {
      'artificial intelligence': ['ai', 'artificial intelligence', 'machine learning', 'neural networks'],
      'ai': ['ai', 'artificial intelligence', 'machine learning', 'neural networks'],
      'machine learning': ['machine learning', 'ml', 'artificial intelligence', 'data science'],
      'data science': ['data science', 'statistics', 'analytics', 'big data'],
      'computer vision': ['computer vision', 'image processing', 'opencv', 'deep learning'],
      'natural language processing': ['nlp', 'natural language processing', 'text mining', 'linguistics'],
      'deep learning': ['deep learning', 'neural networks', 'tensorflow', 'pytorch'],
      'cybersecurity': ['cybersecurity', 'security', 'cryptography', 'network security'],
      'blockchain': ['blockchain', 'cryptocurrency', 'distributed systems'],
      'robotics': ['robotics', 'automation', 'control systems'],
      'database': ['database', 'sql', 'nosql', 'data management'],
      'web development': ['web development', 'javascript', 'react', 'node.js'],
      'mobile development': ['mobile development', 'android', 'ios', 'react native']
    };

    let keywords = [];
    let domains = [];
    let experienceLevel = 'any';

    // Check for experience level indicators
    if (lowercaseQuery.includes('expert') || lowercaseQuery.includes('good at') || 
        lowercaseQuery.includes('skilled') || lowercaseQuery.includes('experienced')) {
      experienceLevel = 'high';
    }

    // Extract keywords and domains
    Object.entries(keywordMap).forEach(([key, values]) => {
      if (lowercaseQuery.includes(key)) {
        keywords.push(...values);
        domains.push(key);
      }
    });

    // Add query words as keywords if no matches found
    if (keywords.length === 0) {
      keywords = query.toLowerCase().split(' ').filter(word => word.length > 2);
    }

    return {
      keywords: [...new Set(keywords)], // Remove duplicates
      domains: [...new Set(domains)],
      intent: `Looking for faculty with expertise in: ${domains.join(', ') || query}`,
      searchType: experienceLevel === 'high' ? 'expertise' : 'general',
      filters: {
        experience_level: experienceLevel,
        specialization: domains[0] || null
      }
    };
  }

  // Smart search function that filters teachers based on AI-parsed query
  smartSearch(teachers, searchQuery, aiParsedQuery) {
    if (!aiParsedQuery || !aiParsedQuery.keywords) {
      return teachers.filter(teacher => 
        teacher.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        teacher.domain_expertise?.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    const { keywords, filters } = aiParsedQuery;
    
    return teachers.filter(teacher => {
      let score = 0;
      const teacherText = `
        ${teacher.name || ''} 
        ${teacher.domain_expertise || ''} 
        ${teacher.phd_thesis || ''} 
        ${teacher.research_interests || ''} 
        ${teacher.bio || ''}
      `.toLowerCase();

      // Score based on keyword matches
      keywords.forEach(keyword => {
        const keywordLower = keyword.toLowerCase();
        if (teacherText.includes(keywordLower)) {
          score += 1;
          
          // Higher score for domain expertise matches
          if (teacher.domain_expertise?.toLowerCase().includes(keywordLower)) {
            score += 2;
          }
          
          // Higher score for research interests matches
          if (teacher.research_interests?.toLowerCase().includes(keywordLower)) {
            score += 1.5;
          }
        }
      });

      // Boost score for teachers with academic profiles (indicates active research)
      if (filters.experience_level === 'high') {
        if (teacher.has_google_scholar || teacher.has_semantic_scholar) {
          score += 1;
        }
        if (teacher.total_citations && teacher.total_citations > 100) {
          score += 1;
        }
        if (teacher.h_index && teacher.h_index > 10) {
          score += 1;
        }
      }

      // Return teachers with score > 0 (at least one keyword match)
      return score > 0;
    }).sort((a, b) => {
      // Sort by relevance score (recalculate for sorting)
      const scoreA = this.calculateRelevanceScore(a, keywords, filters);
      const scoreB = this.calculateRelevanceScore(b, keywords, filters);
      return scoreB - scoreA;
    });
  }

  // Calculate relevance score for sorting
  calculateRelevanceScore(teacher, keywords, filters) {
    let score = 0;
    const teacherText = `
      ${teacher.name || ''} 
      ${teacher.domain_expertise || ''} 
      ${teacher.phd_thesis || ''} 
      ${teacher.research_interests || ''} 
      ${teacher.bio || ''}
    `.toLowerCase();

    keywords.forEach(keyword => {
      const keywordLower = keyword.toLowerCase();
      if (teacherText.includes(keywordLower)) {
        score += 1;
        if (teacher.domain_expertise?.toLowerCase().includes(keywordLower)) {
          score += 2;
        }
        if (teacher.research_interests?.toLowerCase().includes(keywordLower)) {
          score += 1.5;
        }
      }
    });

    // Experience level boost
    if (filters.experience_level === 'high') {
      if (teacher.has_google_scholar || teacher.has_semantic_scholar) score += 1;
      if (teacher.total_citations && teacher.total_citations > 100) score += 1;
      if (teacher.h_index && teacher.h_index > 10) score += 1;
    }

    return score;
  }
  
  // Analyze project description and find matching professors
  async analyzeProject(projectDescription) {
    try {
      const response = await fetch(`${this.BACKEND_URL}/api/project/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ description: projectDescription })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `Server responded with ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Project analysis failed:', error);
      throw error;
    }
  }
}

const aiSearchServiceInstance = new AISearchService();
export default aiSearchServiceInstance;