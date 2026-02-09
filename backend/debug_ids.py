"""
Debug professor IDs and citation cache keys
"""
import json
import logging
from extract_citations import get_cached_citations, load_teachers_data
import database

# Set up logging to console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('debug_ids')

def debug_ids():
    """Debug professor IDs and citation cache keys"""
    
    # Get citation cache
    citations_cache = get_cached_citations()
    logger.info(f"Citation cache has {len(citations_cache)} entries")
    
    # Get sample cache keys
    cache_keys = list(citations_cache.keys())[:5]
    logger.info(f"Sample citation cache keys: {cache_keys}")
    
    # Get teachers from JSON file
    teachers_json = load_teachers_data()
    logger.info(f"Loaded {len(teachers_json)} teachers from JSON")
    
    # Get sample teacher IDs
    teacher_ids = [str(t.get('id', 'unknown')) for t in teachers_json[:5]]
    logger.info(f"Sample teacher IDs from JSON: {teacher_ids}")
    
    # Get professors from database
    professors_db = database.load_professors_data()
    logger.info(f"Loaded {len(professors_db)} professors from database")
    
    # Get sample professor IDs
    prof_ids = [str(p.get('id', 'unknown')) for p in professors_db[:5]]
    logger.info(f"Sample professor IDs from database: {prof_ids}")
    
    # Check ID overlap between cache and database
    prof_ids_set = set(str(p.get('id', '')) for p in professors_db)
    cache_keys_set = set(citations_cache.keys())
    
    common_ids = prof_ids_set.intersection(cache_keys_set)
    logger.info(f"Number of professors with matching cache entries: {len(common_ids)}")
    
    # Check a specific professor with high citations
    high_citations = sorted(
        [(k, v.get('citations', 0)) for k, v in citations_cache.items() if v.get('citations', 0) > 0],
        key=lambda x: x[1],
        reverse=True
    )[:5]
    
    logger.info("Top 5 professors by citation count:")
    for prof_id, citations in high_citations:
        # Find professor in database
        prof = next((p for p in professors_db if str(p.get('id', '')) == prof_id), None)
        if prof:
            logger.info(f"Professor {prof.get('name', 'Unknown')} (ID: {prof_id}): {citations} citations")
        else:
            logger.info(f"Professor with ID {prof_id} not found in database but has {citations} citations")

if __name__ == "__main__":
    debug_ids()