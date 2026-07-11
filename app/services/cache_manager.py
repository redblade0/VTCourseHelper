"""
Cache Manager
Single table for all cache operations — one row per (professor, course) search.
"""

import logging
from flask import current_app
from app.models import db, CourseCache
from app.models.cache import utc_now

logger = logging.getLogger(__name__)


class CacheManager:

    @staticmethod
    def get(professor_name: str, course_id: str) -> CourseCache:
        """
        Get a non-expired cache entry for professor + course pair.
        Returns the ORM object or None.
        """
        try:
            entry = (
                db.session.query(CourseCache)
                .filter_by(professor_name=professor_name, course_id=course_id)
                .first()
            )
            if not entry:
                return None

            if entry.is_expired(current_app.config['CACHE_EXPIRY']):
                db.session.delete(entry)
                db.session.commit()
                logger.info(f"Expired cache: {professor_name} / {course_id}")
                return None

            return entry

        except Exception as e:
            logger.error(f"Cache get error: {str(e)}")
            return None

    @staticmethod
    def set_rmp(professor_name: str, course_id: str, rmp_data: dict) -> bool:
        """
        Upsert RMP data into the combined cache row.
        Creates row if it doesn't exist yet.
        """
        try:
            entry = (
                db.session.query(CourseCache)
                .filter_by(professor_name=professor_name, course_id=course_id)
                .first()
            )
            if entry:
                entry.average_rating = rmp_data.get('average_rating')
                entry.average_difficulty = rmp_data.get('average_difficulty')
            else:
                entry = CourseCache(
                    professor_name=professor_name,
                    course_id=course_id,
                    average_rating=rmp_data.get('average_rating'),
                    average_difficulty=rmp_data.get('average_difficulty'),
                )
                db.session.add(entry)

            db.session.commit()
            logger.info(f"Cached RMP: {professor_name} / {course_id}")
            return True

        except Exception as e:
            logger.error(f"Cache set_rmp error: {str(e)}")
            db.session.rollback()
            return False

    @staticmethod
    def set_reddit(professor_name: str, course_id: str, posts: list) -> bool:
        """
        Upsert Reddit posts into the combined cache row.
        Creates the row if it doesn't exist yet.
        """
        try:
            entry = (
                db.session.query(CourseCache)
                .filter_by(professor_name=professor_name, course_id=course_id)
                .first()
            )
            if entry:
                entry.set_reddit_posts(posts)
            else:
                entry = CourseCache(
                    professor_name=professor_name,
                    course_id=course_id,
                )
                entry.set_reddit_posts(posts)
                db.session.add(entry)

            db.session.commit()
            logger.info(f"Cached {len(posts)} Reddit posts: {professor_name} / {course_id}")
            return True

        except Exception as e:
            logger.error(f"Cache set_reddit error: {str(e)}")
            db.session.rollback()
            return False