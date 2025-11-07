import time 
import logging
from typing import Optional
import httpx

logger = logging.getLogger(__name__)
class Fetcher:
    def __init__(self, delay_ms: int):
        self.delay_ms = delay_ms / 1000.0  # seconds
        self.last_fetch_time = 0.0
        self.user_agent = "QuotesScraperBot/1.0 (Educational Usage +https://github.com/klevun7/webscrape)"
        self.max_retries = 3
        self.backoff_factor = 2
        self.last_request_time = 0

    def fetch(self, url: str) -> Optional[str]:
        for attempt in range(self.max_retries):
            try:
                elapsed = time.time() - self.last_request_time
                sleep_time = (self.delay_ms / 1000) - elapsed
                if sleep_time > 0:
                    time.sleep(sleep_time)
                
                with httpx.Client() as client:
                    response = client.get(
                        url,
                        headers={
                            'User-Agent': self.user_agent,
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                            'Accept-Language': 'en-US,en;q=0.5',
                        },
                        timeout=30.0,
                        follow_redirects=True
                    )
                    self.last_request_time = time.time()
                    response.raise_for_status()
                    logger.debug(f"Successfully fetched {url} (status: {response.status_code})")
                    return response.text
                    
            except httpx.HTTPStatusError as e:
                logger.warning(f"HTTP error on attempt {attempt + 1} for {url}: {e.response.status_code}")
                if e.response.status_code == 404:
                    logger.error(f"Page not found (404): {url}")
                    return None
                    
            except httpx.TimeoutException:
                logger.warning(f"Timeout on attempt {attempt + 1} for {url}")
                
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {type(e).__name__}: {e}")


            # Exponential backoff
            if attempt < self.max_retries - 1:
                wait_time = self.backoff_factor ** attempt
                logger.info(f"Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                logger.error(f"Max retries ({self.max_retries}) reached for {url}")
                return None
        
        return None