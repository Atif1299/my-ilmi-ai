from fastapi import APIRouter, HTTPException
from app.models.query import QueryRequest, CompleteAnalysisAiAndManual, AyahResult, ManualSearchResult, ManualSearchOccurrence
from app.rag.narators_hadith import extract_narrators_chain_with_llm
from app.routes.quran import extract_narators, extract_hadith_content, extract_narrators_manually, narratorsobj
from app.rag.bm25_engine import bm25_engine
import os
import json
import re
from typing import List, Dict
import string

router = APIRouter()

# Global cache for dictionary data
all_keywords_data = []

def load_all_dictionary_data():
    global all_keywords_data
    if all_keywords_data:
        return all_keywords_data

    dictionary_path = os.path.join(os.path.dirname(__file__), "..", "..", "Storage", "Quran Dictionary With English Translation")
    dictionary_files = [f for f in os.listdir(dictionary_path) if f.endswith('.json')]
    
    loaded_data = []
    for file_name in dictionary_files:
        file_path = os.path.join(dictionary_path, file_name)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    loaded_data.extend(data)
        except Exception as e:
            print(f"Error loading dictionary file {file_name}: {e}")
            
    all_keywords_data = loaded_data
    return all_keywords_data

@router.post("/complete-analysis/", response_model=CompleteAnalysisAiAndManual)
async def get_complete_analysis(request: dict):
    hadith_text = request.get("hadith_text")
    if not hadith_text:
        raise HTTPException(status_code=400, detail="hadith_text is required")

    query_request = QueryRequest(query=hadith_text)

    # Step 1: Try direct LLM chain first
    try:
        narrators, content = extract_narrators_chain_with_llm(query_request.query)
    except Exception:
        narrators, content = [], ""

    # Step 2: If LLM chain fails → fallback to previous logic
    if not narrators or not content or content.strip() == "" or content.strip() == query_request.query.strip():
        try:
            narrator_result = await extract_narators(query_request)
            narrators = narrator_result.narrators

            if not narrators or len(narrators) == 0:
                manual_narrators, manual_content = extract_narrators_manually(query_request.query)
                narrators = manual_narrators
                content = manual_content
            else:
                try:
                    content_result = await extract_hadith_content(query_request)
                    content = content_result.hadith_content
                except:
                    _, manual_content = extract_narrators_manually(query_request.query)
                    content = manual_content
        except:
            narrators, content = extract_narrators_manually(query_request.query)

    # Find Narrators that are not present in DB...
    existing_narrators_db = [obj["nameEnglish"] for obj in narratorsobj]
    existing_narrators = [n for n in narrators if n in existing_narrators_db]
    missing_narrators = [n for n in narrators if n not in existing_narrators_db]
    
    if missing_narrators:
        print(f"Missing narrators found in complete info: {missing_narrators}")

    # Step 3: Find keywords in the extracted content
    found_keywords = []
    try:
        keywords_path = os.path.join(os.path.dirname(__file__), "..", "..", "Storage", "english_keywords_array.json")
        
        with open(keywords_path, "r", encoding="utf-8") as f:
            keywords_list = json.load(f)
        
        keywords_sorted = sorted(keywords_list, key=len, reverse=True)
        
        for keyword in keywords_sorted:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, content, re.IGNORECASE):
                if keyword.lower() not in [k.lower() for k in found_keywords]:
                    found_keywords.append(keyword)
    except Exception as e:
        print(f"Error finding keywords: {e}")

    # Step 4: Perform manual search for each found keyword
    manual_search_results = {}
    dictionary_data = load_all_dictionary_data()

    for keyword in found_keywords:
        pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
        matching_keywords = [
            item for item in dictionary_data 
            if item.get("meaning") and re.search(pattern, item["meaning"].lower())
        ]
        
        if not matching_keywords:
            manual_search_results[keyword] = []
            continue

        # Aggregate all occurrences from matching keywords
        all_occurrences = []
        total_occurrences = 0
        for item in matching_keywords:
            all_occurrences.extend(item.get("occurrences", []))
            total_occurrences += item.get("total_occurrences", 0)

        results_for_keyword = []
        for item in matching_keywords:
            occurrences = [
                ManualSearchOccurrence(
                    arabic_text=occ.get("arabic_text", ""),
                    english_translation=occ.get("english_translation", ""),
                    verse_reference=occ.get("verse_reference", {}).get("reference", "")
                ) for occ in item.get("occurrences", [])
            ]
            
            manual_result = ManualSearchResult(
                keyword_text=item.get("keyword_text", ""),
                meaning=item.get("meaning", ""),
                description=item.get("description", ""),
                total_occurrences=item.get("total_occurrences", 0),
                occurrences=occurrences
            )
            results_for_keyword.append(manual_result)
        
        manual_search_results[keyword] = results_for_keyword
    
     # Step 5: Perform AI search for each found keyword
    ai_search_results = {}
    metadata_path = os.path.join(os.path.dirname(__file__), "..", "quran_metadata.json")
    with open(metadata_path, "r", encoding="utf-8") as f:
        quran_metadata = json.load(f)
    ayah_map = {}
    for ayah in quran_metadata:
        clean_text = ayah["english_translation"].strip().lower().translate(str.maketrans("", "", string.punctuation))
        ayah_map[clean_text] = ayah

    for keyword in found_keywords:
        keyword_hits = bm25_engine.search(keyword, top_n=15)
        results = []
        for hit in keyword_hits:
            clean_hit = hit["text"].strip().lower().translate(str.maketrans("", "", string.punctuation))
            if clean_hit in ayah_map:
                ayah = ayah_map[clean_hit]
                results.append({
                    "score": hit["score"],
                    "english_translation": ayah["english_translation"],
                    "surah_name_english": ayah["surah_name_english"],
                    "aya_number": ayah["aya_number"],
                    "arabic_diacritics": ayah.get("arabic_diacritics", "")
                })
        ai_search_results[keyword] = [AyahResult(**r) for r in results]


    # Mock data for demonstration
    analysis_result = CompleteAnalysisAiAndManual(
        hadith_content=content,
        narrators=narrators,
        existing_narrators=existing_narrators,
        missing_narrators=missing_narrators,
        found_keywords=found_keywords,
        manual_search_results=manual_search_results,
        ai_search_results=ai_search_results
    )

    return analysis_result
