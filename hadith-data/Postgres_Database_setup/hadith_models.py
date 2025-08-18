"""
Database models for Hadith storage
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database_config import Base

class Book(Base):
    """Model for Hadith books"""
    __tablename__ = "books"
    
    id = Column(Integer, primary_key=True, index=True)
    book_number = Column(String(10), unique=True, index=True)
    english_name = Column(String(255), nullable=False)
    arabic_name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship with hadiths
    hadiths = relationship("Hadith", back_populates="book", cascade="all, delete-orphan")

class Hadith(Base):
    """Model for individual hadiths"""
    __tablename__ = "hadiths"
    
    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    english_text = Column(Text, nullable=False)
    arabic_text = Column(Text, nullable=False)
    references = Column(JSON)  # Store reference information as JSON
    narrators = Column(JSON)   # Store narrator chain as JSON (if available)
    content = Column(Text)     # Processed content (if available)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship with book
    book = relationship("Book", back_populates="hadiths")
    
    def __repr__(self):
        return f"<Hadith(id={self.id}, book_id={self.book_id})>"
