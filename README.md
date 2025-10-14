<div align="center">

# 🎓 PRISM - Professor Research Intelligence & Search Mechanism

**An intelligent faculty discovery platform powered by AI, designed to bridge the gap between research projects and academic expertise.**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/react-18.2.0-blue.svg)](https://reactjs.org/)
[![MySQL](https://img.shields.io/badge/mysql-8.0+-blue.svg)](https://www.mysql.com/)

[Features](#-key-features) • [Architecture](#-architecture) • [Installation](#-installation) • [Usage](#-usage) • [API Documentation](#-api-documentation) • [Contributing](#-contributing)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Technology Stack](#-technology-stack)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Data Extraction Pipeline](#-data-extraction-pipeline)
- [Project Structure](#-project-structure)
- [Contributing](#-contributing)
- [Troubleshooting](#-troubleshooting)
- [License](#-license)

---

## 🌟 Overview

**PRISM** (Professor Research Intelligence & Search Mechanism) is a sophisticated full-stack application that revolutionizes how researchers, students, and organizations discover and connect with academic experts. By leveraging advanced AI-powered search, natural language processing, and intelligent project-matching algorithms, PRISM makes finding the right academic collaborator as simple as describing your project.

### The Problem
In today's research landscape, finding professors with specific expertise for collaboration, guidance, or consultation is challenging. Traditional directory searches are limited to basic filters and keyword matching, making it difficult to:
- Identify experts based on nuanced project requirements
- Match complex research needs with appropriate academic expertise
- Discover faculty across diverse research domains efficiently
- Access comprehensive academic profiles in one unified platform

### The Solution
PRISM solves these challenges by:
- **AI-Powered Analysis**: Natural language understanding of project descriptions to extract expertise requirements
- **Intelligent Matching**: Sophisticated algorithms that match projects with professors based on research domains, publications, and expertise
- **Unified Academic Profiles**: Aggregated data from Google Scholar, Semantic Scholar, and institutional profiles
- **Real-time Insights**: Live citation metrics, research interests, and domain expertise visualization
- **Semantic Search**: Context-aware search that understands intent, not just keywords

---

## ✨ Key Features

### 🔍 **Intelligent Search & Discovery**
- **Natural Language Search**: Ask questions like "Who is an expert in machine learning for healthcare?"
- **AI Query Parsing**: Automatic extraction of domains, keywords, and intent from conversational queries
- **Multi-dimensional Filtering**: Search by college, expertise domain, publication metrics, and more
- **Semantic Understanding**: Context-aware search that goes beyond simple keyword matching

### 🚀 **Project-Based Faculty Matching**
- **Project Description Analysis**: Submit a project description and get matched with relevant professors
- **Expertise Scoring**: Percentage-based match scores showing how well a professor's expertise aligns with your project
- **Domain Highlighting**: Visual indicators showing which specific expertise areas match your requirements
- **Comprehensive Faculty Profiles**: View publications, citations, academic links, and research interests in one place

### 📊 **Rich Academic Profiles**
- **Multi-Source Data Integration**: Combines data from Google Scholar, Semantic Scholar, and institutional databases
- **Citation Metrics**: H-index, total citations, and publication counts
- **Research Interests**: Automatically extracted and categorized research domains
- **Academic Network Links**: Direct access to Google Scholar, Semantic Scholar, and institutional profiles

### 🤖 **AI-Powered Insights**
- **Gemma AI Integration**: Optional integration with local LLM for advanced analysis
- **Fallback Mechanisms**: Intelligent keyword-based analysis when AI services are unavailable
- **Continuous Learning**: Background extraction of citations and research interests
- **Domain Expertise Analyzer**: Automated categorization of research areas

### 🎨 **Modern User Experience**
- **Responsive Design**: Beautiful, mobile-friendly interface built with React and Tailwind CSS
- **Dark Mode Support**: Eye-friendly dark theme for extended browsing sessions
- **Interactive Visualizations**: Dynamic charts and graphs for citation metrics
- **Real-time Updates**: Live search results and instant feedback

---

## 🏗️ Architecture

PRISM follows a modern three-tier architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                     PRESENTATION LAYER                       │
│                                                               │
│  React 18 + TypeScript + Tailwind CSS + React Router        │
│  - AI-Powered Search Interface                               │
│  - Project Matcher Component                                 │
│  - Professor Profile Cards                                   │
│  - Responsive Dashboard                                      │
└───────────────────────────┬─────────────────────────────────┘
                            │ REST API (HTTP/JSON)
┌───────────────────────────▼─────────────────────────────────┐
│                     APPLICATION LAYER                        │
│                                                               │
│  Flask 3.0 + Python 3.8+                                     │
│  - Professor Routes & Endpoints                              │
│  - AI Search Service (Gemma/Ollama)                          │
│  - Domain Expertise Analyzer                                 │
│  - Google Scholar Extractor                                  │
│  - Semantic Scholar Extractor                                │
│  - Background Citation Processor                             │
└───────────────────────────┬─────────────────────────────────┘
                            │ SQL Queries
┌───────────────────────────▼─────────────────────────────────┐
│                       DATA LAYER                             │
│                                                               │
│  MySQL 8.0+ Database                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  professors  │  │   domains    │  │     plink    │      │
│  │   (master)   │  │  (taxonomy)  │  │  (profiles)  │      │
│  └──────┬───────┘  └──────┬───────┘  └──────────────┘      │
│         │                  │                                 │
│         └────────┬─────────┘                                 │
│                  │                                           │
│         ┌────────▼──────────┐                                │
│         │   prof_domain     │                                │
│         │  (linking table)  │                                │
│         └───────────────────┘                                │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **User Input** → React Frontend captures search query or project description
2. **API Request** → Frontend sends request to Flask backend endpoints
3. **AI Processing** → Gemma/Ollama analyzes natural language to extract intent and domains
4. **Database Query** → SQL queries with JOIN operations aggregate professor data
5. **Matching Algorithm** → Scoring engine calculates relevance based on expertise overlap
6. **Response** → Ranked results with match percentages sent back to frontend
7. **Rendering** → React components display interactive, filterable results

---

## 🛠️ Technology Stack

### Backend
- **Framework**: Flask 3.0.3 with Flask-CORS for cross-origin support
- **Database**: MySQL 8.0+ with mysql-connector-python
- **ORM**: SQLAlchemy 2.0.23 for advanced queries
- **AI/ML**: 
  - Ollama (Gemma 3 4B model) for natural language understanding
  - spaCy 3.8.2 for NLP tasks
  - Transformers 4.45.2 for advanced text processing
- **Web Scraping**: BeautifulSoup4 + lxml for scholar data extraction
- **Data Processing**: Pandas 2.2.2 for data manipulation
- **Environment**: python-dotenv for configuration management

### Frontend
- **Framework**: React 18.2.0 with TypeScript
- **Routing**: React Router 6.15.0
- **Styling**: Tailwind CSS 3.3.0 with custom theme
- **Icons**: Lucide React for beautiful, consistent icons
- **Build Tool**: React Scripts 5.0.1 with custom webpack configuration

### DevOps & Tools
- **API Testing**: Pytest with coverage reporting
- **Server**: Gunicorn for production deployment
- **Code Quality**: ESLint, Prettier for consistent formatting
- **Version Control**: Git with conventional commits

---

## 📦 Installation

### Prerequisites

Before installing PRISM, ensure you have:

- **Node.js** 16+ and npm/yarn ([Download](https://nodejs.org/))
- **Python** 3.8+ ([Download](https://www.python.org/downloads/))
- **MySQL** 8.0+ ([Download](https://dev.mysql.com/downloads/mysql/))
- **Git** ([Download](https://git-scm.com/downloads))
- **(Optional)** Ollama for AI features ([Download](https://ollama.com/))

### Step 1: Clone the Repository

```bash
git clone https://github.com/NotVivek12/SamsungPrism.git
cd SamsungPrism
```

### Step 2: Database Setup

1. **Create the MySQL database:**

```sql
CREATE DATABASE prism_professors CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE prism_professors;
```

2. **Create tables:**

```sql
-- Professors table
CREATE TABLE professors (
    PID INT PRIMARY KEY AUTO_INCREMENT,
    PName VARCHAR(255) NOT NULL,
    CName VARCHAR(255),
    CMailId VARCHAR(255),
    Phd TEXT,
    INDEX idx_name (PName),
    INDEX idx_college (CName)
);

-- Domains taxonomy
CREATE TABLE domains (
    DomainID INT PRIMARY KEY AUTO_INCREMENT,
    DomainName VARCHAR(255) UNIQUE NOT NULL,
    INDEX idx_domain_name (DomainName)
);

-- Professor-Domain linking table
CREATE TABLE prof_domain (
    ProfID INT,
    DomainId INT,
    PRIMARY KEY (ProfID, DomainId),
    FOREIGN KEY (ProfID) REFERENCES professors(PID) ON DELETE CASCADE,
    FOREIGN KEY (DomainId) REFERENCES domains(DomainID) ON DELETE CASCADE
);

-- Academic profile links
CREATE TABLE plink (
    ProfID INT PRIMARY KEY,
    GScholar TEXT,
    SScholar TEXT,
    CProfile TEXT,
    FOREIGN KEY (ProfID) REFERENCES professors(PID) ON DELETE CASCADE
);
```

3. **Import initial data** (if you have an Excel file):

```bash
cd prismZip
python migrate_excel_to_db.py
```

### Step 3: Backend Setup

1. **Navigate to backend directory:**

```bash
cd prismZip
```

2. **Create virtual environment:**

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Install Python dependencies:**

```bash
pip install -r requirements.txt
```

4. **Download spaCy language model:**

```bash
python -m spacy download en_core_web_sm
```

5. **Create `.env` file:**

```bash
# Copy from template
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Database Configuration
DB_HOST=localhost
DB_NAME=prism_professors
DB_USER=root
DB_PASSWORD=your_secure_password
DB_PORT=3306

# API Configuration
PORT=5000
REQUEST_DELAY=5

# Ollama Configuration (Optional)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gemma3:4b
```

### Step 4: Frontend Setup

1. **Navigate to frontend directory:**

```bash
cd ../professors
```

2. **Install Node dependencies:**

```bash
npm install
```

3. **Configure API endpoint:**

Create `.env` file in the `professors` directory:

```env
REACT_APP_API_BASE=http://localhost:5000
```

### Step 5: (Optional) Ollama Setup for AI Features

1. **Install Ollama** from [ollama.com](https://ollama.com/)

2. **Pull Gemma model:**

```bash
ollama pull gemma3:4b
```

3. **Verify Ollama is running:**

```bash
ollama list
```

---

## ⚙️ Configuration

### Backend Configuration (`prismZip/.env`)

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DB_HOST` | MySQL database host | `localhost` | Yes |
| `DB_NAME` | Database name | `prism_professors` | Yes |
| `DB_USER` | Database username | `root` | Yes |
| `DB_PASSWORD` | Database password | - | Yes |
| `DB_PORT` | Database port | `3306` | No |
| `PORT` | Flask server port | `5000` | No |
| `REQUEST_DELAY` | Delay between Scholar requests (seconds) | `5` | No |
| `OLLAMA_BASE_URL` | Ollama API endpoint | `http://localhost:11434` | No |
| `OLLAMA_MODEL` | LLM model name | `gemma3:4b` | No |

### Frontend Configuration (`professors/.env`)

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `REACT_APP_API_BASE` | Backend API URL | `http://localhost:5000` | Yes |

### CORS Configuration

For production deployment, update CORS settings in `app.py`:

```python
from flask_cors import CORS

# Development (allow all origins)
CORS(app)

# Production (restrict origins)
CORS(app, origins=["https://your-frontend-domain.com"])
```

---

## 🚀 Usage

### Running the Application

#### Development Mode

**Terminal 1 - Start Backend:**

```bash
cd prismZip
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux
python app.py
```

Backend will start on `http://localhost:5000`

**Terminal 2 - Start Frontend:**

```bash
cd professors
npm start
```

Frontend will start on `http://localhost:3000`

#### Production Mode

**Backend (using Gunicorn):**

```bash
cd prismZip
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

**Frontend (build and serve):**

```bash
cd professors
npm run build
# Serve the build folder using nginx or any static server
```

### Using the Application

#### 1. **AI-Powered Search**

Navigate to the search page and try queries like:
- "Find experts in machine learning"
- "Who specializes in cybersecurity and blockchain?"
- "Professors experienced in natural language processing"

The AI will:
- Parse your natural language query
- Extract relevant domains and keywords
- Rank professors by expertise match
- Display comprehensive profiles

#### 2. **Project-Based Matching**

1. Go to "Project Matcher" page
2. Describe your project in detail:
   ```
   I'm developing a machine learning application for early detection 
   of diabetic retinopathy using deep learning techniques. The project 
   requires expertise in computer vision, medical image processing, 
   and healthcare AI applications.
   ```
3. Click "Analyze Project"
4. View matched professors with:
   - Match percentage scores
   - Highlighted matching domains
   - Complete academic profiles
   - Contact information

#### 3. **Browse All Professors**

- View complete professor directory
- Filter by college/department
- Sort by various metrics
- Access detailed profiles with one click

---

## 📚 API Documentation

### Base URL
```
http://localhost:5000/api
```

### Endpoints

#### **GET** `/api/professors`
Get all professors with optional filtering.

**Query Parameters:**
- `limit` (integer, optional): Maximum number of results
- `college` (string, optional): Filter by college name

**Response:**
```json
{
  "professors": [
    {
      "id": 1,
      "name": "Dr. John Smith",
      "college": "MIT",
      "email": "john.smith@mit.edu",
      "domain_expertise": "Machine Learning | Computer Vision | AI",
      "google_scholar_url": "https://scholar.google.com/...",
      "phd_thesis": "Advanced Neural Networks for Image Recognition",
      "has_google_scholar": true,
      "expertise_array": ["Machine Learning", "Computer Vision", "AI"]
    }
  ],
  "total_count": 150
}
```

#### **GET** `/api/professors/:id`
Get detailed information about a specific professor.

**Response:**
```json
{
  "id": 1,
  "name": "Dr. John Smith",
  "college": "MIT",
  "email": "john.smith@mit.edu",
  "domain_expertise": "Machine Learning | Computer Vision",
  "google_scholar_url": "https://scholar.google.com/...",
  "semantic_scholar_url": "https://www.semanticscholar.org/...",
  "profile_link": "https://web.mit.edu/john",
  "phd_thesis": "Advanced Neural Networks",
  "expertise_array": ["Machine Learning", "Computer Vision"]
}
```

#### **POST** `/api/ai/search`
AI-powered natural language search.

**Request Body:**
```json
{
  "query": "Find experts in artificial intelligence and robotics"
}
```

**Response:**
```json
{
  "professors": [...],
  "search_metadata": {
    "keywords": ["ai", "artificial intelligence", "robotics"],
    "domains": ["artificial intelligence", "robotics"],
    "intent": "Looking for faculty with expertise in: artificial intelligence, robotics",
    "total_results": 25
  }
}
```

#### **POST** `/api/project/analyze`
Analyze project description and find matching professors.

**Request Body:**
```json
{
  "description": "I need help developing a blockchain-based supply chain tracking system with IoT integration..."
}
```

**Response:**
```json
{
  "analysis": {
    "summary": "Project requires expertise in blockchain, IoT, and distributed systems",
    "required_expertise": ["blockchain", "internet of things", "distributed systems"],
    "key_skills": ["smart contracts", "iot", "sensor networks", "cryptography"]
  },
  "professors": [
    {
      "id": 5,
      "name": "Dr. Jane Doe",
      "match_percentage": 85,
      "matching_domains": ["blockchain", "internet of things"],
      ...
    }
  ],
  "total_matches": 12
}
```

#### **GET** `/api/colleges`
Get list of all colleges with professor counts.

**Response:**
```json
{
  "colleges": [
    {"name": "MIT", "count": 45},
    {"name": "Stanford", "count": 38}
  ]
}
```

#### **GET** `/api/domains`
Get list of all research domains.

**Response:**
```json
{
  "domains": [
    {"id": 1, "name": "Machine Learning", "professor_count": 67},
    {"id": 2, "name": "Computer Vision", "professor_count": 34}
  ]
}
```

---

## 🔄 Data Extraction Pipeline

PRISM employs a sophisticated multi-stage data extraction pipeline:

### Stage 1: Base Data Import
- Excel/CSV files imported into `professors` table
- Basic information: name, college, email, PhD thesis

### Stage 2: Profile Link Extraction
- Google Scholar URLs stored in `plink` table
- Semantic Scholar and institutional profile links cataloged

### Stage 3: Domain Expertise Extraction

**Sources (in priority order):**
1. **Manual declarations** from Excel/CSV
2. **Google Scholar** research interests
3. **Publication analysis** using NLP

**Process:**
```python
# For each professor:
1. Extract research interests from Google Scholar profile
2. Parse and normalize domain names (lowercase, trim, singularize)
3. Map to standardized domain taxonomy
4. Insert into domains table (if new)
5. Create professor-domain link in prof_domain table
```

**Normalization Rules:**
- Convert to title case: "machine learning" → "Machine Learning"
- Handle synonyms: "ML" → "Machine Learning"
- Remove duplicates and variations
- Consolidate related terms

### Stage 4: Citation Metrics (Background Process)

**Extraction:**
- Runs asynchronously to avoid blocking main application
- Fetches h-index, total citations, recent publications
- Caches results in `teacher_citations_cache.json`
- Respects rate limits with `REQUEST_DELAY`

**Update Frequency:**
- Initial: On first professor profile access
- Incremental: Weekly background refresh
- On-demand: Manual trigger via admin endpoint

### Stage 5: Continuous Enrichment
- Periodic re-scraping of scholar profiles
- Publication updates from academic APIs
- User-submitted corrections and additions

### Idempotency & Safety
- All extraction operations are idempotent (safe to re-run)
- UNIQUE constraints prevent duplicate domain entries
- Transactions ensure data consistency
- Rollback on extraction errors

---

## 📁 Project Structure

```
SamsungPrism/
├── prismZip/                          # Backend (Python/Flask)
│   ├── app.py                         # Main Flask application
│   ├── database.py                    # Database connection & queries
│   ├── professor_routes.py            # API route handlers
│   ├── gemma_service.py               # AI/LLM integration
│   ├── google_scholar_extractor.py    # Scholar data scraping
│   ├── scholar_extractor.py           # Citation extraction
│   ├── domain_expertise_analyzer.py   # Domain classification
│   ├── helpers.py                     # Utility functions
│   ├── config.py                      # Configuration management
│   ├── utils.py                       # General utilities
│   ├── requirements.txt               # Python dependencies
│   ├── .env                           # Environment variables (not in git)
│   ├── migrate_excel_to_db.py         # Initial data import script
│   ├── backfill_prof_domains.py       # Domain backfill utility
│   ├── extract_citations.py           # Citation extraction worker
│   └── tests/                         # Backend test suite
│       ├── test_api.py
│       ├── test_domain_expertise.py
│       └── conftest.py
│
├── professors/                        # Frontend (React/TypeScript)
│   ├── public/
│   │   ├── index.html
│   │   └── prism_logo.png
│   ├── src/
│   │   ├── index.tsx                  # Application entry point
│   │   ├── App.jsx                    # Main App component
│   │   ├── index.css                  # Global styles
│   │   ├── components/                # Reusable UI components
│   │   │   ├── ProjectExpertiseMatcher.jsx
│   │   │   ├── ComprehensiveTeacherSearch.jsx
│   │   │   ├── StatCard.jsx
│   │   │   ├── LevelBadge.jsx
│   │   │   └── ThemeToggleButton.jsx
│   │   ├── services/                  # API service layer
│   │   │   └── aiSearchService.js
│   │   ├── pages/                     # Page components
│   │   ├── layouts/                   # Layout components
│   │   └── assets/                    # Static assets
│   ├── package.json                   # Node dependencies
│   ├── tsconfig.json                  # TypeScript config
│   ├── tailwind.config.js             # Tailwind CSS config
│   └── postcss.config.js              # PostCSS config
│
├── README.md                          # This file
├── LICENSE                            # License information
└── .gitignore                         # Git ignore rules
```

---

## 🤝 Contributing

We welcome contributions from the community! Here's how you can help:

### Reporting Issues

1. Check existing issues to avoid duplicates
2. Use the issue template
3. Provide:
   - Clear description of the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - System information (OS, Python version, Node version)
   - Error logs if applicable

### Submitting Pull Requests

1. **Fork the repository**

2. **Create a feature branch:**
   ```bash
   git checkout -b feature/amazing-new-feature
   ```

3. **Make your changes:**
   - Follow existing code style
   - Add tests for new features
   - Update documentation

4. **Test your changes:**
   ```bash
   # Backend tests
   cd prismZip
   pytest

   # Frontend tests
   cd professors
   npm test
   ```

5. **Commit with conventional commits:**
   ```bash
   git commit -m "feat: add amazing new feature"
   git commit -m "fix: resolve search bug"
   git commit -m "docs: update API documentation"
   ```

6. **Push and create PR:**
   ```bash
   git push origin feature/amazing-new-feature
   ```

### Code Style Guidelines

**Python:**
- Follow PEP 8
- Use type hints where applicable
- Document functions with docstrings
- Maximum line length: 120 characters

**JavaScript/TypeScript:**
- Use ESLint configuration
- Prefer functional components with hooks
- Use meaningful variable names
- Add JSDoc comments for complex functions

### Development Workflow

1. Set up development environment
2. Create feature branch from `main`
3. Implement changes with tests
4. Run linters and formatters
5. Submit PR with clear description
6. Address review feedback
7. Merge after approval

---

## 🐛 Troubleshooting

### Common Issues

#### Database Connection Errors

**Symptom:** `Error connecting to MySQL database`

**Solutions:**
1. Verify MySQL is running:
   ```bash
   # Windows
   net start MySQL80
   
   # macOS
   brew services start mysql
   
   # Linux
   sudo systemctl start mysql
   ```

2. Check `.env` credentials are correct
3. Ensure database `prism_professors` exists
4. Test connection:
   ```bash
   mysql -u root -p
   USE prism_professors;
   ```

#### Missing Research Areas in UI

**Symptom:** Professor cards show empty domain expertise

**Solution:**
Run the backfill script:
```bash
cd prismZip
python backfill_prof_domains.py
```

#### Ollama/AI Features Not Working

**Symptom:** Search falls back to keyword matching

**Solutions:**
1. Verify Ollama is running:
   ```bash
   ollama list
   ```

2. Check model is downloaded:
   ```bash
   ollama pull gemma3:4b
   ```

3. Test Ollama endpoint:
   ```bash
   curl http://localhost:11434/api/tags
   ```

4. Review `OLLAMA_BASE_URL` in `.env`

#### Port Already in Use

**Symptom:** `Address already in use: 5000`

**Solutions:**
```bash
# Windows - Find and kill process
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:5000 | xargs kill -9
```

Or change port in `.env`:
```env
PORT=5001
```

#### CORS Errors

**Symptom:** `Access to fetch blocked by CORS policy`

**Solution:**
Ensure Flask-CORS is properly configured in `app.py`:
```python
from flask_cors import CORS
CORS(app, origins=["http://localhost:3000"])
```

#### Frontend Build Errors

**Symptom:** Node.js heap out of memory

**Solution:**
```bash
# Increase Node memory
set NODE_OPTIONS=--max-old-space-size=4096
npm run build
```

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2025 PRISM Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

---

## 🙏 Acknowledgments

- **Google Scholar** for academic data
- **Semantic Scholar** for research metrics
- **Ollama** for local LLM capabilities
- **React** and **Flask** communities
- All contributors and users of PRISM

---

## 📞 Contact & Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/NotVivek12/SamsungPrism/issues)
- **Documentation**: [Full documentation](https://github.com/NotVivek12/SamsungPrism/wiki)
- **Email**: support@prism-app.com

---

<div align="center">

**Built with ❤️ by the PRISM Team**

[⬆ Back to Top](#-prism---professor-research-intelligence--search-mechanism)

</div>
