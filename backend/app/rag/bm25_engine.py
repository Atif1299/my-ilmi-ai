import os
from rank_bm25 import BM25Okapi

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
corpus_path = os.path.join(BASE_DIR, "..", "quran_cleaned_corpus.txt")
corpus_path = os.path.abspath(corpus_path)

class BM25Search:
    def __init__(self, file_path=corpus_path):
        with open(file_path, "r", encoding="utf-8") as f:
            self.documents = [line.strip().split() for line in f]
        self.bm25 = BM25Okapi(self.documents)

    def search(self, query: str, top_n=15):
        tokenized_query = query.lower().split()
        scores = self.bm25.get_scores(tokenized_query)
        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
        return [{"text": " ".join(self.documents[i]), "score": score} for i, score in ranked[:top_n]]
    
    def search_with_variations(self, query: str, top_n=15):
        """Search for ayats containing any variation/substring of the keyword"""
        tokenized_query = query.lower().split()
        results = []
        
        for i, document in enumerate(self.documents):
            ayah_text = " ".join(document).lower()
            # Check if any query word is a substring of any word in the ayah
            matches = 0
            for query_word in tokenized_query:
                for ayah_word in document:
                    if query_word in ayah_word.lower():
                        matches += 1
                        break
            
            if matches > 0:
                # Calculate a simple score based on matches
                score = matches / len(tokenized_query)
                results.append({"text": " ".join(document), "score": score})
        
        # Sort by score (descending) and return top results
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_n]

bm25_engine = BM25Search(corpus_path)
