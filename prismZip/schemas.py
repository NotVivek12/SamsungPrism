from typing import List, Dict, Optional
from pydantic import BaseModel

class Publication(BaseModel):
    title: str
    year: str

class ScholarData(BaseModel):
    Teacher_Name: str
    Google_Scholar_URL: str
    citations: int
    h_index: int
    i10_index: int
    publications: List[Publication]
