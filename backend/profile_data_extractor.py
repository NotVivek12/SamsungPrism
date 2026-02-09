"""
Enhanced Profile Data Extractor
Fetches detailed information from College Profile Links, Google Scholar URLs, and Semantic Scholar Links
Includes profile pictures, bio information, research metrics, and academic details
"""

import requests
from bs4 import BeautifulSoup
import re
import time
import sqlite3
from urllib.parse import urljoin, urlparse
import json
from typing import Dict, List, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProfileDataExtractor:
    def __init__(self, db_path: str = 'teachers.db'):
        self.db_path = db_path
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def extract_college_profile_data(self, profile_url: str) -> Dict:
        """Extract data from college profile page"""
        if not profile_url or profile_url.strip() == "":
            return {}
            
        try:
            response = self.session.get(profile_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            profile_data = {}
            
            # Extract profile picture
            profile_pic = self._extract_profile_picture(soup, profile_url)
            if profile_pic:
                profile_data['profile_picture_url'] = profile_pic
                
            # Extract bio/about information
            bio = self._extract_bio_info(soup)
            if bio:
                profile_data['bio'] = bio
                
            # Extract contact information
            contact_info = self._extract_contact_info(soup)
            profile_data.update(contact_info)
            
            # Extract education details
            education = self._extract_education(soup)
            if education:
                profile_data['education'] = education
                
            # Extract teaching areas
            teaching_areas = self._extract_teaching_areas(soup)
            if teaching_areas:
                profile_data['teaching_areas'] = teaching_areas
                
            # Extract awards and achievements
            awards = self._extract_awards(soup)
            if awards:
                profile_data['awards'] = awards
                
            # Extract publications from college profile
            publications = self._extract_college_publications(soup)
            if publications:
                profile_data['college_publications'] = publications
                
            logger.info(f"Extracted college profile data: {len(profile_data)} fields")
            return profile_data
            
        except Exception as e:
            logger.error(f"Error extracting college profile data from {profile_url}: {str(e)}")
            return {}
            
    def extract_google_scholar_data(self, scholar_url: str) -> Dict:
        """Extract data from Google Scholar profile"""
        if not scholar_url or scholar_url.strip() == "":
            return {}
            
        try:
            response = self.session.get(scholar_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            scholar_data = {}
            
            # Extract profile picture from Google Scholar
            scholar_pic = self._extract_scholar_profile_picture(soup, scholar_url)
            if scholar_pic:
                scholar_data['scholar_profile_picture'] = scholar_pic
                
            # Extract citation metrics
            metrics = self._extract_citation_metrics(soup)
            scholar_data.update(metrics)
            
            # Extract research interests
            interests = self._extract_research_interests(soup)
            if interests:
                scholar_data['research_interests'] = interests
                
            # Extract affiliation
            affiliation = self._extract_affiliation(soup)
            if affiliation:
                scholar_data['affiliation'] = affiliation
                
            # Extract recent publications
            publications = self._extract_scholar_publications(soup)
            if publications:
                scholar_data['recent_publications'] = publications
                
            # Extract co-authors
            coauthors = self._extract_coauthors(soup)
            if coauthors:
                scholar_data['frequent_coauthors'] = coauthors
                
            logger.info(f"Extracted Google Scholar data: {len(scholar_data)} fields")
            return scholar_data
            
        except Exception as e:
            logger.error(f"Error extracting Google Scholar data from {scholar_url}: {str(e)}")
            return {}
            
    def extract_semantic_scholar_data(self, semantic_url: str) -> Dict:
        """Extract data from Semantic Scholar profile"""
        if not semantic_url or semantic_url.strip() == "":
            return {}
            
        try:
            response = self.session.get(semantic_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            semantic_data = {}
            
            # Extract Semantic Scholar metrics
            h_index = self._extract_h_index(soup)
            if h_index:
                semantic_data['semantic_h_index'] = h_index
                
            # Extract paper count
            paper_count = self._extract_paper_count(soup)
            if paper_count:
                semantic_data['total_papers'] = paper_count
                
            # Extract citation count
            citation_count = self._extract_semantic_citations(soup)
            if citation_count:
                semantic_data['semantic_citations'] = citation_count
                
            # Extract research areas from Semantic Scholar
            research_areas = self._extract_semantic_research_areas(soup)
            if research_areas:
                semantic_data['semantic_research_areas'] = research_areas
                
            # Extract notable papers
            notable_papers = self._extract_notable_papers(soup)
            if notable_papers:
                semantic_data['notable_papers'] = notable_papers
                
            logger.info(f"Extracted Semantic Scholar data: {len(semantic_data)} fields")
            return semantic_data
            
        except Exception as e:
            logger.error(f"Error extracting Semantic Scholar data from {semantic_url}: {str(e)}")
            return {}
    
    def _extract_profile_picture(self, soup: BeautifulSoup, base_url: str) -> Optional[str]:
        """Extract profile picture from college website"""
        selectors = [
            'img[alt*="profile" i]',
            'img[alt*="photo" i]',
            'img[class*="profile" i]',
            'img[class*="faculty" i]',
            'img[src*="faculty" i]',
            'img[src*="profile" i]',
            '.faculty-image img',
            '.profile-image img',
            '.faculty-photo img',
            'img[alt*="Dr." i]',
            'img[alt*="Prof." i]'
        ]
        
        for selector in selectors:
            img = soup.select_one(selector)
            if img and img.get('src'):
                img_url = urljoin(base_url, img['src'])
                # Validate it's an image URL
                if self._is_valid_image_url(img_url):
                    return img_url
        
        return None
    
    def _extract_scholar_profile_picture(self, soup: BeautifulSoup, base_url: str) -> Optional[str]:
        """Extract profile picture from Google Scholar"""
        img_selectors = [
            '#gsc_prf_pup-img',
            'img[alt="Profile picture"]',
            '.gsc_prf_ila img'
        ]
        
        for selector in img_selectors:
            img = soup.select_one(selector)
            if img and img.get('src'):
                img_url = img['src']
                if img_url.startswith('//'):
                    img_url = 'https:' + img_url
                elif img_url.startswith('/'):
                    img_url = 'https://scholar.google.com' + img_url
                return img_url
        
        return None
    
    def _extract_bio_info(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract bio/about information"""
        bio_selectors = [
            '.bio', '.about', '.description', '.faculty-bio',
            'div[class*="bio" i]', 'div[class*="about" i]',
            'p[class*="bio" i]', 'section[class*="about" i]'
        ]
        
        for selector in bio_selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                if len(text) > 50:  # Ensure it's substantial content
                    return text[:1000]  # Limit length
        
        return None
    
    def _extract_contact_info(self, soup: BeautifulSoup) -> Dict:
        """Extract contact information"""
        contact_info = {}
        
        # Extract phone
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phone_text = soup.get_text()
        phone_match = re.search(phone_pattern, phone_text)
        if phone_match:
            contact_info['phone'] = phone_match.group()
        
        # Extract office location
        office_selectors = [
            'span:contains("Office")', 'div:contains("Office")',
            'span:contains("Room")', 'div:contains("Room")'
        ]
        
        for selector in office_selectors:
            element = soup.select_one(selector)
            if element:
                office_text = element.get_text(strip=True)
                if 'office' in office_text.lower() or 'room' in office_text.lower():
                    contact_info['office_location'] = office_text[:100]
                    break
        
        return contact_info
    
    def _extract_education(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract education details"""
        education_selectors = [
            '.education', '.qualifications', 'div[class*="education" i]',
            'section[class*="education" i]', 'div[class*="qualification" i]'
        ]
        
        for selector in education_selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                if len(text) > 20:
                    return text[:500]
        
        return None
    
    def _extract_teaching_areas(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract teaching areas"""
        teaching_selectors = [
            '.teaching', '.courses', 'div[class*="teaching" i]',
            'div[class*="course" i]', 'section[class*="teaching" i]'
        ]
        
        for selector in teaching_selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                if len(text) > 10:
                    return text[:300]
        
        return None
    
    def _extract_awards(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract awards and achievements"""
        award_selectors = [
            '.awards', '.achievements', '.honors',
            'div[class*="award" i]', 'div[class*="achievement" i]',
            'section[class*="award" i]'
        ]
        
        for selector in award_selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                if len(text) > 10:
                    return text[:400]
        
        return None
    
    def _extract_college_publications(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract publications from college profile"""
        pub_selectors = [
            '.publications', '.research-papers', 'div[class*="publication" i]',
            'section[class*="publication" i]', 'div[class*="research" i]'
        ]
        
        for selector in pub_selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                if len(text) > 20:
                    return text[:800]
        
        return None
    
    def _extract_citation_metrics(self, soup: BeautifulSoup) -> Dict:
        """Extract citation metrics from Google Scholar"""
        metrics = {}
        
        # Extract total citations
        citations_element = soup.select_one('#gsc_rsb_st .gsc_rsb_std')
        if citations_element:
            try:
                metrics['total_citations'] = int(citations_element.get_text(strip=True).replace(',', ''))
            except ValueError:
                pass
        
        # Extract h-index
        h_index_elements = soup.select('#gsc_rsb_st .gsc_rsb_std')
        if len(h_index_elements) >= 2:
            try:
                metrics['h_index'] = int(h_index_elements[1].get_text(strip=True))
            except (ValueError, IndexError):
                pass
        
        # Extract i10-index
        if len(h_index_elements) >= 3:
            try:
                metrics['i10_index'] = int(h_index_elements[2].get_text(strip=True))
            except (ValueError, IndexError):
                pass
        
        return metrics
    
    def _extract_research_interests(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract research interests from Google Scholar"""
        interests_element = soup.select_one('#gsc_prf_int')
        if interests_element:
            interests = []
            for link in interests_element.select('a'):
                interests.append(link.get_text(strip=True))
            if interests:
                return ', '.join(interests)
        
        return None
    
    def _extract_affiliation(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract affiliation from Google Scholar"""
        affiliation_element = soup.select_one('.gsc_prf_ila')
        if affiliation_element:
            return affiliation_element.get_text(strip=True)
        
        return None
    
    def _extract_scholar_publications(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract recent publications from Google Scholar"""
        publications = []
        
        pub_elements = soup.select('#gsc_a_b .gsc_a_tr')[:5]  # Get top 5 publications
        for pub in pub_elements:
            title_element = pub.select_one('.gsc_a_at')
            authors_element = pub.select_one('.gsc_a_at + div')
            year_element = pub.select_one('.gsc_a_y span')
            citations_element = pub.select_one('.gsc_a_c a')
            
            if title_element:
                publication = {
                    'title': title_element.get_text(strip=True),
                    'authors': authors_element.get_text(strip=True) if authors_element else '',
                    'year': year_element.get_text(strip=True) if year_element else '',
                    'citations': citations_element.get_text(strip=True) if citations_element else '0'
                }
                publications.append(publication)
        
        return publications
    
    def _extract_coauthors(self, soup: BeautifulSoup) -> List[str]:
        """Extract frequent co-authors from Google Scholar"""
        coauthors = []
        
        coauthor_elements = soup.select('#gsc_rsb_co .gsc_rsb_aa')
        for author in coauthor_elements:
            name_element = author.select_one('a span')
            if name_element:
                coauthors.append(name_element.get_text(strip=True))
        
        return coauthors[:10]  # Return top 10 co-authors
    
    def _extract_h_index(self, soup: BeautifulSoup) -> Optional[int]:
        """Extract h-index from Semantic Scholar"""
        # This would need to be adapted based on Semantic Scholar's current structure
        # Semantic Scholar might not always display h-index prominently
        return None
    
    def _extract_paper_count(self, soup: BeautifulSoup) -> Optional[int]:
        """Extract paper count from Semantic Scholar"""
        # Look for paper count indicators
        text = soup.get_text()
        paper_match = re.search(r'(\d+)\s+papers?', text, re.IGNORECASE)
        if paper_match:
            try:
                return int(paper_match.group(1))
            except ValueError:
                pass
        
        return None
    
    def _extract_semantic_citations(self, soup: BeautifulSoup) -> Optional[int]:
        """Extract citation count from Semantic Scholar"""
        text = soup.get_text()
        citation_match = re.search(r'(\d+)\s+citations?', text, re.IGNORECASE)
        if citation_match:
            try:
                return int(citation_match.group(1))
            except ValueError:
                pass
        
        return None
    
    def _extract_semantic_research_areas(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract research areas from Semantic Scholar"""
        # This would need to be adapted based on current Semantic Scholar structure
        return None
    
    def _extract_notable_papers(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract notable papers from Semantic Scholar"""
        papers = []
        # This would need to be implemented based on Semantic Scholar's structure
        return papers
    
    def _is_valid_image_url(self, url: str) -> bool:
        """Check if URL points to a valid image"""
        try:
            response = self.session.head(url, timeout=5)
            content_type = response.headers.get('content-type', '').lower()
            return 'image' in content_type
        except:
            return url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))
    
    def extract_all_profile_data(self, teacher_name: str, profile_link: str, 
                                google_scholar_url: str, semantic_scholar_url: str) -> Dict:
        """Extract all profile data for a teacher"""
        logger.info(f"Extracting profile data for: {teacher_name}")
        
        all_data = {'teacher_name': teacher_name}
        
        # Extract college profile data
        if profile_link:
            college_data = self.extract_college_profile_data(profile_link)
            all_data.update(college_data)
            time.sleep(1)  # Be respectful with requests
        
        # Extract Google Scholar data
        if google_scholar_url:
            scholar_data = self.extract_google_scholar_data(google_scholar_url)
            all_data.update(scholar_data)
            time.sleep(1)  # Be respectful with requests
        
        # Extract Semantic Scholar data
        if semantic_scholar_url:
            semantic_data = self.extract_semantic_scholar_data(semantic_scholar_url)
            all_data.update(semantic_data)
            time.sleep(1)  # Be respectful with requests
        
        return all_data
    
    def update_database_with_profile_data(self):
        """Update database with enhanced profile data for all teachers"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # First, add new columns to store profile data if they don't exist
        new_columns = [
            ('profile_picture_url', 'TEXT'),
            ('scholar_profile_picture', 'TEXT'),
            ('bio', 'TEXT'),
            ('phone', 'TEXT'),
            ('office_location', 'TEXT'),
            ('education', 'TEXT'),
            ('teaching_areas', 'TEXT'),
            ('awards', 'TEXT'),
            ('college_publications', 'TEXT'),
            ('total_citations', 'INTEGER'),
            ('h_index', 'INTEGER'),
            ('i10_index', 'INTEGER'),
            ('research_interests', 'TEXT'),
            ('affiliation', 'TEXT'),
            ('recent_publications', 'TEXT'),
            ('frequent_coauthors', 'TEXT'),
            ('semantic_h_index', 'INTEGER'),
            ('total_papers', 'INTEGER'),
            ('semantic_citations', 'INTEGER'),
            ('semantic_research_areas', 'TEXT'),
            ('notable_papers', 'TEXT'),
            ('profile_data_updated', 'TIMESTAMP')
        ]
        
        for column_name, column_type in new_columns:
            try:
                cursor.execute(f'ALTER TABLE teachers ADD COLUMN {column_name} {column_type}')
                logger.info(f"Added column: {column_name}")
            except sqlite3.OperationalError as e:
                if "duplicate column name" not in str(e):
                    logger.error(f"Error adding column {column_name}: {e}")
        
        conn.commit()
        
        # Get all teachers with profile links
        cursor.execute('''
            SELECT id, name, profile_link, google_scholar_url, semantic_scholar_url 
            FROM teachers 
            WHERE (profile_link IS NOT NULL AND profile_link != '') 
               OR (google_scholar_url IS NOT NULL AND google_scholar_url != '')
               OR (semantic_scholar_url IS NOT NULL AND semantic_scholar_url != '')
        ''')
        
        teachers = cursor.fetchall()
        logger.info(f"Found {len(teachers)} teachers with profile links to process")
        
        for teacher_id, name, profile_link, google_scholar_url, semantic_scholar_url in teachers:
            try:
                # Extract all profile data
                profile_data = self.extract_all_profile_data(
                    name, profile_link, google_scholar_url, semantic_scholar_url
                )
                
                if profile_data and len(profile_data) > 1:  # More than just teacher_name
                    # Prepare update query
                    update_fields = []
                    update_values = []
                    
                    for key, value in profile_data.items():
                        if key != 'teacher_name' and value is not None:
                            if isinstance(value, (list, dict)):
                                value = json.dumps(value)
                            update_fields.append(f'{key} = ?')
                            update_values.append(value)
                    
                    if update_fields:
                        update_fields.append('profile_data_updated = CURRENT_TIMESTAMP')
                        update_values.append(teacher_id)
                        
                        update_query = f'''
                            UPDATE teachers 
                            SET {', '.join(update_fields)}
                            WHERE id = ?
                        '''
                        
                        cursor.execute(update_query, update_values)
                        conn.commit()
                        
                        logger.info(f"Updated profile data for {name} - {len(update_fields)-1} fields")
                
                # Add delay between teachers to be respectful
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Error processing {name}: {str(e)}")
                continue
        
        conn.close()
        logger.info("Profile data extraction completed")

def main():
    """Main function to extract and update profile data"""
    extractor = ProfileDataExtractor()
    extractor.update_database_with_profile_data()

if __name__ == "__main__":
    main()