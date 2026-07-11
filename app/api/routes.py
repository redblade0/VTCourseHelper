"""
REST API Routes
"""

import logging
from flask import Blueprint, request, jsonify, current_app

from app.models.cache import utc_now
from app.services.rmp_scraper import RMPScraper
from app.services.reddit_scraper import RedditScraper
from app.services.cache_manager import CacheManager
from app.utils.validator import InputValidator

logger = logging.getLogger(__name__)
api = Blueprint('api', __name__, url_prefix='/api')


@api.route('/search', methods=['GET'])
def search():
    """
    Search for professor ratings and course discussions
    ---
    parameters:
      - name: query
        in: query
        type: string
        required: true
        description: Full search query e.g. "Arthur Ball ECE 1004"
        example: Arthur Ball ECE 1004
    responses:
      200:
        description: Search results
      400:
        description: Invalid input
      500:
        description: Server error
    """
    try:
        query = request.args.get('query', '').strip()
        professor = request.args.get('professor', '').strip()
        department = request.args.get('department', '').strip()
        course = request.args.get('course', '').strip()

        parsed = InputValidator.validate_and_parse(
            professor=professor or None,
            department=department or None,
            course_id=course or None,
            query=query or None,
        )

        if not parsed:
            return jsonify({
                'error': 'Invalid input format',
                'message': 'Use query="First Last DEPT 1234"',
                'example': 'query=Arthur Ball ECE 1004',
            }), 400

        prof_name = parsed['professor']
        dept_code = parsed['department']
        course_code = parsed['course_id']
        course_key = f"{dept_code} {course_code}"

        logger.info(f"Search: {prof_name} / {course_key}")

        # --- Check combined cache ---
        cached = CacheManager.get(prof_name, course_key)

        # RMP: use cache or scrape
        rmp_data = None
        if cached and cached.average_rating is not None:
            rmp_data = {
                'average_rating': cached.average_rating,
                'average_difficulty': cached.average_difficulty,
            }
        else:
            scraped = RMPScraper().scrape(prof_name)
            if scraped:
                CacheManager.set_rmp(prof_name, course_key, scraped)
                rmp_data = scraped

        # Reddit: use cache or scrape
        reddit_data = None
        if cached and cached.get_reddit_posts():
            reddit_data = {'posts': cached.get_reddit_posts()}
        else:
            scraped = RedditScraper().scrape(course_key)
            if scraped and scraped.get('posts'):
                CacheManager.set_reddit(prof_name, course_key, scraped['posts'])
                reddit_data = scraped

        return jsonify({
            'professor': prof_name,
            'department': dept_code,
            'course_id': course_code,
            'timestamp': utc_now().isoformat(),
            'data': {
                'rmp': _format_rmp(rmp_data, prof_name),
                'reddit': _format_reddit(reddit_data, dept_code, course_code),
            }
        }), 200

    except Exception as e:
        import traceback
        logger.error(f"Search error: {e}\n{traceback.format_exc()}")
        return jsonify({'error': 'Internal server error', 'message': str(e)}), 500


@api.route('/health', methods=['GET'])
def health():
    """
    Health check
    ---
    responses:
      200:
        description: API is healthy
    """
    return jsonify({'status': 'healthy', 'timestamp': utc_now().isoformat()}), 200


def _format_rmp(data: dict, professor_name: str) -> dict:
    if data:
        return {
            'found': True,
            'average_rating': data.get('average_rating'),
            'average_difficulty': data.get('average_difficulty'),
        }
    return {'found': False, 'message': f'No Rate My Professor data found for {professor_name}'}


def _format_reddit(data: dict, dept: str, course: str) -> dict:
    if data and data.get('posts'):
        return {
            'found': True,
            'count': len(data['posts']),
            'posts': data['posts'],
        }
    return {
        'found': False,
        'message': f'No Reddit discussions found for {dept.upper()} {course}',
        'posts': [],
        'count': 0,
    }