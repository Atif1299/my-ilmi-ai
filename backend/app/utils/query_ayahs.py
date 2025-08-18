import os
import numpy as np
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from qdrant_client import QdrantClient
from typing import List
from ..models.query import AyahResult
import json
import string
from collections import defaultdict
load_dotenv()

embedding_client = OpenAIEmbeddings(
    model="text-embedding-ada-002",
    openai_api_key=os.getenv("OPENAI_API_KEY")
);


def get_embedding(text):
    try:
        embedding = embedding_client.embed_query(text)
        return list(np.array(embedding, dtype=np.float32))
    except Exception as e:
        print("Error while getting embedding:", e)
        return None



def get_qdrant_client():
    return QdrantClient(
        url=os.getenv("QDRANT_URL", "http://localhost:6333"),
        api_key=os.getenv("QDRANT_API_KEY"),
        prefer_grpc=False,
        timeout=30.0
    )


def search_ayahs(query_vector: List[float], limit: int = 15) -> List[AyahResult]:
    client = get_qdrant_client()
    search_response = client.search(
        collection_name="quran_embeddings",
        query_vector=query_vector,
        limit=limit
    )
    return [
        AyahResult(
            score=hit.score,
            english_translation=hit.payload["english_translation"],
            surah_name_english=hit.payload["surah_name_english"],
            aya_number=hit.payload["aya_number"],
            arabic_diacritics=hit.payload.get("arabic_diacritics", "")
        )
        for hit in search_response
    ]


def preprocess_text(text: str) -> str:
    """Lowercase and remove punctuation from a string."""
    return text.strip().lower().translate(str.maketrans("", "", string.punctuation))


def map_bm25_hits_to_ayahs(keyword_hits: list[dict]) -> list[AyahResult]:
    """Map BM25 keyword hits to actual AyahResult objects using Quran metadata with preprocessing match."""
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    metadata_path = os.path.join(BASE_DIR, "..", "quran_metadata.json")
    metadata_path = os.path.abspath(metadata_path)

    with open(metadata_path, "r", encoding="utf-8") as f:
        quran_metadata = json.load(f)

    # Preprocess ayah translations once
    processed_ayah_map = {
        preprocess_text(ayah["english_translation"]): ayah
        for ayah in quran_metadata
    }

    results = []
    for hit in keyword_hits:
        cleaned_hit_text = preprocess_text(hit["text"])
        if cleaned_hit_text in processed_ayah_map:
            ayah = processed_ayah_map[cleaned_hit_text]
            results.append(
                AyahResult(
                    score=float(hit["score"]),
                    english_translation=ayah["english_translation"],
                    surah_name_english=ayah["surah_name_english"],
                    aya_number=ayah["aya_number"],
                    arabic_diacritics=ayah.get("arabic_diacritics", "")
                )
            )

    return results




def rrf_fusion(semantic_ayahs, bm25_ayahs, k=60):
    scores = defaultdict(float)

    for rank, ayah in enumerate(semantic_ayahs, start=1):
        ayah_key = f"{ayah.surah_name_english}:{ayah.aya_number}"
        scores[ayah_key] += 1 / (k + rank)

    for rank, ayah in enumerate(bm25_ayahs, start=1):
        ayah_key = f"{ayah.surah_name_english}:{ayah.aya_number}"
        scores[ayah_key] += 1 / (k + rank)

    ayah_dict = {f"{ayah.surah_name_english}:{ayah.aya_number}": ayah for ayah in semantic_ayahs + bm25_ayahs}
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [ayah_dict[key] for key, _ in ranked]


def get_openai_embedding(text: str) -> List[float]:
    embedding = embedding_client.embed_query(text)
    return embedding

def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    v1 = np.array(vec1)
    v2 = np.array(vec2)
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def deduplicate_ayahs_by_embedding(ayahs: List[AyahResult], threshold: float = 0.95) -> List[AyahResult]:
    unique_ayahs = []
    seen_embeddings = []

    for ayah in ayahs:
        emb = get_openai_embedding(ayah.english_translation)
        is_duplicate = False

        for existing_emb in seen_embeddings:
            sim = cosine_similarity(emb, existing_emb)
            if sim > threshold:
                is_duplicate = True
                break

        if not is_duplicate:
            unique_ayahs.append(ayah)
            seen_embeddings.append(emb)

    return unique_ayahs
