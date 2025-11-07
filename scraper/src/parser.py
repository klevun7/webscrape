from bs4 import BeautifulSoup
from typing import List, Dict
from urllib.parse import urljoin
import logging

logger = logging.getLogger(__name__)
class QuotesParser:

    def parse_quotes_page(self, html: str, base_url: str) -> List[Dict]:
        soup = BeautifulSoup(html, 'html.parser')
        quotes = []

        quote_divs = soup.find_all('div', class_ = "quote")

        for quote_div in quote_divs:
            try:
                quote = self.parse_quotes_element(quote_div, base_url)
                if quote:
                    quotes.append(quote)
            except Exception as e:
                logger.warning(f"Failed to parse quote: {e}")
                continue
        return quotes

    def parse_quotes_element(self, quote_div, base_url: str) -> Dict:
        text_elem = quote_div.find('span', class_="text")
        quote_text = text_elem.text.strip() if text_elem else ''

        author_elem = quote_div.find('small', class_="author")
        author = author_elem.text.strip() if author_elem else ''

        author_url = ''
        author_link = quote_div.find('a')
        if author_link:
            href =  author_link.get('href', '')
            author_url = urljoin(base_url,href)
        
        tags_div = quote_div.find('div', class_='tags')
        tags = []
        if tags_div:
            tag_links = tags_div.find_all('a', class_='tag')
            tags = []
            for tag in tag_links:
                tags.append(tag.text.strip())
            
        quote_url = base_url

        return {
            'text': quote_text,
            'author': author,
            'author_url': author_url,
            'tags': tags,
            'tag_count': len(tags),
            'url': quote_url
        }