"""
Reddit Scraper

Uses a simple descriptive User-Agent (Reddit's preferred format for scripts)
and hits the subreddit search.json endpoint directly.
"""

import requests
import logging
from urllib.parse import quote
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

MAX_POSTS = 5


class RedditScraper:

    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    def scrape(self, course_code: str) -> Optional[Dict[str, Any]]:
        """
        Scrapes r/VirginiaTech for posts with course code
        @args: course_code: ex. ece 1004
        @return: dict with list of postss
        """
        try:
            search_query = course_code.replace(' ', '').upper()
            encoded = quote(search_query, safe='')

            url = (
                f"https://www.reddit.com/r/VirginiaTech/search.json"
                f"?q={encoded}&restrict_sr=1&sort=relevance&t=all"
            )

            logger.info(f"Scraping Reddit: {url}")

            response = requests.get(
                url,
                timeout=self.timeout,
                headers={
                    "Accept": "application/json",
                    "User-Agent": "VTCourseHelper/0.1 (contact: local-dev)",
                }
            )

            logger.info(f"Reddit status: {response.status_code}")
            response.raise_for_status()

            data = response.json()
            children = data.get("data", {}).get("children", [])

            posts = []
            for child in children[:MAX_POSTS]:
                post_data = child.get("data", {})
                title = post_data.get("title", "").strip()
                permalink = post_data.get("permalink", "")
                if title:
                    posts.append({
                        "title": title,
                        "post_url": f"https://www.reddit.com{permalink}" if permalink else None,
                    })

            logger.info(f"Found {len(posts)} Reddit posts for: {course_code}")
            return {"posts": posts, "count": len(posts)}

        except requests.exceptions.Timeout:
            logger.error(f"Reddit timeout: {course_code}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Reddit request error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Reddit error: {str(e)}")
            return None