
import requests
import logging
from typing import Optional, Dict, Any
from urllib.parse import quote

logger = logging.getLogger(__name__)

class RedditScraper:
    """Scraper for Reddit discussion posts"""

    BASE_URL =  "https://www.reddit.com/r/VirginiaTech/search.json"
    MAX_TITLES = 5

    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    ]

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.user_agent_idx = 0
    
    def _get_user_agent(self) -> str:
        """Get rotating user agent"""
        agent = self.USER_AGENTS[self.user_agent_idx % len(self.USER_AGENTS)]
        self.user_agent_idx += 1
        return agent
    
    def scrape(self, course_code: str) -> Optional[Dict[str, Any]]:
        """
        Scrape Reddit for course posts
        @args: course_code: course code (ex. ECE 1004)
        @return: dict with list of titles or none
        """

        try:
            logger.info(f"Scraping Reddit: {course_code}")

            search_query = course_code.replace(' ', '')
            encoded_query = quote(search_query, safe='')

            url = f"{self.BASE_URL}?q={encoded_query}&restrict_sr=1&sort=relevance&t=all"
            
            response = requests.get(
                url,
                headers={'User-Agent': self._get_user_agent()},
                timeout=self.timeout
            )

            response.raise_for_status()
            data = response.json()

            posts = data.get('data', {}).get('children', [])

            if not posts:
                logger.info(f"No Reddit posts: {course_code}")
                return {'titles': [], 'count': 0}
            
            titles = []
            for post in posts[:self.MAX_TITLES]:
                title = post.get('data', {}).get('title', {}).strip()
                if title:
                    titles.append(title)

            logger.info(f"Found {len(titles)} Reddit posts: {course_code}")
            return {'titles': titles, 'count': len(titles)}
        
        except requests.exceptions.Timeout:
            logger.error(f"Reddit timeout: {course_code}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Reddit request error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Reddit scraping error: {str(e)}")
            return None