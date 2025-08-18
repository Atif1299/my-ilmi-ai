from ..models.query import QueryResponse
from ..utils.query_ayahs import get_embedding, search_ayahs,map_bm25_hits_to_ayahs
from ..utils.get_hadith import extract_narrators_chain_with_llm
from ..rag.ayah_filter import filter_relevant_ayahs, score_all_ayahs_with_gpt
from ..rag.bm25_engine import bm25_engine
from ..utils.query_ayahs import rrf_fusion, deduplicate_ayahs_by_embedding

def validate_hadith(query: str):
    narrators , query = extract_narrators_chain_with_llm(query)
    query_vector = get_embedding(query)

    semantic_ayahs = search_ayahs(query_vector=query_vector, limit=15)
    filtered_semantic_ayahs = filter_relevant_ayahs(ayahs=semantic_ayahs, hadith_text=query)

    keyword_hits = bm25_engine.search(query, top_n=15)
    bm25_results = map_bm25_hits_to_ayahs(keyword_hits)
    filtered_bm25_ayahs = filter_relevant_ayahs(ayahs=bm25_results, hadith_text=query)

    hybrid_results = rrf_fusion(filtered_semantic_ayahs, filtered_bm25_ayahs)
    hybrid_results = deduplicate_ayahs_by_embedding(hybrid_results)

    result = score_all_ayahs_with_gpt(hadith_text=query , ayahs=hybrid_results)
    return QueryResponse(results=result[:5])
