# Teacher Details Extraction Report
**Date:** September 20, 2025  
**Source File:** sirs.xlsx  
**Total Teachers Processed:** 206  

## 📊 Summary Statistics

- **Total Records in Excel:** 207 (1 test record removed)
- **Valid Teacher Records:** 206
- **Teachers with Google Scholar:** 187 (90.8%)
- **Teachers with Semantic Scholar:** 70 (34.0%)
- **Teachers with Domain Expertise:** 200 (97.1%)
- **Teachers with PhD Thesis Info:** 183 (88.8%)

## 🏆 Top Research Domains

| Rank | Domain | Number of Teachers |
|------|--------|-------------------|
| 1 | Machine Learning | 36 |
| 2 | AI | 27 |
| 3 | IoT | 20 |
| 4 | Deep Learning | 20 |
| 5 | Artificial Intelligence | 17 |
| 6 | Image Processing | 16 |
| 7 | ML | 14 |
| 8 | NLP | 10 |
| 9 | Computer Vision | 8 |
| 10 | Data Analytics | 8 |

## 📋 Data Structure

Each teacher record contains the following fields:
- **Name:** Full name of the professor
- **College:** Institution/University name
- **Email:** College email address
- **Profile Link:** College profile URL
- **Domain Expertise:** Research areas and specializations
- **PhD Thesis:** Thesis topic/title
- **Google Scholar URL:** Google Scholar profile link
- **Semantic Scholar URL:** Semantic Scholar profile link
- **Timestamp:** When the data was collected

## 📁 Generated Files

1. **`teachers.db`** - SQLite database containing all teacher records
2. **`teachers_data.json`** - JSON file with complete teacher data
3. **`extract_teachers.py`** - Python script used for extraction

## 🔗 Sample Teacher Records

### 1. Dr. Jayakumar Sadhasivam
- **Institution:** Vellore Institute of Technology, Vellore
- **Email:** jayakumars@vit.ac.in
- **Domain:** Network and Cyber Security, AI, Web3.0
- **PhD Thesis:** Hybrid Machine Learning Technique for Massive Open Online Course Using Sentiment Classification and Opinion Analysis for Product Review
- **Google Scholar:** ✅ Available
- **Semantic Scholar:** ❌ Not available

### 2. Ramesh Ashok Tabib
- **Institution:** KLE Technological University
- **Email:** ramesh_t@kletech.ac.in
- **Domain:** Visual Intelligence, GenAI, Computer Vision
- **PhD Thesis:** Learning Representation
- **Google Scholar:** ✅ Available
- **Semantic Scholar:** ✅ Available

### 3. Dr. Sowmya BJ
- **Institution:** Ramaiah Institute of Technology
- **Email:** sowmyabj@msrit.edu
- **Domain:** Artificial Intelligence, Machine learning, Quantum Computing, Security
- **PhD Thesis:** Building an Utility system to provide Data Analytic solutions for Agricultural Challenges in context with Cyber Physical Systems
- **Google Scholar:** ✅ Available
- **Semantic Scholar:** ✅ Available

## 🎯 Research Area Distribution

### Machine Learning & AI (Combined: 80+ teachers)
- Machine Learning: 36 teachers
- AI: 27 teachers
- Artificial Intelligence: 17 teachers
- Deep Learning: 20 teachers
- ML: 14 teachers

### Computer Science Specializations
- Image Processing: 16 teachers
- Computer Vision: 8 teachers
- NLP: 10 teachers
- IoT: 20 teachers
- Data Analytics: 8 teachers

## 🏛️ Top Institutions (by number of teachers)

Based on the extracted data, the institutions with the most teachers include:
- Vellore Institute of Technology (multiple campuses)
- Ramaiah Institute of Technology
- KLE Technological University
- B.M.S College Of Engineering
- PSG College of Technology
- Chandigarh University
- And many other prestigious institutions

## 📊 Data Quality Assessment

- **High Quality Records:** 187 teachers (90.8%) have Google Scholar profiles
- **Complete Profiles:** 183 teachers (88.8%) have PhD thesis information
- **Domain Expertise:** 200 teachers (97.1%) have specified research domains
- **Email Availability:** Most teachers have institutional email addresses

## 🚀 Next Steps

With this extracted data, you can now:

1. **Academic Collaboration:** Find experts in specific research domains
2. **Research Mapping:** Analyze research trends across institutions
3. **Scholar Metrics:** Extract citation data from Google Scholar profiles
4. **Network Analysis:** Build academic collaboration networks
5. **Publication Analysis:** Analyze research publications and impact

## 💾 Database Access

The data is stored in SQLite database (`teachers.db`) with the following structure:

```sql
CREATE TABLE teachers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    college TEXT,
    email TEXT,
    profile_link TEXT,
    domain_expertise TEXT,
    phd_thesis TEXT,
    google_scholar_url TEXT,
    semantic_scholar_url TEXT,
    timestamp TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 📖 Usage Examples

### Query teachers by domain:
```python
import sqlite3
conn = sqlite3.connect('teachers.db')
cursor = conn.cursor()
cursor.execute("SELECT name, college FROM teachers WHERE domain_expertise LIKE '%Machine Learning%'")
ml_experts = cursor.fetchall()
```

### Load JSON data:
```python
import json
with open('teachers_data.json', 'r', encoding='utf-8') as f:
    teachers = json.load(f)
```

---

**✅ Extraction completed successfully!**  
**Total time:** < 1 minute  
**Success rate:** 100% (206/206 records processed)  
**Data integrity:** Verified and validated