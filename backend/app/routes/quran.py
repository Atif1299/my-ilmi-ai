from fastapi import APIRouter
from ..models.query import QueryRequest, QueryResponse , HadithOnlyResponse, HadithAndNaratorsResponse , NaratorsResponse, KeywordHighlightResponse, HadithCompleteInfoResponse, AyahResult
import os
from ..services.quran_services import validate_hadith
from ..rag.narators_hadith import extract_narrators_chain_with_llm
from typing import Dict
import string
import json
import re
router = APIRouter()

def highlight_keywords_in_text(text: str, keywords: list, highlight_tag: str = "**") -> str:
    """Highlight keywords in text using the specified highlight tag"""
    if not text or not keywords:
        return text
    
    highlighted_text = text
    for keyword in keywords:
        if keyword.lower() in text.lower():
            # Create a case-insensitive pattern
            pattern = re.compile(re.escape(keyword), re.IGNORECASE)
            highlighted_text = pattern.sub(f"{highlight_tag}{keyword}{highlight_tag}", highlighted_text)
    
    return highlighted_text

@router.post("/get_hadith_related_ayahs", response_model=QueryResponse)
async def search_ayahs(request: QueryRequest):
    """Search for related ayahs - ORIGINAL functionality without highlighting"""
    try:
        # Try the original function first - NO HIGHLIGHTING HERE
        return validate_hadith(request.query)
    except Exception as e:
        # Fallback to simple keyword search - NO HIGHLIGHTING
        try:
            from ..rag.bm25_engine import bm25_engine
            
            # Simple BM25 search without external dependencies
            keyword_hits = bm25_engine.search(request.query, top_n=15)
            
            # Load Quran metadata 
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            metadata_path = os.path.join(BASE_DIR, "..", "quran_metadata.json")
            
            with open(metadata_path, "r", encoding="utf-8") as f:
                quran_metadata = json.load(f)
            
            # Create ayah mapping
            ayah_map = {}
            for ayah in quran_metadata:
                clean_text = ayah["english_translation"].strip().lower().translate(str.maketrans("", "", string.punctuation))
                ayah_map[clean_text] = ayah
            
            results = []
            for hit in keyword_hits:
                clean_hit = hit["text"].strip().lower().translate(str.maketrans("", "", string.punctuation))
                if clean_hit in ayah_map:
                    ayah = ayah_map[clean_hit]
                    
                    # NO HIGHLIGHTING - keep original English translation
                    results.append({
                        "score": hit["score"],
                        "english_translation": ayah["english_translation"],  # Original, no highlighting
                        "surah_name_english": ayah["surah_name_english"], 
                        "aya_number": ayah["aya_number"],
                        "arabic_diacritics": ayah.get("arabic_diacritics", "")
                    })
            
            from ..models.query import QueryResponse, AyahResult
            ayah_results = [
                AyahResult(
                    score=r["score"],
                    english_translation=r["english_translation"],
                    surah_name_english=r["surah_name_english"],
                    aya_number=r["aya_number"],
                    arabic_diacritics=r["arabic_diacritics"]
                ) for r in results[:5]
            ]
            
            return QueryResponse(results=ayah_results)
        except Exception as fallback_error:
            # Return empty result with error info
            from ..models.query import QueryResponse
            return QueryResponse(results=[])


@router.post('/get_hadith_narators', response_model=NaratorsResponse)
async def extract_narators(request: QueryRequest):
    try:
        narators, _ = extract_narrators_chain_with_llm(request.query)
        if not narators or len(narators) == 0 or narators == []:
            # LLM didn't work, use manual extraction
            narators, _ = extract_narrators_manually(request.query)
        return {"narrators": narators}
    except Exception as e:
        # Fallback to manual extraction
        try:
            narators, _ = extract_narrators_manually(request.query)
            return {"narrators": narators}
        except:
            return {"narrators": []}


@router.post('/get_hadith_content', response_model=HadithOnlyResponse)
async def extract_hadith_content(request: QueryRequest):
    try:
        _, content = extract_narrators_chain_with_llm(request.query)
        if not content or content.strip() == "" or content == request.query:
            # LLM didn't work, use manual extraction
            _, content = extract_narrators_manually(request.query)
        return {"hadith_content": content}
    except Exception as e:
        # Fallback to manual extraction
        try:
            _, content = extract_narrators_manually(request.query)
            return {"hadith_content": content}
        except:
            return {"hadith_content": request.query}
    except Exception as e:
        # Fallback to manual extraction
        try:
            _, content = extract_narrators_manually(request.query)
            return {"hadith_content": content}
        except:
            return {"hadith_content": request.query}


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@router.post("/keyword_search", response_model=Dict)
async def keyword_search(request: QueryRequest):
    """Enhanced keyword search that finds variations of keywords"""
    try:
        from ..rag.bm25_engine import bm25_engine
        
        query = request.query.lower()
        
        # Use the new variation search method
        keyword_hits = bm25_engine.search_with_variations(query, top_n=30)
        
        # Load Quran metadata to get proper ayah info
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        metadata_path = os.path.join(BASE_DIR, "..", "quran_metadata.json")
        
        with open(metadata_path, "r", encoding="utf-8") as f:
            quran_metadata = json.load(f)
        
        # Create a mapping for faster lookup
        ayah_map = {}
        for ayah in quran_metadata:
            clean_text = ayah["english_translation"].strip().lower().translate(str.maketrans("", "", string.punctuation))
            ayah_map[clean_text] = ayah
        
        # Extract search keywords for highlighting
        search_keywords = [word.strip() for word in request.query.lower().split() if word.strip()]
        
        results = []
        for hit in keyword_hits:
            clean_hit = hit["text"].strip().lower().translate(str.maketrans("", "", string.punctuation))
            if clean_hit in ayah_map:
                ayah = ayah_map[clean_hit]
                
                # Highlight keywords in the English translation
                highlighted_english = highlight_keywords_in_text(
                    ayah["english_translation"], 
                    search_keywords
                )
                
                results.append({
                    "english_translation": highlighted_english,
                    "surah_name_english": ayah["surah_name_english"], 
                    "aya_number": ayah["aya_number"],
                    "arabic_diacritics": ayah.get("arabic_diacritics", ""),
                    "score": hit["score"]
                })
        
        return {
            "query": query,
            "matched_ayats": results[:20],
            "total_matches": len(results)
        }
    except Exception as e:
        return {
            "query": request.query,
            "error": str(e),
            "matched_ayats": [],
            "total_matches": 0
        }


def extract_narrators_manually(hadith_text: str):
    """
    Manual fallback for narrator extraction using common patterns
    """
    try:
        # Common hadith patterns
        patterns = [
            r'It was narrated from (.+?) that (.+)',
            r'(.+?) narrated that (.+)',
            r'On the authority of (.+?) that (.+)',
            r'From (.+?) that (.+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, hadith_text, re.IGNORECASE)
            if match:
                narrator_chain = match.group(1)
                content = match.group(2)
                
                # Extract individual narrators from the chain
                # Split by common separators
                narrators = []
                if narrator_chain:
                    # Split by "from", "," and clean up
                    parts = re.split(r',\s*from\s*|,\s*|\s*from\s*', narrator_chain)
                    for part in parts:
                        part = part.strip(' ",')
                        if part and len(part) > 1:
                            narrators.append(part)
                
                return narrators, content.strip()
        
        # If no pattern matches, return empty narrators and original text
        return [], hadith_text
        
    except Exception as e:
        return [], hadith_text

@router.post("/get_hadith_complete_info", response_model=HadithCompleteInfoResponse)
async def get_hadith_complete_info(request: QueryRequest):
    """
    Complete Analysis: Call individual working functions directly
    """
    # Step 1: Extract narrators and content with fallback
    try:
        narrator_result = await extract_narators(request)
        narrators = narrator_result.narrators
        
        # If no narrators found with LLM, try manual extraction
        if not narrators or len(narrators) == 0:
            manual_narrators, manual_content = extract_narrators_manually(request.query)
            narrators = manual_narrators
            content = manual_content
        else:
            # Get content from the other endpoint
            try:
                content_result = await extract_hadith_content(request)
                content = content_result.hadith_content
            except:
                # If content extraction fails, try manual extraction
                _, manual_content = extract_narrators_manually(request.query)
                content = manual_content
                
    except Exception as e:
        # Fallback to manual extraction
        narrators, content = extract_narrators_manually(request.query)
    
    # Step 2: Find related ayahs using extracted content
    try:
        search_request = QueryRequest(query=content if content != request.query else request.query)
        related_ayahs_result = await search_ayahs(search_request)
        related_ayahs = related_ayahs_result.results
    except:
        related_ayahs = []
    
    # Step 3: Highlight keywords in the ayahs
    highlighted_ayahs = []
    all_found_keywords = []
    
    try:
        # Load keywords from database
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        keywords_path = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "Storage", "english_keywords_array.json"))
        
        with open(keywords_path, "r", encoding="utf-8") as f:
            keywords_list = json.load(f)
        
        keywords_sorted = sorted(keywords_list, key=len, reverse=True)
        
        for ayah in related_ayahs:
            highlighted_english = ayah.english_translation
            
            for keyword in keywords_sorted:
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, highlighted_english, re.IGNORECASE):
                    if keyword.lower() not in [k.lower() for k in all_found_keywords]:
                        all_found_keywords.append(keyword)
                
                highlighted_english = re.sub(
                    pattern, 
                    f'**{keyword}**', 
                    highlighted_english, 
                    flags=re.IGNORECASE
                )
            
            highlighted_ayah = AyahResult(
                score=ayah.score,
                english_translation=highlighted_english,
                surah_name_english=ayah.surah_name_english,
                aya_number=ayah.aya_number,
                arabic_diacritics=ayah.arabic_diacritics
            )
            highlighted_ayahs.append(highlighted_ayah)
            
    except Exception as e:
        # Fallback: use original ayahs without highlighting
        highlighted_ayahs = related_ayahs
        all_found_keywords = []
    
    return {
        "hadith_content": content,
        "narrators": narrators,
        "related_ayahs": highlighted_ayahs,
        "keywords": {
            "found_keywords": all_found_keywords,
            "total_keywords_found": len(all_found_keywords)
        }
    }


@router.post("/highlight_keywords", response_model=KeywordHighlightResponse)
async def highlight_keywords(request: QueryRequest):
    """
    Highlight keywords in the input text that match the keywords from english_keywords_array.json
    """
    # Load keywords from the json file
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    keywords_path = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "Storage", "english_keywords_array.json"))
    
    try:
        with open(keywords_path, "r", encoding="utf-8") as f:
            keywords_list = json.load(f)
    except FileNotFoundError:
        return {
            "original_text": request.query,
            "highlighted_text": request.query,
            "found_keywords": []
        }
    
    # Convert keywords to lowercase for case-insensitive matching
    keywords_lower = [keyword.lower() for keyword in keywords_list]
    
    # Find matching keywords in the input text
    input_text = request.query
    found_keywords = []
    highlighted_text = input_text
    
    # Sort keywords by length (longest first) to avoid partial replacements
    keywords_sorted = sorted(keywords_list, key=len, reverse=True)
    
    for keyword in keywords_sorted:
        # Case-insensitive search for whole words
        pattern = r'\b' + re.escape(keyword) + r'\b'
        matches = re.finditer(pattern, input_text, re.IGNORECASE)
        
        for match in matches:
            if keyword.lower() not in [k.lower() for k in found_keywords]:
                found_keywords.append(keyword)
        
        # Replace with highlighted version
        highlighted_text = re.sub(
            pattern, 
            f'<mark style="background-color: #ffeb3b; padding: 2px 4px; border-radius: 3px;">{keyword}</mark>', 
            highlighted_text, 
            flags=re.IGNORECASE
        )
    
    return {
        "original_text": input_text,
        "highlighted_text": highlighted_text,
        "found_keywords": found_keywords
    }
