import httpx
from urllib.robotparser import RobotFileParser
from urllib.parse import urljoin
import logging

logger = logging.getLogger(__name__)

class RobotsChecker:
    
    def can_fetch(self, base_url: str, url: str, user_agent: str = "Quote Scraper") -> bool:
        robots_url = urljoin(base_url, '/robots.txt')
        try:
            with httpx.Client() as client:
                response = client.get(robots_url, timeout=10.0)
                
            if response.status_code == 404:
                logger.info("No robots.txt found - assuming crawling is allowed")
                return True
                
            response.raise_for_status()
            
            rp = RobotFileParser()
            rp.parse(response.text.splitlines())
            
            can_fetch = rp.can_fetch(user_agent, url)
            logger.info(f"robots.txt check: {'Allowed' if can_fetch else 'Disallowed'} for {user_agent}")
            
            return can_fetch
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.info("robots.txt not found (404) - assuming crawling is allowed")
                return True
            logger.warning(f"Error fetching robots.txt: {e}")
            return True  
            
        except Exception as e:
            logger.warning(f"Error checking robots.txt: {e}")
            return True  
