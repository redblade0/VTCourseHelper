"""
Rate My Professor Scraper
Fetches professor ratings using GraphQL API
"""

import requests
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class RMPScraper:
    """Scraper for Rate My Professor data"""

    GRAPHQL_URL = "https://www.ratemyprofessors.com/graphql"
    REFERER = "https://www.ratemyprofessors.com/"
    VT_SCHOOL_ID = "U2Nob29sLTEzNDk="  # Encoded School-1349

    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    ]

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.user_agent_idx = 0

    def _get_user_agent(self) -> str:
        agent = self.USER_AGENTS[self.user_agent_idx % len(self.USER_AGENTS)]
        self.user_agent_idx += 1
        return agent

    def scrape(self, professor_name: str) -> Optional[Dict[str, Any]]:
        """
        Scrape professor data from RMP using newSearch GraphQL API
        """
        try:
            logger.info(f"Scraping RMP: {professor_name}")

            query = """
            query SearchTeacher($query: TeacherSearchQuery!) {
                newSearch {
                    teachers(query: $query) {
                        edges {
                            node {
                                firstName
                                lastName
                                avgRating
                                avgDifficulty
                                numRatings
                            }
                        }
                    }
                }
            }
            """

            payload = {
                "operationName": "SearchTeacher",
                "query": query,
                "variables": {
                    "query": {
                        "text": professor_name,
                        "schoolID": self.VT_SCHOOL_ID,
                        "fallback": True
                    }
                }
            }

            response = requests.post(
                self.GRAPHQL_URL,
                json=payload,
                headers={
                    'User-Agent': self._get_user_agent(),
                    'Referer': self.REFERER,
                    'Origin': 'https://www.ratemyprofessors.com',
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'Accept-Language': 'en-US,en;q=0.9',
                },
                timeout=self.timeout
            )

            response.raise_for_status()
            data = response.json()

            if 'errors' in data:
                logger.warning(f"RMP GraphQL error: {data['errors']}")
                return None

            edges = (
                data.get('data', {})
                    .get('newSearch', {})
                    .get('teachers', {})
                    .get('edges', [])
            )

            if not edges:
                logger.info(f"No RMP results for: {professor_name}")
                return None

            name_parts = professor_name.strip().lower().split()
            first_name = name_parts[0] if name_parts else ''
            last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''

            for edge in edges:
                node = edge.get('node', {})
                if (node.get('firstName', '').lower() == first_name and
                        node.get('lastName', '').lower() == last_name):
                    logger.info(f"Exact RMP match: {professor_name}")
                    return {
                        'average_rating': node.get('avgRating'),
                        'average_difficulty': node.get('avgDifficulty'),
                    }

            node = edges[0].get('node', {})
            logger.warning(f"Using first RMP result for: {professor_name}")
            return {
                'average_rating': node.get('avgRating'),
                'average_difficulty': node.get('avgDifficulty'),
            }

        except requests.exceptions.Timeout:
            logger.error(f"RMP timeout: {professor_name}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"RMP request error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"RMP scraping error: {str(e)}")
            return None