"""
Core Package - Configuration and Utilities
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration"""
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_NAME = os.getenv('DB_NAME', 'prism_professors')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    
    OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'gemma3:4b')
    
    REQUEST_DELAY = int(os.getenv('REQUEST_DELAY', 5))
    PORT = int(os.getenv('PORT', 5000))


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
