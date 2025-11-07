from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class PaginationHandler:
    def get_next_page(self, html: str, current_url: str) -> Optional[str]:
        soup = BeautifulSoup(html, 'html.parser')
        pager = soup.find('ul', class_ = 'pager')
        if pager:
            next_link = pager.find('li', class_='next')
            if next_link:
                anchor = next_link.find('a')
                if anchor and anchor.get('href'):
                    next_url = urljoin(current_url, anchor['href'])
                    return next_url
        logger.info("No next page found.")
        return None