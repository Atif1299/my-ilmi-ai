from pydantic import BaseModel
from typing import List, Dict, Union

class AyahResult(BaseModel):
    score: float
    english_translation: str
    surah_name_english: str
    aya_number: int
    arabic_diacritics: str

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    results: List[AyahResult]

class NaratorsResponse(BaseModel):
    narrators: List[str]

class HadithOnlyResponse(BaseModel):
    hadith_content: str

class HadithAndNaratorsResponse(BaseModel):
    hadith_content: str
    narrators: List[str]

class HadithCompleteInfoResponse(BaseModel):
    hadith_content: str
    narrators: List[str]
    related_ayahs: List[AyahResult]
    keywords: Dict[str, Union[List[str], int]]

class KeywordHighlightResponse(BaseModel):
    original_text: str
    highlighted_text: str
    found_keywords: List[str]
