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
    existing_narrators: List[str]
    missing_narrators: List[str]

class HadithOnlyResponse(BaseModel):
    hadith_content: str

class HadithAndNaratorsResponse(BaseModel):
    hadith_content: str
    narrators: List[str]

class HadithCompleteInfoResponse(BaseModel):
    hadith_content: str
    narrators: List[str]
    existing_narrators: List[str]
    missing_narrators: List[str]
    related_ayahs: List[AyahResult]
    keywords: Dict[str, Union[List[str], int]]

class ManualSearchOccurrence(BaseModel):
    arabic_text: str
    english_translation: str
    verse_reference: str

class ManualSearchResult(BaseModel):
    keyword_text: str
    meaning: str
    description: str
    total_occurrences: int
    occurrences: List[ManualSearchOccurrence]

class CompleteAnalysisAiAndManual(BaseModel):
    hadith_content: str
    narrators: List[str]
    existing_narrators: List[str]
    missing_narrators: List[str]
    found_keywords: List[str]
    manual_search_results: Dict[str, List[ManualSearchResult]]
    ai_search_results: Dict[str, List[AyahResult]]


class KeywordHighlightResponse(BaseModel):
    original_text: str
    highlighted_text: str
    found_keywords: List[str]
