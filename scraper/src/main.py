import json
import logging
import time
from pathlib import Path
from src.fetcher import Fetcher
from src.parser import QuotesParser
from src.pagignation import PaginationHandler
from src.robots import RobotsChecker

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
        self.parser = QuotesParser
        self.pagination = PaginationHandler()
        self.robots = RobotsChecker()
        self.seen_urls = set()
        self.seen_authors = set()

    def crawl(self):
        base_url = '/'.join(self.start_url.split('/')[:3])
        can_fetch = self.robots.can_fetch(base_url, self.start_url)

        if not can_fetch and not self.dry_run:
            logger.error("Crawling not allowed by robots.txt. Exiting")
            return
        
        output_file = Path("data/items.jsonl")
        output_file.parent.mkdir(exist_ok=True)

        if not self.dry_run:
            output_file.write_text("")
        
        current_url = self.start_url
        pages_crawled = 0
        total_items = 0

        while current_url and pages_crawled < self.max_pages:
            if current_url in self.seen_urls:
                logger.info(f"URL: {current_url} already seen skipping.")
            self.seen_urls.add(current_url)
            
