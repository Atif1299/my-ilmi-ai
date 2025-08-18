"""
Query utilities for the Hadith database
"""
from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy import and_, or_, func
from database_config import engine
from hadith_models import Book, Hadith
import json

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class HadithQueryManager:
    """Class to handle queries on the Hadith database"""
    
    def __init__(self):
        self.session = SessionLocal()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()
    
    def get_all_books(self):
        """Get all books ordered by book number"""
        return self.session.query(Book).order_by(Book.book_number).all()
    
    def get_all_books_with_counts(self):
        """Get all books with hadith count"""
        books = self.session.query(Book).order_by(Book.book_number).all()
        result = []
        for book in books:
            hadith_count = self.session.query(Hadith).filter(Hadith.book_id == book.id).count()
            result.append({
                'book_number': book.book_number,
                'english_name': book.english_name,
                'arabic_name': book.arabic_name,
                'hadith_count': hadith_count
            })
        return result
    
    def get_book_by_number(self, book_number: str):
        """Get a specific book by its number"""
        return self.session.query(Book).filter(Book.book_number == book_number).first()
    
    def get_hadiths_by_book(self, book_number: str, limit: int = None):
        """Get all hadiths from a specific book"""
        book = self.get_book_by_number(book_number)
        if not book:
            return []
        
        query = self.session.query(Hadith).options(joinedload(Hadith.book)).filter(Hadith.book_id == book.id)
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def search_hadiths_by_text(self, search_term: str, language: str = 'english', limit: int = 10):
        """Search hadiths by text content"""
        if language == 'english':
            query = self.session.query(Hadith).options(joinedload(Hadith.book)).filter(
                Hadith.english_text.ilike(f'%{search_term}%')
            )
        elif language == 'arabic':
            query = self.session.query(Hadith).options(joinedload(Hadith.book)).filter(
                Hadith.arabic_text.ilike(f'%{search_term}%')
            )
        else:  # Both
            query = self.session.query(Hadith).options(joinedload(Hadith.book)).filter(
                or_(
                    Hadith.english_text.ilike(f'%{search_term}%'),
                    Hadith.arabic_text.ilike(f'%{search_term}%')
                )
            )
        
        return query.limit(limit).all()
    
    def get_hadiths_with_narrators(self, limit: int = 10):
        """Get hadiths that have narrator information"""
        return self.session.query(Hadith).filter(
            Hadith.narrators.isnot(None)
        ).limit(limit).all()
    
    def get_random_hadith(self):
        """Get a random hadith"""
        return self.session.query(Hadith).order_by(func.random()).first()
    
    def get_database_stats(self):
        """Get comprehensive database statistics"""
        total_books = self.session.query(Book).count()
        total_hadiths = self.session.query(Hadith).count()
        hadiths_with_narrators = self.session.query(Hadith).filter(
            Hadith.narrators.isnot(None)
        ).count()
        
        return {
            'total_books': total_books,
            'total_hadiths': total_hadiths,
            'hadiths_with_narrators': hadiths_with_narrators,
            'hadiths_without_narrators': total_hadiths - hadiths_with_narrators
        }
    
    def get_total_hadith_count(self):
        """Get total number of hadiths"""
        return self.session.query(Hadith).count()
    
    def get_hadith_count_by_book(self, book_number: str):
        """Get number of hadiths in a specific book"""
        book = self.get_book_by_number(book_number)
        if not book:
            return 0
        return self.session.query(Hadith).filter(Hadith.book_id == book.id).count()
    
    def get_hadith_by_id(self, hadith_id: int):
        """Get a specific hadith by ID"""
        return self.session.query(Hadith).options(joinedload(Hadith.book)).filter(Hadith.id == hadith_id).first()
    
    def search_hadiths_by_narrator(self, narrator_name: str, limit: int = 10):
        """Search hadiths by narrator name"""
        return self.session.query(Hadith).options(joinedload(Hadith.book)).filter(
            Hadith.english_text.ilike(f'%{narrator_name}%')
        ).limit(limit).all()

def main():
    """Example usage of the query manager"""
    with HadithQueryManager() as hqm:
        # Get database stats
        stats = hqm.get_database_stats()
        print("📊 Database Statistics:")
        print(f"  📚 Total Books: {stats['total_books']}")
        print(f"  📜 Total Hadiths: {stats['total_hadiths']}")
        print(f"  👥 With Narrators: {stats['hadiths_with_narrators']}")
        print(f"  ❓ Without Narrators: {stats['hadiths_without_narrators']}")
        
        # Get all books
        print("\n📖 Available Books:")
        books = hqm.get_all_books_with_counts()
        for book in books:
            print(f"  Book {book['book_number']}: {book['english_name']} ({book['hadith_count']} hadiths)")
        
        # Search example
        print("\n🔍 Search Example (prayer):")
        search_results = hqm.search_hadiths_by_text("prayer", limit=3)
        for hadith in search_results:
            print(f"  - Book {hadith.book.book_number}: {hadith.english_text[:100]}...")
        
        # Random hadith
        print("\n🎲 Random Hadith:")
        random_hadith = hqm.get_random_hadith()
        if random_hadith:
            print(f"  Book {random_hadith.book.book_number}: {random_hadith.english_text[:150]}...")

if __name__ == "__main__":
    main()
