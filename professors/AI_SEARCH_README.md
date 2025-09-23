# 🤖 AI-Powered Faculty Research Directory

An intelligent faculty search system powered by Google's Gemini AI that understands natural language queries and finds relevant professors based on their expertise.

## 🚀 Features

### AI-Powered Natural Language Search
- **Smart Query Understanding**: Ask questions like "Show me professors good at artificial intelligence" or "Find experts in machine learning"
- **Keyword Extraction**: Automatically extracts relevant technical terms and research areas
- **Experience Level Detection**: Understands qualifiers like "expert", "good at", "skilled in"
- **Relevance Scoring**: Ranks results based on expertise match and research activity

### Enhanced Search Capabilities
- **Traditional Search**: Still supports exact keyword matching
- **Smart Filtering**: Filter by academic profiles (Google Scholar, Semantic Scholar)
- **Multiple View Modes**: Grid and list views
- **Profile Pictures**: Visual faculty identification
- **Academic Links**: Direct links to research profiles

## 🛠️ Setup Instructions

### 1. Get Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Copy the generated key

### 2. Configure Environment
1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
2. Edit `.env` and add your API key:
   ```
   REACT_APP_GEMINI_API_KEY=your-actual-api-key-here
   REACT_APP_ENABLE_AI_SEARCH=true
   ```

### 3. Install Dependencies
```bash
npm install
```

### 4. Start Development Server
```bash
npm start
```

## 🎯 How to Use AI Search

### Natural Language Queries
The AI search works best with descriptive queries:

**✅ Good Examples:**
- "Show me professors good at artificial intelligence"
- "Find experts in machine learning and data science"
- "Who are skilled in computer vision?"
- "Cybersecurity researchers with high experience"
- "Data science specialists"

**❌ Less Effective:**
- Single words: "AI", "ML"
- Very short phrases: "find prof"
- Non-descriptive: "show me"

### Query Understanding
The AI automatically:
- **Expands Keywords**: "AI" → "artificial intelligence, machine learning, neural networks"
- **Detects Experience Level**: "good at", "expert", "skilled" → prioritizes highly cited researchers
- **Maps Domains**: "computer vision" → "image processing, deep learning, opencv"
- **Scores Relevance**: Ranks by domain expertise, citations, and research activity

### Visual Indicators
- **🧠 Brain Icon**: Shows when AI is processing your query
- **✨ Sparkles Button**: Click to see AI's understanding of your query
- **Blue Info Box**: Displays extracted keywords and search intent

## 🎨 Search Interface Features

### Smart Search Bar
- **AI-Powered Placeholder**: Suggests natural language examples
- **Real-time Processing**: AI analyzes queries as you type
- **Suggestion Chips**: Click pre-made queries to see AI in action

### AI Search Helper
- **Query Intent**: Shows what the AI understood from your search
- **Extracted Keywords**: Displays technical terms identified
- **Search Strategy**: Explains how results are ranked

### Results Enhancement
- **Relevance Ranking**: AI-sorted results by expertise match
- **Experience Boosting**: Prioritizes researchers with high citations/h-index
- **Domain Matching**: Highlights exact specialty matches

## 🔧 Technical Details

### AI Service Architecture
```
User Query → Gemini AI → Keyword Extraction → Smart Filtering → Ranked Results
```

### Fallback System
- If AI service fails, falls back to traditional keyword search
- Maintains full functionality even without API key
- Graceful degradation of features

### Performance Optimization
- **Debounced Requests**: Prevents excessive API calls
- **Local Caching**: Stores AI results for repeated queries
- **Smart Triggering**: Only uses AI for natural language queries (10+ chars)

## 📊 Example Searches

### AI Research
```
"Show me experts in artificial intelligence"
→ Finds: ML researchers, AI specialists, neural network experts
→ Keywords: artificial intelligence, machine learning, deep learning, neural networks
```

### Data Science
```
"Find professors good at data science"
→ Finds: Statistics experts, big data researchers, analytics specialists  
→ Keywords: data science, statistics, analytics, big data, machine learning
```

### Computer Vision
```
"Computer vision researchers with high experience"
→ Finds: Image processing experts, CV researchers with high citations
→ Keywords: computer vision, image processing, deep learning, opencv
→ Boost: High citation count, h-index > 10
```

## 🚀 Advanced Features

### Experience Level Detection
- **"expert", "good at", "skilled"** → Boosts researchers with:
  - Google Scholar/Semantic Scholar profiles
  - High citation count (>100)
  - Strong h-index (>10)

### Domain Expansion
- **"AI"** → artificial intelligence, machine learning, neural networks, deep learning
- **"cybersecurity"** → security, cryptography, network security, information security
- **"web dev"** → web development, javascript, react, node.js, frontend, backend

### Smart Filtering
- Combines traditional filters with AI understanding
- Maintains all existing functionality
- Enhanced with intelligent query processing

## 🔍 Troubleshooting

### AI Search Not Working
1. Check if API key is correctly set in `.env`
2. Verify internet connection
3. Check browser console for errors
4. Fallback search should still work

### No Results Found
1. Try broader terms: "machine learning" instead of "ML transformers"
2. Use descriptive phrases: "experts in data science" vs "data"
3. Check spelling and try alternative phrasings

### Slow Response
1. AI processing takes 1-3 seconds for complex queries
2. Simple searches use traditional fast search
3. Results are cached for repeated queries

## 🎯 Best Practices

### Writing Effective Queries
1. **Be Descriptive**: "professors specialized in computer vision" vs "CV"
2. **Include Context**: "machine learning experts with industry experience"
3. **Use Natural Language**: Write as you would ask a colleague
4. **Specify Experience**: "senior researchers in AI" vs "AI people"

### Getting Better Results
1. **Combine Terms**: "data science and machine learning experts"
2. **Add Qualifiers**: "experienced cybersecurity researchers"
3. **Be Specific**: "natural language processing specialists" vs "NLP"
4. **Use Examples**: Try the suggested search chips for ideas

## 🌟 Future Enhancements

- **Multi-language Support**: Search in different languages
- **Research Paper Integration**: Include recent publications in ranking
- **Collaboration Suggestions**: Find researchers who work well together
- **Trend Analysis**: Identify emerging research areas
- **Personalized Recommendations**: Learn from search patterns

---

**Powered by Google Gemini AI** 🧠  
**Built with React & Modern Web Technologies** ⚛️