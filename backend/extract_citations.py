"""
Extract citations for all teachers with Google Scholar URLs and cache them
"""
import os
import json
import time
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
CACHE_FILE = 'teacher_citations_cache.json'
CACHE_EXPIRY = 86400  # 24 hours in seconds

def extract_citations(url):
    """
    Extract only the citations count from a Google Scholar profile URL
    
    Args:
        url: Google Scholar profile URL
        
    Returns:
        Dictionary with citations count or None if extraction failed
    """
    try:
        # Use a browser-like user agent to avoid being blocked
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Fetch the HTML content
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            logger.warning(f"Failed to fetch Google Scholar profile: Status code {response.status_code}")
            return None
            
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
        
        return {
            'citations': total_citations,
            'h_index': h_index,
            'i10_index': i10_index
        }
        
    except Exception as e:
        logger.error(f"Error extracting citations: {str(e)}")
        return None

def load_teachers_data():
    """
    Load teachers data from JSON file or database
    """
    try:
        # Try to load from teachers_data.json
        try:
            with open('teachers_data.json', 'r', encoding='utf-8') as f:
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
            logger.warning(f"Could not load from teachers_data.json: {str(e)}")
            # If file not found, try to import from database module
            try:
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
            # Check if cache file is still valid
            if time.time() - os.path.getmtime(CACHE_FILE) < CACHE_EXPIRY:
                with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
        return {}
    except Exception as e:
        logger.error(f"Error loading citations cache: {str(e)}")
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
    
    # Load existing cache
    citations_cache = load_citations_cache()
    
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
        
        # Skip if already cached and not expired
        if teacher_id in citations_cache and 'timestamp' in citations_cache[teacher_id]:
            cache_age = time.time() - citations_cache[teacher_id]['timestamp']
            if cache_age < CACHE_EXPIRY and citations_cache[teacher_id].get('citations') is not None:
                continue
        
        teachers_to_process.append((teacher_id, gs_url))
    
    logger.info(f"Need to extract citations for {len(teachers_to_process)} teachers")
    
    # Extract citations in parallel with a thread pool
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_teacher = {
            executor.submit(extract_citations, gs_url): (teacher_id, gs_url)
            for teacher_id, gs_url in teachers_to_process
        }
        
        for i, future in enumerate(concurrent.futures.as_completed(future_to_teacher)):
            teacher_id, gs_url = future_to_teacher[future]
            
            try:
                citation_data = future.result()
                if citation_data:
                    # Store in cache with timestamp
                    citations_cache[teacher_id] = {
                        'citations': citation_data.get('citations', 0),
                        'h_index': citation_data.get('h_index', 0),
                        'i10_index': citation_data.get('i10_index', 0),
                        'timestamp': time.time()
                    }
                    logger.info(f"Extracted citations for teacher {teacher_id}: {citation_data}")
                else:
                    # Store empty data with timestamp to avoid repeated failed attempts
                    citations_cache[teacher_id] = {
                        'citations': 0,
                        'h_index': 0,
                        'i10_index': 0,
                        'timestamp': time.time()
                    }
                    logger.warning(f"Failed to extract citations for teacher {teacher_id}")
                
                # Save cache periodically (every 10 teachers)
                if (i + 1) % 10 == 0 or i == len(teachers_to_process) - 1:
                    save_citations_cache(citations_cache)
                    logger.info(f"Progress: {i+1}/{len(teachers_to_process)} ({((i+1)/len(teachers_to_process))*100:.1f}%)")
                
            except Exception as e:
                logger.error(f"Error processing teacher {teacher_id}: {str(e)}")
    
    # Final save
    save_citations_cache(citations_cache)
    logger.info("Citations extraction completed")
    
    return citations_cache

def get_cached_citations():
    """
    Get cached citations data
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
