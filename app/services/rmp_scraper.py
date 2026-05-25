
import requests
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class RMPScraper:
    """Scraper for Rate My Professor data"""

    GRAPHQL_URL = "https://www.ratemyprofessors.com/graphql"
    REFERER = "https://www.ratemyprofessors.com"
    VT_SCHOOL_ID = 1349 # this can change, if teachers don't look right, change this

    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    ]

    def __init__(self, timeout:int = 10) -> str:
        self.timeout = timeout
        self.user_agent_idx = 0

    def _get_user_agent(self) -> str:
        """Rotates user agents"""
        agent = self.USER_AGENTS[self.user_agent_idx % len(self.USER_AGENTS)]

        self.user_agent_idx += 1
        return agent
    
    def scrape(self, professor_name: str) -> Optional[Dict[str, Any]]:
        """
        Scrapes professor data from rate my professor
        @args: professor_name: professor (ex. Arthur Ball)
        @return: dict with rating and difficuly or None
        """
        try:
            logger.info(f"Scraping RMP: {professor_name}")

            query = """
            query TeacherSearch($query: String!, $schoolID: Int!) {
                            search(query: $query, schoolID: $schoolID) {
                                teachers(first: 10) {
                                    edges {
                                        node {
                                            firstName
                                            lastName
                                            avgRating
                                            avgDifficulty
                                        }
                                    }
                                }
                            }
                        }
            """

            response = requests.post(
                self.GRAPHQL_URL,
                json={
                    'query':query,
                    'variables': {
                        'query': professor_name,
                        'schoolID': self.VT_SCHOOL_ID
                    }
                },
                headers={
                    'User-Agent': self._get_user_agent(),
                    'Referer': self.REFERER,
                    'Content-Type': 'applications/json',
                },
                timeout=self.timeout
            )

            response.raise_for_status()
            data = response.json()

            if 'errors' in data:
                logger.warning(f"RMP GraphQL error: {data['errors']}")
                return None
            
            teachers = data.get('data', {}).get('search', {}).get('teachers', {}).get('edges', [])

            if not teachers:
                logger.info(f"No RMP data: {professor_name}")
                return None
            
            name_parts = professor_name.strip().lower().split()
            first_name = name_parts[0]
            last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''

            for teacher_edge in teachers:
                teacher = teacher_edge.get('node', {})
                if (teacher.get('firstName', '').lower() == first_name and
                    teacher.get('lastName', '').lower() == last_name):
                    
                    result = {
                        'average_rating': teacher.get('avgRating'),
                        'average_difficulty': teacher.get('avgDifficulty'),
                    }
                    logger.info(f"Found RMP data: {professor_name}")
                    return result
            
            if teachers:
                teacher = teachers[0].get('node', {})
                logger.warning(f"Using first RMP result for {professor_name}")
                return {
                    'average_rating': teacher.get('avgRating'),
                    'average_difficulty': teacher.get('avgDifficulty'),
                }
            
            return None
        
        except requests.exceptions.Timeout:
            logger.error(f"RMP timeout: {professor_name}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"RMP request error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"RMP scraping error: {str(e)}")
            return None