import argparse
import json
import logging
import time
from pathlib import Path
from fetcher import Fetcher
from parser import QuotesParser
from pagination import PaginationHandler
from robots import RobotsChecker

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class QuotesScraper:
    
    def __init__(self, start_url: str, max_pages: int, delay_ms: int, dry_run: bool = False, fetch_authors: bool = False):        
        self.start_url = start_url
        self.max_pages = max_pages
        self.delay_ms = delay_ms
        self.dry_run = dry_run
        self.fetch_authors = fetch_authors
        self.fetcher = Fetcher(delay_ms)
        self.parser = QuotesParser()
        self.pagination = PaginationHandler()
        self.robots = RobotsChecker()
        self.seen_urls = set()
        self.seen_authors = set()
        
    def crawl(self):
        base_url = '/'.join(self.start_url.split('/')[:3])
        can_fetch = self.robots.can_fetch(base_url, self.start_url)
        logger.info(f"robots.txt check for {self.start_url}: {'✓ Allowed' if can_fetch else '✗ Disallowed'}")
        
        if not can_fetch and not self.dry_run:
            logger.error("Crawling not allowed by robots.txt. Exiting.")
            return
            
        output_file = Path("data/items.jsonl")
        output_file.parent.mkdir(exist_ok=True)
        
        if not self.dry_run:
            output_file.write_text("") 
            
        current_url = self.start_url
        pages_crawled = 0
        total_items = 0
        
        logger.info(f"Starting crawl: max_pages={self.max_pages}, delay={self.delay_ms}ms, fetch_authors={self.fetch_authors}")
        
        while current_url and pages_crawled < self.max_pages:
            if current_url in self.seen_urls:
                logger.info(f"Skipping duplicate URL: {current_url}")
                break
                
            self.seen_urls.add(current_url)
            
 
            if self.dry_run:
                logger.info(f"[DRY RUN] Would crawl page {pages_crawled + 1}: {current_url}")
                pages_crawled += 1

                if pages_crawled < self.max_pages:
                    current_url = f"{base_url}/page/{pages_crawled + 1}/"
                else:
                    break
                continue
                
            logger.info(f"Crawling page {pages_crawled + 1}/{self.max_pages}: {current_url}")
            

            html = self.fetcher.fetch(current_url)
            if not html:
                logger.error(f"Failed to fetch {current_url}. Stopping crawl.")
                break
                

            quotes = self.parser.parse_quotes_page(html, current_url)
            
            

            with open(output_file, 'a', encoding='utf-8') as f:
                for quote in quotes:
                    f.write(json.dumps(quote, ensure_ascii=False) + '\n')
                    
            total_items += len(quotes)
            logger.info(f"Extracted {len(quotes)} quotes from page {pages_crawled + 1}")
            

            next_url = self.pagination.get_next_page(html, current_url)
            current_url = next_url
            pages_crawled += 1
            
        logger.info(f"{'=' * 50}")
        logger.info(f"Crawl complete!")
        logger.info(f"Pages scraped: {pages_crawled}")
        logger.info(f"Total items: {total_items}")
        logger.info(f"Output file: {output_file.absolute()}")
        logger.info(f"{'=' * 50}")

def main():
    parser = argparse.ArgumentParser(
        description='Scrape quotes from quotes.toscrape.com',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='Example usage:\n  python main.py --site quotes --start http://quotes.toscrape.com/page/1/ --max-pages 10 --delay-ms 500'
    )
    parser.add_argument('--site', default='quotes', help='Site to scrape (books or quotes)')
    parser.add_argument('--start', required=True, help='Starting URL')
    parser.add_argument('--max-pages', type=int, default=5, help='Maximum pages to crawl (default: 5)')
    parser.add_argument('--delay-ms', type=int, default=700, help='Delay between requests in ms (default: 700)')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode - log what would be crawled without saving')
    
    args = parser.parse_args()
    
    scraper = QuotesScraper(args.start, args.max_pages, args.delay_ms, args.dry_run)
    scraper.crawl()

if __name__ == '__main__':
    main()