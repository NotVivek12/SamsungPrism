"""
Direct test of citation extraction
"""
import os
import sys
import json
import logging
from extract_citations import extract_and_cache_citations, load_teachers_data, load_citations_cache

# Set up logging to console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('direct_test')

def test_extraction():
    """Test citation extraction directly"""
    
    logger.info("Current working directory: %s", os.getcwd())
    
    try:
        # Try to load teachers data
        teachers = load_teachers_data()
        logger.info(f"Loaded {len(teachers)} teachers")
        
        # Check if any have Google Scholar URLs
        gs_teachers = [t for t in teachers if t.get('google_scholar_url')]
        logger.info(f"Found {len(gs_teachers)} teachers with Google Scholar URLs")
        
        if gs_teachers:
            for i, teacher in enumerate(gs_teachers[:3]):
                logger.info(f"Teacher {i+1}: {teacher.get('name', 'Unknown')} - {teacher.get('google_scholar_url')}")
        
        # Run extraction directly
        logger.info("Starting citation extraction")
        result = extract_and_cache_citations()
        
        # Check cache
        cache = load_citations_cache()
        logger.info(f"Citation cache has {len(cache)} entries")
        
        # Show sample cache entries
        if cache:
            logger.info("Sample cache entries:")
            for teacher_id, data in list(cache.items())[:3]:
                logger.info(f"Teacher ID: {teacher_id}")
                logger.info(f"  Citations: {data.get('citations', 'N/A')}")
                logger.info(f"  h-index: {data.get('h_index', 'N/A')}")
                logger.info(f"  i10-index: {data.get('i10_index', 'N/A')}")
                logger.info(f"  timestamp: {data.get('timestamp', 'N/A')}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error in test: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    success = test_extraction()
    sys.exit(0 if success else 1)