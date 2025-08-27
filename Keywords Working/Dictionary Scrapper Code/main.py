#!/usr/bin/env python3
"""
Complete Quranic Arabic Dictionary Scraper

This script scrapes the complete Quranic Arabic dictionary from corpus.quran.com
including all letters, keywords, descriptions, and Quranic verse occurrences.

Usage:
    python main.py [--testing] [--resume] [--letters A,b,t] [--max-keywords 10]

Options:
    --testing: Run in testing mode with limited data
    --resume: Resume from last saved progress
    --letters: Specify specific letters to scrape (comma-separated)
    --max-keywords: Maximum keywords per letter (for testing)
"""

import argparse
import sys
import time
import logging
from datetime import datetime

# Import our modules
from config import ARABIC_LETTERS, TESTING_MODE, MAX_LETTERS_FOR_TESTING, MAX_KEYWORDS_PER_LETTER
from utils import setup_logging, save_json, ProgressTracker, safe_log_text, format_filename
from browser_manager import WebDriverManager
from scraper import QuranDictionaryScraper

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Scrape Quranic Arabic Dictionary')
    
    parser.add_argument('--testing', action='store_true', 
                       help='Run in testing mode with limited data')
    parser.add_argument('--resume', action='store_true',
                       help='Resume from last saved progress')
    parser.add_argument('--letters', type=str,
                       help='Specific letters to scrape (comma-separated, e.g., A,b,t)')
    parser.add_argument('--max-keywords', type=int,
                       help='Maximum keywords per letter (for testing)')
    parser.add_argument('--headless', action='store_true', default=True,
                       help='Run browser in headless mode (default: True)')
    parser.add_argument('--delay', type=float, default=2.0,
                       help='Delay between requests in seconds (default: 2.0)')
    
    return parser.parse_args()

def get_letters_to_process(args, progress_tracker):
    """Determine which letters to process based on arguments and progress"""
    
    if args.letters:
        # User specified specific letters
        specified_letters = [l.strip() for l in args.letters.split(',')]
        letters_to_process = []
        for letter_param in specified_letters:
            # Find the Arabic letter for this parameter
            arabic_letter = None
            for ar, param in ARABIC_LETTERS.items():
                if param == letter_param:
                    arabic_letter = ar
                    break
            
            if arabic_letter:
                letters_to_process.append((arabic_letter, letter_param))
            else:
                logging.warning(f"Unknown letter parameter: {letter_param}")
        
        return letters_to_process
    
    # Get all letters
    all_letters = list(ARABIC_LETTERS.items())
    
    if args.testing:
        # Testing mode - limit letters
        max_letters = args.max_keywords or MAX_LETTERS_FOR_TESTING
        all_letters = all_letters[:max_letters]
    
    if args.resume:
        # Resume mode - filter out completed letters
        remaining_letters = []
        for arabic_letter, letter_param in all_letters:
            if not progress_tracker.is_letter_completed(letter_param):
                remaining_letters.append((arabic_letter, letter_param))
        return remaining_letters
    
    return all_letters

def main():
    """Main scraping function"""
    
    # Parse arguments
    args = parse_arguments()
    
    # Setup logging
    logger = setup_logging()
    logger.info("Starting Quranic Arabic Dictionary Scraper")
    logger.info(f"Arguments: {vars(args)}")
    
    # Initialize progress tracker
    progress_tracker = ProgressTracker()
    
    if args.resume:
        logger.info("Resuming from previous progress...")
        stats = progress_tracker.get_stats()
        logger.info(f"Previous progress: {stats}")
    
    # Determine letters to process
    letters_to_process = get_letters_to_process(args, progress_tracker)
    safe_letters = [safe_log_text(l[0]) for l in letters_to_process]
    logger.info(f"Will process {len(letters_to_process)} letters: {safe_letters}")
    
    if not letters_to_process:
        logger.info("No letters to process. Exiting.")
        return
    
    # Initialize WebDriver and Scraper
    try:
        with WebDriverManager() as driver_manager:
            scraper = QuranDictionaryScraper(driver_manager)
            
            all_scraped_data = []
            
            for i, (arabic_letter, letter_param) in enumerate(letters_to_process, 1):
                safe_letter = safe_log_text(arabic_letter)
                logger.info(f"\n{'='*60}")
                logger.info(f"Processing letter {i}/{len(letters_to_process)}: '{safe_letter}' (param: {letter_param})")
                logger.info(f"{'='*60}")
                
                try:
                    # Check if letter is already completed
                    if progress_tracker.is_letter_completed(letter_param):
                        logger.info(f"Letter '{safe_letter}' already completed. Skipping.")
                        continue
                    
                    # Determine max keywords for this letter
                    max_keywords = None
                    if args.testing or args.max_keywords:
                        max_keywords = args.max_keywords or MAX_KEYWORDS_PER_LETTER
                    
                    # Update progress
                    progress_tracker.update_letter_progress(arabic_letter, 0)
                    
                    # Scrape the letter
                    letter_data = scraper.scrape_letter(arabic_letter, letter_param, max_keywords)
                    
                    if letter_data:
                        # Save individual letter data
                        letter_filename = f"letter_{format_filename(letter_param)}_{format_filename(arabic_letter)}.json"
                        save_json(letter_data, letter_filename)
                        
                        # Add to combined data
                        all_scraped_data.extend(letter_data)
                        
                        # Mark letter as completed
                        progress_tracker.mark_letter_completed(letter_param)
                        
                        logger.info(f"Successfully scraped {len(letter_data)} keywords for letter '{safe_letter}'")
                    else:
                        logger.warning(f"No data scraped for letter '{safe_letter}'")
                    
                    # Save progress
                    progress_tracker.save()
                    
                    # Save combined data so far
                    if all_scraped_data:
                        save_json(all_scraped_data, "complete_quran_dictionary.json")
                    
                except Exception as e:
                    logger.error(f"Error processing letter '{safe_letter}': {e}")
                    continue
            
            # Final save
            if all_scraped_data:
                save_json(all_scraped_data, "complete_quran_dictionary.json")
                
                # Generate summary report
                generate_summary_report(all_scraped_data)
                
            # Final statistics
            final_stats = progress_tracker.get_stats()
            logger.info(f"\n{'='*60}")
            logger.info("SCRAPING COMPLETED!")
            logger.info(f"Final Statistics: {final_stats}")
            logger.info(f"Total keywords scraped: {len(all_scraped_data)}")
            logger.info(f"{'='*60}")
            
    except KeyboardInterrupt:
        logger.info("Scraping interrupted by user. Progress has been saved.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

def generate_summary_report(scraped_data):
    """Generate a summary report of scraped data"""
    
    summary = {
        'total_keywords': len(scraped_data),
        'total_occurrences': sum(kw['total_occurrences'] for kw in scraped_data),
        'letters_processed': len(set(kw['letter'] for kw in scraped_data)),
        'keywords_by_letter': {},
        'top_keywords': [],
        'generation_time': datetime.now().isoformat()
    }
    
    # Group by letter
    for keyword in scraped_data:
        letter = keyword['letter']
        if letter not in summary['keywords_by_letter']:
            summary['keywords_by_letter'][letter] = {
                'count': 0,
                'total_occurrences': 0
            }
        
        summary['keywords_by_letter'][letter]['count'] += 1
        summary['keywords_by_letter'][letter]['total_occurrences'] += keyword['total_occurrences']
    
    # Find top keywords by occurrence count
    top_keywords = sorted(scraped_data, key=lambda x: x['total_occurrences'], reverse=True)[:20]
    summary['top_keywords'] = [
        {
            'keyword': kw['keyword_text'],
            'letter': kw['letter'],
            'occurrences': kw['total_occurrences']
        }
        for kw in top_keywords
    ]
    
    save_json(summary, "scraping_summary.json")
    
    logging.info("Summary report generated:")
    logging.info(f"  - Total keywords: {summary['total_keywords']}")
    logging.info(f"  - Total occurrences: {summary['total_occurrences']}")
    logging.info(f"  - Letters processed: {summary['letters_processed']}")

if __name__ == "__main__":
    main()
