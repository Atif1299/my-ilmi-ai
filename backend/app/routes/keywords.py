from fastapi import APIRouter
import json
import os
from typing import Dict, List

router = APIRouter()

def load_keywords_data() -> Dict[str, List[str]]:
    """Load all three keyword JSON files"""
    # Use relative path to the keywords directory
    keywords_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "Storage", "Keywords"))
    print(f"Looking for keywords in: {keywords_dir}")
    
    files = {
        "english": "collected_meanings_english.json",
        "urdu": "collected_meanings_urdu.json", 
        "arabic": "collected_meanings_arabic.json"
    }
    
    data = {}
    for lang, filename in files.items():
        file_path = os.path.join(keywords_dir, filename)
        print(f"Trying to load: {file_path}")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data[lang] = json.load(f)
                print(f"Loaded {lang}: {len(data[lang])} items")
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            data[lang] = []
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            data[lang] = []
    
    return data

@router.get("/keywords")
async def get_all_keywords():
    """Get all keywords from all three JSON files"""
    return load_keywords_data()

@router.get("/keywords/{language}")
async def get_keywords_by_language(language: str):
    """Get keywords for a specific language"""
    data = load_keywords_data()
    if language not in data:
        return {"error": f"Language '{language}' not found"}
    return {"language": language, "keywords": data[language]}

@router.get("/keywords/search/{query}")
async def search_keywords(query: str, language: str = "all"):
    """Search keywords across languages"""
    data = load_keywords_data()
    results = {}
    
    query_lower = query.lower()
    
    if language == "all":
        for lang, keywords in data.items():
            matching = [kw for kw in keywords if query_lower in kw.lower()]
            if matching:
                results[lang] = matching
    else:
        if language in data:
            matching = [kw for kw in data[language] if query_lower in kw.lower()]
            results[language] = matching
    
    return results
