import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DEBUG = os.getenv("DEBUG", False)
    PORT = int(os.getenv("PORT", 5000))
    REQUEST_DELAY = int(os.getenv("REQUEST_DELAY", 5))
