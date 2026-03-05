"""
Extract citations for all teachers with Google Scholar URLs and cache them
"""
import os
import json
import time
import random
import logging
import requests
from bs4 import BeautifulSoup
import threading
import concurrent.futures

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('citation_extraction.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('citations_extractor')

# Constants
CACHE_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'teacher_citations_cache.json')
CACHE_EXPIRY = 86400  # 24 hours in seconds

# Rotating user agents to avoid detection
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
]

def extract_citations(url, retry_count=2):
    """
    Extract only the citations count from a Google Scholar profile URL
    
    Args:
        url: Google Scholar profile URL
        retry_count: number of retries on failure
        
    Returns:
        Dictionary with citations count or None if extraction failed
    """
    for attempt in range(retry_count + 1):
        try:
            # Random delay between requests to avoid rate limiting
            if attempt > 0:
                delay = random.uniform(3, 8) * (attempt + 1)
                logger.info(f"Retry {attempt} for {url}, waiting {delay:.1f}s")
                time.sleep(delay)
            
            # Use a browser-like session with rotating user agents
            session = requests.Session()
            
            headers = {
                'User-Agent': random.choice(USER_AGENTS),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0',
            }
            
            # First visit scholar.google.com to get cookies
            try:
                session.get('https://scholar.google.com', headers=headers, timeout=10)
                time.sleep(random.uniform(0.5, 1.5))
            except Exception:
                pass  # Not critical if this fails
            
            # Fetch the profile page
            response = session.get(url, headers=headers, timeout=15)
            
            if response.status_code == 429:
                logger.warning(f"Rate limited (429) for {url}, attempt {attempt+1}")
                continue
            
            if response.status_code != 200:
                logger.warning(f"Failed to fetch Google Scholar profile: Status code {response.status_code} for {url}")
                continue
            
            # Check if we got a CAPTCHA page
            if 'captcha' in response.text.lower() or 'unusual traffic' in response.text.lower():
                logger.warning(f"CAPTCHA detected for {url}, attempt {attempt+1}")
                continue
                
            # Parse HTML with BeautifulSoup for basic structure
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract metrics (citations, h-index, i10-index)
            metrics_data = {}
            metrics_table = soup.select_one('table#gsc_rsb_st')
            if metrics_table:
                rows = metrics_table.select('tr')
                for row in rows[1:]:  # Skip header row
                    cols = row.select('td')
                    if len(cols) >= 2:
                        metric_name = cols[0].get_text(strip=True)
                        metric_value = cols[1].get_text(strip=True)
                        metrics_data[metric_name] = int(metric_value) if metric_value.isdigit() else metric_value
            
            # Get total citations
            total_citations = metrics_data.get('Citations', 0)
            h_index = metrics_data.get('h-index', 0)
            i10_index = metrics_data.get('i10-index', 0)
            
            # If we got actual data (at least one metric is nonzero), return it
            if total_citations > 0 or h_index > 0 or i10_index > 0:
                logger.info(f"Successfully extracted citations for {url}: citations={total_citations}, h={h_index}, i10={i10_index}")
                return {
                    'citations': total_citations,
                    'h_index': h_index,
                    'i10_index': i10_index,
                    'extraction_success': True
                }
            
            # If metrics_table was found but values are 0, they might genuinely be 0
            if metrics_table:
                logger.info(f"Metrics table found but values are 0 for {url} (may be genuine)")
                return {
                    'citations': total_citations,
                    'h_index': h_index,
                    'i10_index': i10_index,
                    'extraction_success': True
                }
            
            # No metrics table found - page was likely blocked or incomplete
            logger.warning(f"No metrics table found for {url}, attempt {attempt+1}")
            continue
            
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout for {url}, attempt {attempt+1}")
            continue
        except Exception as e:
            logger.error(f"Error extracting citations from {url}: {str(e)}")
            continue
    
    # All retries failed
    logger.error(f"All {retry_count+1} attempts failed for {url}")
    return None

def load_teachers_data():
    """
    Load teachers data from JSON file or database
    """
    try:
        # Try to load from teachers_data.json (use absolute path relative to backend dir)
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        json_path = os.path.join(backend_dir, 'teachers_data.json')
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Check if the data has a "teachers" key (the expected format)
                if isinstance(data, dict) and "teachers" in data:
                    teachers = data["teachers"]
                    logger.info(f"Successfully loaded {len(teachers)} teachers from teachers_data.json")
                    return teachers
                else:
                    # If it's already an array
                    if isinstance(data, list):
                        logger.info(f"Successfully loaded {len(data)} teachers from teachers_data.json")
                        return data
                    else:
                        logger.error("Invalid format in teachers_data.json")
                        return []
        except (FileNotFoundError, IOError) as e:
            logger.warning(f"Could not load from {json_path}: {str(e)}")
            # If file not found, try to import from database module
            try:
                # Add backend dir to sys.path so we can import database
                import sys
                if backend_dir not in sys.path:
                    sys.path.insert(0, backend_dir)
                import database
                teachers = database.load_professors_data()
                logger.info(f"Successfully loaded {len(teachers)} teachers from database")
                return teachers
            except ImportError:
                logger.error("Could not import database module")
                return []
    except Exception as e:
        logger.error(f"Error loading teachers data: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return []

def load_citations_cache():
    """
    Load citations from cache file if it exists and is not expired
    """
    try:
        if os.path.exists(CACHE_FILE):
            # Check if cache file is still valid (not expired)
            cache_age = time.time() - os.path.getmtime(CACHE_FILE)
            if cache_age < CACHE_EXPIRY:
                with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
                    # Filter: only return entries that were successfully extracted
                    valid_cache = {}
                    for key, val in cache.items():
                        if val.get('extraction_success', False) or val.get('citations', 0) > 0 or val.get('h_index', 0) > 0:
                            valid_cache[key] = val
                    logger.info(f"Loaded cache with {len(valid_cache)} valid entries out of {len(cache)} total")
                    return valid_cache
            else:
                logger.info(f"Cache expired (age: {cache_age/3600:.1f}h > {CACHE_EXPIRY/3600:.1f}h)")
        return {}
    except Exception as e:
        logger.error(f"Error loading citations cache: {str(e)}")
        return {}

def load_citations_cache_raw():
    """
    Load ALL citations from cache file (including failed extractions) for re-processing.
    Does NOT check expiry.
    """
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.error(f"Error loading raw citations cache: {str(e)}")
        return {}

def save_citations_cache(cache_data):
    """
    Save citations data to cache file
    """
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, indent=2)
        logger.info(f"Citations cache saved to {CACHE_FILE}")
    except Exception as e:
        logger.error(f"Error saving citations cache: {str(e)}")

def extract_and_cache_citations():
    """
    Extract citations for all teachers with Google Scholar URLs and cache them
    """
    logger.info("Starting citations extraction process")
    
    # Load existing teachers data
    teachers = load_teachers_data()
    
    # Load existing cache (raw, including failures, for re-processing)
    citations_cache = load_citations_cache_raw()
    
    # Count teachers with Google Scholar URLs
    gs_teachers = [t for t in teachers if t.get('google_scholar_url')]
    total_gs_teachers = len(gs_teachers)
    
    logger.info(f"Found {total_gs_teachers} teachers with Google Scholar URLs")
    
    if total_gs_teachers == 0:
        logger.info("No teachers with Google Scholar URLs found")
        return citations_cache
    
    # Check which teachers need citation extraction
    teachers_to_process = []
    for teacher in gs_teachers:
        teacher_id = str(teacher.get('id', ''))
        gs_url = teacher.get('google_scholar_url', '')
        
        # Skip if already cached WITH SUCCESSFUL extraction and not expired
        if teacher_id in citations_cache:
            entry = citations_cache[teacher_id]
            if entry.get('extraction_success', False) and 'timestamp' in entry:
                cache_age = time.time() - entry['timestamp']
                if cache_age < CACHE_EXPIRY:
                    continue
        
        teachers_to_process.append((teacher_id, gs_url))
    
    logger.info(f"Need to extract citations for {len(teachers_to_process)} teachers")
    
    if not teachers_to_process:
        logger.info("All citations are cached and valid")
        return citations_cache
    
    # Extract citations SEQUENTIALLY with delays to avoid rate limiting
    # (parallel requests to Google Scholar get blocked very quickly)
    successful = 0
    failed = 0
    
    for i, (teacher_id, gs_url) in enumerate(teachers_to_process):
        try:
            # Add delay between requests (important to avoid rate limiting)
            if i > 0:
                delay = random.uniform(5, 12)
                logger.info(f"Waiting {delay:.1f}s before next request...")
                time.sleep(delay)
            
            citation_data = extract_citations(gs_url)
            if citation_data and citation_data.get('extraction_success', False):
                # Store in cache with timestamp
                citations_cache[teacher_id] = {
                    'citations': citation_data.get('citations', 0),
                    'h_index': citation_data.get('h_index', 0),
                    'i10_index': citation_data.get('i10_index', 0),
                    'timestamp': time.time(),
                    'extraction_success': True
                }
                successful += 1
                logger.info(f"[{i+1}/{len(teachers_to_process)}] Extracted citations for teacher {teacher_id}: {citation_data}")
            else:
                # Mark as failed - do NOT overwrite previously successful data
                if teacher_id not in citations_cache or not citations_cache[teacher_id].get('extraction_success', False):
                    citations_cache[teacher_id] = {
                        'citations': 0,
                        'h_index': 0,
                        'i10_index': 0,
                        'timestamp': time.time(),
                        'extraction_success': False
                    }
                failed += 1
                logger.warning(f"[{i+1}/{len(teachers_to_process)}] Failed to extract citations for teacher {teacher_id}")
            
            # Save cache periodically (every 5 teachers)
            if (i + 1) % 5 == 0 or i == len(teachers_to_process) - 1:
                save_citations_cache(citations_cache)
                logger.info(f"Progress: {i+1}/{len(teachers_to_process)} (success={successful}, failed={failed})")
                
        except Exception as e:
            logger.error(f"Error processing teacher {teacher_id}: {str(e)}")
            failed += 1
    
    # Final save
    save_citations_cache(citations_cache)
    logger.info(f"Citations extraction completed: {successful} successful, {failed} failed out of {len(teachers_to_process)}")
    
    # Also persist successful extractions to the database
    try:
        import sys
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if backend_dir not in sys.path:
            sys.path.insert(0, backend_dir)
        import database
        
        # Build reverse mapping: JSON ID → DB PID
        # We need to load all professors from DB and map their Google Scholar URLs
        db_professors = database.load_professors_data()
        
        # Create mapping from google_scholar_url to DB PID
        url_to_db_id = {}
        for prof in db_professors:
            gs_url = prof.get('google_scholar_url', '')
            if gs_url:
                url_to_db_id[gs_url] = prof.get('id')
        
        # Also create mapping from JSON teacher ID → Google Scholar URL
        json_id_to_url = {}
        for teacher in teachers:
            tid = str(teacher.get('id', ''))
            gs_url = teacher.get('google_scholar_url', '')
            if tid and gs_url:
                json_id_to_url[tid] = gs_url
        
        db_updated = 0
        for json_id, data in citations_cache.items():
            if not data.get('extraction_success', False):
                continue
            citations = data.get('citations', 0)
            h_idx = data.get('h_index', 0)
            i10_idx = data.get('i10_index', 0)
            
            # Skip if all zeros
            if citations == 0 and h_idx == 0 and i10_idx == 0:
                continue
            
            # Find the DB PID for this JSON ID
            gs_url = json_id_to_url.get(json_id, '')
            db_pid = url_to_db_id.get(gs_url)
            
            if db_pid:
                result = database.update_professor_citations(db_pid, citations, h_idx, i10_idx)
                if result:
                    db_updated += 1
        
        logger.info(f"Updated {db_updated} professors in database with citation data")
        
    except Exception as e:
        logger.error(f"Error persisting citations to database: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
    
    return citations_cache

def get_cached_citations():
    """
    Get cached citations data (only successfully extracted entries)
    """
    return load_citations_cache()

# Track if extraction is currently running
_extraction_running = False
_extraction_thread = None
_extraction_start_time = 0

# Start extraction in a background thread
def start_background_extraction():
    """
    Start citation extraction in a background thread
    """
    global _extraction_running, _extraction_thread, _extraction_start_time
    
    # Check if extraction is already running
    if _extraction_running and _extraction_thread and _extraction_thread.is_alive():
        logger.info("Citation extraction already running, not starting new thread")
        return _extraction_thread
    
    logger.info("Starting background citation extraction")
    
    # Reset state
    _extraction_running = True
    _extraction_start_time = time.time()
    
    # Create and start thread
    def thread_wrapper():
        global _extraction_running
        try:
            logger.info("Starting citation extraction in thread")
            # Make sure extraction_running is set properly in the thread
            _extraction_running = True
            result = extract_and_cache_citations()
            logger.info(f"Extraction completed with {len(result) if result else 0} items in cache")
        except Exception as e:
            logger.error(f"Error in citation extraction thread: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
        finally:
            logger.info("Citation extraction thread finished")
            _extraction_running = False
    
    _extraction_thread = threading.Thread(target=thread_wrapper)
    _extraction_thread.daemon = True
    _extraction_thread.start()
    
    # Short delay to ensure the thread has started
    time.sleep(0.1)
    
    logger.info(f"Started citation extraction thread (daemon={_extraction_thread.daemon}, running={_extraction_running})")
    return _extraction_thread

def get_extraction_status():
    """
    Get status of the extraction process
    """
    global _extraction_running, _extraction_thread, _extraction_start_time
    
    # Check if thread is alive
    thread_alive = _extraction_thread is not None and _extraction_thread.is_alive()
    
    # If thread is not alive but running flag is still True, reset it
    if _extraction_running and not thread_alive:
        logger.warning("Extraction thread not alive but running flag is True. Resetting state.")
        _extraction_running = False
    
    running_time = time.time() - _extraction_start_time if _extraction_running else 0
    
    return {
        'running': _extraction_running,
        'alive': thread_alive,
        'start_time': _extraction_start_time,
        'running_time_seconds': running_time
    }

# Direct execution
if __name__ == "__main__":
    extract_and_cache_citations()
