"""
Script to import all Muwatta Malik JSON files into PostgreSQL database
"""
import json
import os
import glob
from typing import List, Dict, Any
from database_config import engine, SessionLocal, Base
from hadith_models import Book, Hadith

def create_tables():
    """Create database tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")

def load_json_file(file_path: str) -> Dict[str, Any]:
    """Load JSON file and return data"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading {file_path}: {e}")
        return None

def import_book_to_db(book_data: Dict[str, Any], db_session) -> bool:
    """Import a single book and its hadiths to database"""
    try:
        # Check if book already exists
        existing_book = db_session.query(Book).filter(
            Book.book_number == book_data.get("book_number")
        ).first()
        
        if existing_book:
            print(f"⚠️ Book {book_data.get('book_number')} already exists. Skipping...")
            return True
        
        # Create book record
        book = Book(
            book_number=book_data.get("book_number"),
            english_name=book_data.get("english_name"),
            arabic_name=book_data.get("arabic_name")
        )
        
        db_session.add(book)
        db_session.commit()
        db_session.refresh(book)
        
        print(f"📚 Created book: {book.english_name} (Book {book.book_number})")
        
        # Import hadiths
        hadiths_data = book_data.get("hadiths", [])
        hadith_count = 0
        
        for hadith_data in hadiths_data:
            hadith = Hadith(
                book_id=book.id,
                english_text=hadith_data.get("english", ""),
                arabic_text=hadith_data.get("arabic", ""),
                references=hadith_data.get("references", {}),
                narrators=hadith_data.get("narrators"),  # May be None
                content=hadith_data.get("content")       # May be None
            )
            
            db_session.add(hadith)
            hadith_count += 1
        
        db_session.commit()
        print(f"✅ Imported {hadith_count} hadiths for book {book.book_number}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error importing book {book_data.get('book_number', 'unknown')}: {e}")
        db_session.rollback()
        return False

def import_all_books():
    """Import all JSON books from Muwatta Malik directory"""
    # Get all JSON files from Muwatta Malik directory
    books_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Results", "Muwatta Malik")
    json_files = glob.glob(os.path.join(books_dir, "book_*.json"))
    
    print(f"📂 Found {len(json_files)} book files to import")
    
    if not json_files:
        print("❌ No book files found in Muwatta Malik directory!")
        return
    
    # Create database session
    db_session = SessionLocal()
    
    try:
        successful_imports = 0
        failed_imports = 0
        
        for json_file in sorted(json_files):
            print(f"\n📖 Processing: {os.path.basename(json_file)}")
            
            book_data = load_json_file(json_file)
            if book_data:
                if import_book_to_db(book_data, db_session):
                    successful_imports += 1
                else:
                    failed_imports += 1
            else:
                failed_imports += 1
        
        print(f"\n🎉 Import Summary:")
        print(f"✅ Successful imports: {successful_imports}")
        print(f"❌ Failed imports: {failed_imports}")
        print(f"📊 Total processed: {successful_imports + failed_imports}")
        
    except Exception as e:
        print(f"❌ Critical error during import: {e}")
    finally:
        db_session.close()

def import_modified_books():
    """Import all JSON books from Muwatta_Malik_Modified directory (with narrator info)"""
    # Get all JSON files from modified directory
    books_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Results", "Muwatta_Malik_Modified")
    json_files = glob.glob(os.path.join(books_dir, "book_*.json"))
    
    print(f"📂 Found {len(json_files)} modified book files to import")
    
    if not json_files:
        print("❌ No modified book files found in Muwatta_Malik_Modified directory!")
        return
    
    # Create database session
    db_session = SessionLocal()
    
    try:
        successful_imports = 0
        failed_imports = 0
        
        for json_file in sorted(json_files):
            print(f"\n📖 Processing: {os.path.basename(json_file)}")
            
            book_data = load_json_file(json_file)
            if book_data:
                if import_book_to_db(book_data, db_session):
                    successful_imports += 1
                else:
                    failed_imports += 1
            else:
                failed_imports += 1
        
        print(f"\n🎉 Import Summary:")
        print(f"✅ Successful imports: {successful_imports}")
        print(f"❌ Failed imports: {failed_imports}")
        print(f"📊 Total processed: {successful_imports + failed_imports}")
        
    except Exception as e:
        print(f"❌ Critical error during import: {e}")
    finally:
        db_session.close()

def get_database_stats():
    """Get statistics about imported data"""
    db_session = SessionLocal()
    
    try:
        book_count = db_session.query(Book).count()
        hadith_count = db_session.query(Hadith).count()
        
        print(f"\n📊 Database Statistics:")
        print(f"📚 Total Books: {book_count}")
        print(f"📜 Total Hadiths: {hadith_count}")
        
        # Show books
        books = db_session.query(Book).order_by(Book.book_number).all()
        print(f"\n📖 Books in Database:")
        for book in books:
            hadith_count_for_book = db_session.query(Hadith).filter(Hadith.book_id == book.id).count()
            print(f"  Book {book.book_number}: {book.english_name} ({hadith_count_for_book} hadiths)")
        
    except Exception as e:
        print(f"❌ Error getting database stats: {e}")
    finally:
        db_session.close()

def main():
    """Main function"""
    print("🚀 Starting Muwatta Malik Database Import")
    print("=" * 50)
    
    # Create tables first
    create_tables()
    
    # Choose which directory to import from
    choice = input("\nChoose import source:\n1. Original books (Muwatta Malik/)\n2. Modified books with narrators (Muwatta_Malik_Modified/)\n3. Both\n4. Show database stats only\nEnter choice (1-4): ")
    
    if choice == "1":
        import_all_books()
    elif choice == "2":
        import_modified_books()
    elif choice == "3":
        import_all_books()
        import_modified_books()
    elif choice == "4":
        pass
    else:
        print("Invalid choice. Showing stats only.")
    
    # Show final stats
    get_database_stats()

if __name__ == "__main__":
    main()
