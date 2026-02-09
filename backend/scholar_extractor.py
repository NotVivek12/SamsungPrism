import spacy
import re
import requests
import json
import logging
from typing import Dict, List, Any
from urllib.parse import urlparse

def combine_scholar_data(semantic_data: Dict, teacher_data: Dict) -> Dict:
    """
    Enhanced function to combine Google Scholar and Semantic Scholar data.
    Uses the best available data from either source and creates a unified view.
    
    Args:
        semantic_data: Dictionary containing Semantic Scholar data
        teacher_data: Dictionary containing Google Scholar data
        
    Returns:
        Dict: Combined and enhanced scholarly data
    """
    try:
        semantic_scholar = semantic_data.get('Semantic Scholar Data', {})
        google_scholar = teacher_data.get('Google Scholar Data', {})
        
        logging.info("Combining scholarly data from multiple sources")
        
        # Always use the non-zero or higher value for citations
        gs_citations = google_scholar.get('Citations', 0)
        ss_citations = semantic_scholar.get('Citations', 0)
        
        if gs_citations > 0 and (ss_citations == 0 or gs_citations > ss_citations):
            semantic_scholar['Citations'] = gs_citations
            semantic_scholar['_citation_source'] = 'Google Scholar'
        elif ss_citations > 0:
            semantic_scholar['_citation_source'] = 'Semantic Scholar'
            
        # Same approach for h-index
        gs_h_index = google_scholar.get('h-index', 0)
        ss_h_index = semantic_scholar.get('h-index', 0)
        
        if gs_h_index > 0 and (ss_h_index == 0 or gs_h_index > ss_h_index):
            semantic_scholar['h-index'] = gs_h_index
            semantic_scholar['_h_index_source'] = 'Google Scholar'
        elif ss_h_index > 0:
            semantic_scholar['_h_index_source'] = 'Semantic Scholar'
            
        # For i10-index, only Google Scholar provides this
        if google_scholar.get('i10_index', 0) > 0:
            semantic_scholar['i10-index'] = google_scholar.get('i10_index', 0)
            semantic_scholar['_i10_index_source'] = 'Google Scholar'
            
        # Combine publications from both sources if needed
        gs_publications = google_scholar.get('Publications', [])
        ss_publications = semantic_scholar.get('Publications', [])
        
        # Use Google Scholar publications if Semantic Scholar has none
        if not ss_publications and gs_publications:
            semantic_scholar['Publications'] = gs_publications
            semantic_scholar['_publications_source'] = 'Google Scholar'
        # Or merge them if both have publications
        elif ss_publications and gs_publications:
            # Create a set of existing titles to avoid duplicates
            existing_titles = {pub['title'].lower() for pub in ss_publications}
            
            # Add Google Scholar publications that don't exist in Semantic Scholar
            for gs_pub in gs_publications:
                if gs_pub['title'].lower() not in existing_titles:
                    ss_publications.append(gs_pub)
                    existing_titles.add(gs_pub['title'].lower())
            
            semantic_scholar['Publications'] = ss_publications
            semantic_scholar['_publications_source'] = 'Combined'
            
        # Recalculate total publications
        if semantic_scholar.get('Publications'):
            semantic_scholar['Total Publications'] = len(semantic_scholar['Publications'])
        elif google_scholar.get('Total Publications', 0) > semantic_scholar.get('Total Publications', 0):
            semantic_scholar['Total Publications'] = google_scholar.get('Total Publications', 0)
            
        # Combine research interests/topics
        gs_interests = google_scholar.get('Research Interests', [])
        ss_topics = semantic_scholar.get('Research Topics', [])
        
        combined_topics = list(set(gs_interests + ss_topics))
        if combined_topics:
            semantic_scholar['Research Topics'] = combined_topics[:10]  # Limit to top 10
            
        # Update current affiliation if missing
        if semantic_scholar.get('Current Affiliation') == 'Not available' and google_scholar.get('Current Affiliation'):
            semantic_scholar['Current Affiliation'] = google_scholar.get('Current Affiliation')
            
        # Debug info
        semantic_scholar['_debug'] = {
            'combined_from': ['Semantic Scholar', 'Google Scholar'],
            'citation_sources': {
                'semantic_scholar': ss_citations,
                'google_scholar': gs_citations
            },
            'h_index_sources': {
                'semantic_scholar': ss_h_index,
                'google_scholar': gs_h_index
            }
        }
        
        logging.info(f"Successfully combined scholarly data: citations={semantic_scholar['Citations']}, h-index={semantic_scholar['h-index']}")
        return semantic_data
        
    except Exception as e:
        logging.error(f"Error combining scholarly data: {str(e)}")
        # If anything goes wrong, return the original Semantic Scholar data
        return semantic_data

def process_paper_with_nlp(nlp, title: str, abstract: str = None) -> Dict[str, Any]:
    """Process paper title and abstract with spaCy NLP."""
    result = {'research_topics': set()}
    
    # Process title
    doc = nlp(title)
    for ent in doc.ents:
        if ent.label_ in ['ORG', 'PRODUCT', 'GPE']:
            result['research_topics'].add(ent.text)
            
    # Look for technical terms in noun phrases
    for chunk in doc.noun_chunks:
        if any(token.pos_ in ['NOUN', 'PROPN'] for token in chunk):
            result['research_topics'].add(chunk.text)
    
    # Process abstract if available
    if abstract:
        doc = nlp(abstract)
        for sent in doc.sents:
            # Look for sentences describing methodology or findings
            if any(keyword in sent.text.lower() for keyword in ['method', 'approach', 'technique', 'framework', 'result']):
                for chunk in sent.noun_chunks:
                    if any(token.pos_ in ['NOUN', 'PROPN'] for token in chunk):
                        result['research_topics'].add(chunk.text)
    
    result['research_topics'] = list(result['research_topics'])
    return result

def extract_semantic_scholar_data(semantic_scholar_url: str, nlp) -> Dict[str, Any]:
    """
    Enhanced Semantic Scholar data extraction with NLP processing.
    """
    default_response = {
        'Semantic Scholar Data': {
            'status': 'error',
            'Citations': 0,
            'h-index': 0,
            'Total Publications': 0,
            'Current Affiliation': 'Not available',
            'Research Topics': [],
            'Publications': [],
            'Research Trends': {},
            'Citation Impact': {
                'Recent Papers': 0,
                'High Impact Papers': 0,
                'Average Citations Per Paper': 0
            }
        }
    }

    try:
        # Extract author ID from URL
        parsed_url = urlparse(semantic_scholar_url)
        path_parts = parsed_url.path.strip('/').split('/')
        
        if 'author' in path_parts:
            # Get the numeric ID which is always the last part of the URL
            author_id = path_parts[-1]
            if not author_id.isalnum():  # Verify it's a valid ID
                raise ValueError("Invalid author ID format")
        else:
            raise ValueError("Could not find author ID in URL")

        # Fetch author data
        api_url = f"https://api.semanticscholar.org/graph/v1/author/{author_id}"
        params = {
            'fields': 'name,affiliations,paperCount,citationCount,hIndex,papers.limit(20),papers.year,papers.title,papers.abstract,papers.citationCount,papers.fieldsOfStudy,papers.venue'
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 Academic Research Bot',
            'Accept': 'application/json'
        }
        
        try:
            response = requests.get(api_url, params=params, headers=headers, timeout=15)
            
            # If we get a bad request with the complex query, try a simpler one
            if response.status_code == 400:
                simple_params = {
                    'fields': 'name,affiliations,paperCount,citationCount,hIndex,papers'
                }
                response = requests.get(api_url, params=simple_params, headers=headers, timeout=15)
            
            if response.status_code == 404:
                raise ValueError(f"Author ID {author_id} not found in Semantic Scholar")
            elif response.status_code == 429:
                raise ValueError("Rate limit exceeded. Please try again later.")
            
            response.raise_for_status()
            
            data = response.json()
            
            # If citation data is missing, try alternate endpoint
            if response.status_code == 200 and not (data.get('citationCount') or data.get('hIndex')):
                try:
                    # Try the alternative author lookup endpoint
                    alt_api_url = f"https://api.semanticscholar.org/graph/v1/paper/search"
                    alt_params = {
                        'query': f'author:{data.get("name", author_id)}',
                        'limit': 100,
                        'fields': 'title,year,citationCount,authors'
                    }
                    
                    alt_response = requests.get(alt_api_url, params=alt_params, headers=headers, timeout=10)
                    if alt_response.status_code == 200:
                        alt_data = alt_response.json()
                        
                        # Calculate citation metrics from paper search
                        if 'data' in alt_data and isinstance(alt_data['data'], list):
                            papers = alt_data['data']
                            
                            # Get total citations
                            total_alt_citations = sum(paper.get('citationCount', 0) for paper in papers)
                            if total_alt_citations > 0:
                                data['citationCount'] = total_alt_citations
                                
                            # Calculate h-index
                            citation_counts = sorted([paper.get('citationCount', 0) for paper in papers], reverse=True)
                            h_index = 0
                            for i, citations in enumerate(citation_counts):
                                if citations >= i + 1:
                                    h_index = i + 1
                                else:
                                    break
                            data['hIndex'] = h_index
                except Exception:
                    # Ignore errors from alternate endpoint
                    pass
            
            # Debug log the response structure
            logging.info(f"Semantic Scholar API response: {json.dumps(data, indent=2)}")
            
            # Check for alternate citation data locations
            citation_count = None
            h_index = None
            
            if 'citationCount' in data:
                citation_count = data['citationCount']
            elif 'citations' in data:
                citation_count = data['citations']
                
            if 'hIndex' in data:
                h_index = data['hIndex']
            elif 'h-index' in data:
                h_index = data['h-index']
            elif 'hindex' in data:
                h_index = data['hindex']
                
            # Store these for later use
            data['_extracted_citation_count'] = citation_count
            data['_extracted_h_index'] = h_index
                
        except ValueError:
            raise ValueError("Invalid JSON response from Semantic Scholar API")
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Request error: {str(e)}")

        # Process publications
        publications = []
        research_topics = set()
        yearly_pubs = {}
        total_citations = 0
        recent_papers = 0
        high_impact_papers = 0
        manual_citation_count = 0
        
        if 'papers' in data:
            # Handle both array and object format
            papers_data = data['papers']
            papers = []
            
            if isinstance(papers_data, list):
                papers = papers_data
            elif isinstance(papers_data, dict) and 'data' in papers_data:
                papers = papers_data['data']
            
            # Sort by year (handle potential missing years)
            try:
                papers = sorted(papers, 
                              key=lambda x: int(x.get('year', 0)) if x.get('year') else 0,
                              reverse=True)
            except (TypeError, ValueError):
                # If sorting fails, use as is
                pass
            
            current_year = 2025  # Current year
            
            for paper in papers[:20]:  # Process top 20 recent papers
                if not isinstance(paper, dict):
                    continue
                    
                title = paper.get('title')
                year = paper.get('year')
                
                if not title:
                    continue
                    
                # Default year to current if missing
                if not year:
                    year = current_year
                
                # Make sure year is string
                year = str(year)
                    
                # Process paper with NLP (safely)
                try:
                    nlp_results = process_paper_with_nlp(nlp, title, paper.get('abstract'))
                    research_topics.update(nlp_results.get('research_topics', []))
                except Exception:
                    nlp_results = {'research_topics': []}
                
                # Track yearly publications
                yearly_pubs[year] = yearly_pubs.get(year, 0) + 1
                
                # Track impact metrics
                citations = paper.get('citationCount', 0)
                if citations > 0:
                    manual_citation_count += citations
                total_citations += citations
                
                try:
                    if int(year) >= current_year - 3:  # Papers in last 3 years
                        recent_papers += 1
                except ValueError:
                    pass
                    
                if citations >= 10:  # High impact threshold
                    high_impact_papers += 1
                
                pub_data = {
                    'title': title,
                    'year': year,
                    'citations': citations,
                    'venue': paper.get('venue', 'Unknown'),
                    'fields': paper.get('fieldsOfStudy', []) if isinstance(paper.get('fieldsOfStudy'), list) else []
                }
                
                # Add research topics if available
                if nlp_results.get('research_topics'):
                    topics = nlp_results['research_topics']
                    if isinstance(topics, list) and topics:
                        pub_data['research_topics'] = topics[:3]  # Top 3 topics per paper
                
                publications.append(pub_data)

        # Process affiliation (safely)
        current_affiliation = "Not available"
        if data.get('affiliations') and isinstance(data['affiliations'], list) and data['affiliations']:
            try:
                affiliation_text = str(data['affiliations'][0])
                doc = nlp(affiliation_text)
                org_name = next((ent.text for ent in doc.ents if ent.label_ == 'ORG'), affiliation_text)
                current_affiliation = org_name
            except Exception:
                # If any error in processing, use the raw affiliation
                current_affiliation = str(data['affiliations'][0]) if data['affiliations'] else "Not available"

        # Calculate average citations (safely)
        try:
            avg_citations = round(total_citations / len(publications), 2) if publications else 0
        except:
            avg_citations = 0
            
        # Safely get primary fields
        primary_fields = []
        try:
            field_counter = {}
            for paper in publications:
                for field in paper.get('fields', []):
                    if field:
                        field_counter[field] = field_counter.get(field, 0) + 1
            
            # Get top 3 fields
            primary_fields = sorted(field_counter.items(), key=lambda x: x[1], reverse=True)
            primary_fields = [field[0] for field in primary_fields[:3]]
        except:
            primary_fields = []

        # Safe list conversion of research topics
        try:
            research_topics_list = list(sorted(research_topics))[:5] if research_topics else []
        except:
            research_topics_list = []

        # Calculate citation metrics if missing
        if not data.get('_extracted_citation_count'):
            if manual_citation_count > 0:
                data['_extracted_citation_count'] = manual_citation_count
            elif publications:
                # Sum up citations from papers if available
                calculated_citations = sum(paper.get('citations', 0) for paper in publications)
                if calculated_citations > 0:
                    data['_extracted_citation_count'] = calculated_citations
                
        # Calculate h-index if missing
        if not data.get('_extracted_h_index') and publications:
            # Simple h-index calculation from papers
            citation_counts = sorted([paper.get('citations', 0) for paper in publications], reverse=True)
            h_index = 0
            for i, citations in enumerate(citation_counts):
                if citations >= i + 1:
                    h_index = i + 1
                else:
                    break
            data['_extracted_h_index'] = h_index

        return {
            'Semantic Scholar Data': {
                'status': 'success',
                'Citations': data.get('_extracted_citation_count', 0) or data.get('citationCount', 0) or sum(paper.get('citations', 0) for paper in publications),
                'h-index': data.get('_extracted_h_index', 0) or data.get('hIndex', 0),
                'Total Publications': data.get('paperCount', 0) or len(publications),
                'Current Affiliation': current_affiliation,
                'Research Topics': research_topics_list,  # Top 5 overall topics
                'Publications': publications,
                'Research Trends': {
                    'Yearly Publications': dict(sorted(yearly_pubs.items(), reverse=True)[:5]) if yearly_pubs else {},
                    'Recent Activity': f"{recent_papers} papers in last 3 years",
                    'Primary Fields': primary_fields
                },
                'Citation Impact': {
                    'Recent Papers': recent_papers,
                    'High Impact Papers': high_impact_papers,
                    'Average Citations Per Paper': avg_citations
                }
            }
        }
        
    except Exception as e:
        default_response['Semantic Scholar Data']['reason'] = f"Error: {str(e)}"
        return default_response