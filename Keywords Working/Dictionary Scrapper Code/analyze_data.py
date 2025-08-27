#!/usr/bin/env python3
"""
Data Analysis and Export Script for Quranic Dictionary Data

This script provides various analysis and export functions for the scraped data.
"""

import json
import pandas as pd
import logging
from datetime import datetime
from collections import Counter, defaultdict
from utils import load_json, save_json, setup_logging

class QuranDictionaryAnalyzer:
    """Analyze and export scraped Quranic dictionary data"""
    
    def __init__(self, data_file="complete_quran_dictionary.json"):
        self.logger = logging.getLogger(__name__)
        self.data = load_json(data_file)
        
        if not self.data:
            raise ValueError(f"No data found in {data_file}")
        
        self.logger.info(f"Loaded {len(self.data)} keywords for analysis")
    
    def generate_statistics(self):
        """Generate comprehensive statistics"""
        stats = {
            'overview': self._get_overview_stats(),
            'letter_distribution': self._get_letter_distribution(),
            'occurrence_analysis': self._get_occurrence_analysis(),
            'word_type_analysis': self._get_word_type_analysis(),
            'surah_distribution': self._get_surah_distribution(),
            'generated_at': datetime.now().isoformat()
        }
        
        save_json(stats, "dictionary_statistics.json")
        self.logger.info("Statistics generated and saved")
        return stats
    
    def _get_overview_stats(self):
        """Get basic overview statistics"""
        total_keywords = len(self.data)
        total_occurrences = sum(kw['total_occurrences'] for kw in self.data)
        letters_covered = len(set(kw['letter'] for kw in self.data))
        
        return {
            'total_keywords': total_keywords,
            'total_occurrences': total_occurrences,
            'letters_covered': letters_covered,
            'avg_occurrences_per_keyword': total_occurrences / total_keywords if total_keywords > 0 else 0
        }
    
    def _get_letter_distribution(self):
        """Analyze distribution across letters"""
        letter_stats = defaultdict(lambda: {'keywords': 0, 'occurrences': 0})
        
        for keyword in self.data:
            letter = keyword['letter']
            letter_stats[letter]['keywords'] += 1
            letter_stats[letter]['occurrences'] += keyword['total_occurrences']
        
        return dict(letter_stats)
    
    def _get_occurrence_analysis(self):
        """Analyze occurrence patterns"""
        occurrence_counts = [kw['total_occurrences'] for kw in self.data]
        occurrence_counter = Counter(occurrence_counts)
        
        return {
            'min_occurrences': min(occurrence_counts) if occurrence_counts else 0,
            'max_occurrences': max(occurrence_counts) if occurrence_counts else 0,
            'median_occurrences': sorted(occurrence_counts)[len(occurrence_counts)//2] if occurrence_counts else 0,
            'occurrence_frequency': dict(occurrence_counter.most_common(20)),
            'top_keywords': self._get_top_keywords(20)
        }
    
    def _get_top_keywords(self, limit=20):
        """Get top keywords by occurrence count"""
        sorted_keywords = sorted(self.data, key=lambda x: x['total_occurrences'], reverse=True)
        return [
            {
                'keyword': kw['keyword_text'],
                'letter': kw['letter'],
                'occurrences': kw['total_occurrences'],
                'word_type': kw.get('word_type', ''),
                'meaning': kw.get('meaning', '')
            }
            for kw in sorted_keywords[:limit]
        ]
    
    def _get_word_type_analysis(self):
        """Analyze word types distribution"""
        word_types = [kw.get('word_type', 'Unknown') for kw in self.data]
        word_type_counter = Counter(word_types)
        
        return {
            'total_types': len(word_type_counter),
            'type_distribution': dict(word_type_counter.most_common())
        }
    
    def _get_surah_distribution(self):
        """Analyze distribution across Surahs"""
        surah_occurrences = defaultdict(int)
        
        for keyword in self.data:
            for occurrence in keyword.get('occurrences', []):
                surah_num = occurrence.get('surah')
                if surah_num:
                    surah_occurrences[surah_num] += 1
        
        return {
            'surahs_covered': len(surah_occurrences),
            'top_surahs': dict(Counter(surah_occurrences).most_common(20))
        }
    
    def export_to_csv(self):
        """Export data to CSV files"""
        try:
            # Main keywords CSV
            keywords_data = []
            for kw in self.data:
                keywords_data.append({
                    'letter': kw['letter'],
                    'keyword_text': kw['keyword_text'],
                    'keyword_value': kw['keyword_value'],
                    'word_type': kw.get('word_type', ''),
                    'meaning': kw.get('meaning', ''),
                    'description': kw.get('description', ''),
                    'total_occurrences': kw['total_occurrences'],
                    'scraped_at': kw.get('scraped_at', '')
                })
            
            keywords_df = pd.DataFrame(keywords_data)
            keywords_df.to_csv('scraped_data/keywords.csv', index=False, encoding='utf-8')
            
            # Occurrences CSV
            occurrences_data = []
            for kw in self.data:
                for occ in kw.get('occurrences', []):
                    occurrences_data.append({
                        'keyword_text': kw['keyword_text'],
                        'letter': kw['letter'],
                        'surah': occ.get('surah'),
                        'verse': occ.get('verse'),
                        'word_position': occ.get('word_position'),
                        'verse_reference': occ.get('verse_reference', {}).get('reference', ''),
                        'transliteration': occ.get('transliteration', ''),
                        'english_meaning': occ.get('english_meaning', ''),
                        'arabic_text': occ.get('arabic_text', ''),
                        'highlighted_word': occ.get('highlighted_word', '')
                    })
            
            occurrences_df = pd.DataFrame(occurrences_data)
            occurrences_df.to_csv('scraped_data/occurrences.csv', index=False, encoding='utf-8')
            
            self.logger.info("Data exported to CSV files")
            
        except Exception as e:
            self.logger.error(f"Error exporting to CSV: {e}")
    
    def export_by_letter(self):
        """Export separate files for each letter"""
        letter_groups = defaultdict(list)
        
        for keyword in self.data:
            letter_groups[keyword['letter']].append(keyword)
        
        for letter, keywords in letter_groups.items():
            filename = f"letter_{letter}_detailed.json"
            save_json(keywords, filename)
        
        self.logger.info(f"Exported {len(letter_groups)} letter files")
    
    def create_search_index(self):
        """Create a search index for quick keyword lookup"""
        search_index = {}
        
        for keyword in self.data:
            # Index by keyword text
            key = keyword['keyword_text'].lower()
            search_index[key] = keyword
            
            # Index by transliterations
            for occ in keyword.get('occurrences', []):
                trans = occ.get('transliteration', '').lower()
                if trans and trans not in search_index:
                    search_index[trans] = keyword
        
        save_json(search_index, "keyword_search_index.json")
        self.logger.info(f"Created search index with {len(search_index)} entries")
    
    def generate_report(self):
        """Generate a comprehensive report"""
        stats = self.generate_statistics()
        
        report = f"""
# Quranic Arabic Dictionary Scraping Report

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overview
- **Total Keywords**: {stats['overview']['total_keywords']:,}
- **Total Occurrences**: {stats['overview']['total_occurrences']:,}
- **Letters Covered**: {stats['overview']['letters_covered']}/28
- **Average Occurrences per Keyword**: {stats['overview']['avg_occurrences_per_keyword']:.2f}

## Top 10 Most Frequent Keywords
"""
        
        for i, kw in enumerate(stats['occurrence_analysis']['top_keywords'][:10], 1):
            report += f"{i}. **{kw['keyword']}** ({kw['letter']}) - {kw['occurrences']} occurrences\n"
        
        report += f"""

## Letter Distribution
"""
        
        for letter, data in sorted(stats['letter_distribution'].items()):
            report += f"- **{letter}**: {data['keywords']} keywords, {data['occurrences']} occurrences\n"
        
        # Save report
        with open('scraped_data/scraping_report.md', 'w', encoding='utf-8') as f:
            f.write(report)
        
        self.logger.info("Comprehensive report generated")
        return report

def main():
    """Main analysis function"""
    setup_logging()
    
    try:
        analyzer = QuranDictionaryAnalyzer()
        
        print("Generating statistics...")
        analyzer.generate_statistics()
        
        print("Exporting to CSV...")
        analyzer.export_to_csv()
        
        print("Exporting by letter...")
        analyzer.export_by_letter()
        
        print("Creating search index...")
        analyzer.create_search_index()
        
        print("Generating report...")
        report = analyzer.generate_report()
        
        print("\nAnalysis completed! Check the 'scraped_data' directory for outputs.")
        print("\nQuick Summary:")
        print(report.split("## Top 10")[0])
        
    except Exception as e:
        logging.error(f"Analysis failed: {e}")

if __name__ == "__main__":
    main()
