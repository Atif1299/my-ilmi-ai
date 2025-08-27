import logging
import json
import os
from datetime import datetime
from config import LOG_LEVEL, LOG_FILE, OUTPUT_DIR

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL),
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def safe_log_text(text):
    """Convert text to ASCII-safe version for logging"""
    if not text:
        return text
    try:
        # Try to encode as ASCII, replace problematic characters
        return text.encode('ascii', 'replace').decode('ascii')
    except:
        return repr(text)

def save_json(data, filename):
    """Save data to JSON file"""
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logging.info(f"Data saved to {filepath}")

def load_json(filename):
    """Load data from JSON file"""
    filepath = os.path.join(OUTPUT_DIR, filename)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def save_progress(progress_data):
    """Save scraping progress"""
    progress_data['last_updated'] = datetime.now().isoformat()
    save_json(progress_data, 'scraping_progress.json')

def load_progress():
    """Load scraping progress"""
    return load_json('scraping_progress.json') or {
        'completed_letters': [],
        'current_letter': None,
        'completed_keywords': [],
        'total_keywords_scraped': 0,
        'last_updated': None
    }

def clean_text(text):
    """Clean and normalize text"""
    if not text:
        return ""
    return text.strip().replace('\n', ' ').replace('\r', ' ')

def extract_verse_reference(text):
    """Extract verse reference like (2:31:2) from text"""
    import re
    pattern = r'\((\d+):(\d+):(\d+)\)'
    match = re.search(pattern, text)
    if match:
        return {
            'surah': int(match.group(1)),
            'verse': int(match.group(2)),
            'word': int(match.group(3)),
            'reference': match.group(0)
        }
    return None

def format_filename(text):
    """Create a safe filename from text"""
    import re
    # Remove special characters and replace with underscores
    safe_text = re.sub(r'[<>:"/\\|?*]', '_', text)
    return safe_text[:50]  # Limit length

class ProgressTracker:
    """Track scraping progress"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.progress = load_progress()
        self.start_time = datetime.now()
        
    def update_letter_progress(self, letter, keywords_count):
        """Update progress for a letter"""
        self.progress['current_letter'] = letter
        self.progress[f'keywords_count_{letter}'] = keywords_count
        safe_letter = safe_log_text(letter)
        self.logger.info(f"Processing letter '{safe_letter}' with {keywords_count} keywords")
        
    def mark_letter_completed(self, letter):
        """Mark a letter as completed"""
        if letter not in self.progress['completed_letters']:
            self.progress['completed_letters'].append(letter)
        self.progress['current_letter'] = None
        safe_letter = safe_log_text(letter)
        self.logger.info(f"Completed letter '{safe_letter}'")
        
    def mark_keyword_completed(self, letter, keyword):
        """Mark a keyword as completed"""
        key = f"completed_keywords_{letter}"
        if key not in self.progress:
            self.progress[key] = []
        
        if keyword not in self.progress[key]:
            self.progress[key].append(keyword)
            self.progress['total_keywords_scraped'] += 1
            
        safe_letter = safe_log_text(letter)
        safe_keyword = safe_log_text(keyword)
        self.logger.info(f"Completed keyword '{safe_keyword}' for letter '{safe_letter}'")
        
    def is_letter_completed(self, letter):
        """Check if a letter is already completed"""
        return letter in self.progress['completed_letters']
        
    def is_keyword_completed(self, letter, keyword):
        """Check if a keyword is already completed"""
        key = f"completed_keywords_{letter}"
        return keyword in self.progress.get(key, [])
        
    def save(self):
        """Save current progress"""
        save_progress(self.progress)
        
    def get_stats(self):
        """Get scraping statistics"""
        elapsed = datetime.now() - self.start_time
        return {
            'letters_completed': len(self.progress['completed_letters']),
            'total_keywords_scraped': self.progress['total_keywords_scraped'],
            'elapsed_time': str(elapsed),
            'current_letter': self.progress.get('current_letter'),
            'last_updated': self.progress.get('last_updated')
        }
