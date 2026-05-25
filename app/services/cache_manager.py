
import logging
from flask import current_app
from app.models import db, RMPCache, RedditCache
from app.models.cache import utc_now

logger = logging.getLogger(__name__)

class CacheManager:
    """Manages cache"""

    @staticmethod
    def get_rmp(professor_name: str) -> dict:
        """
        Gets RMP cache data if valid
        """

        try:
            entry = RMPCache.query.filter_by(professor_name=professor_name).first()

            if not entry:
                return None
            
            if entry.is_expired(current_app.config['CACHE_EXPIRY']):
                db.session.delete(entry)
                db.session.commit()
                logger.info(f"Expired RMP cache: {professor_name}")
                return None
            
            return {
                'average_rating': entry.average_rating,
                'average_difficulty': entry.average_difficulty,
            }

        except Exception as e:
            logger.error(f"RMP chache get error: {str(e)}")
            return None
        
    @staticmethod
    def set_rmp(professor_name: str, data: dict) -> bool:
        """Stores RMP cache data"""
        try:
            existing = RMPCache.query.filter_by(professor_name=professor_name).first()

            if existing:
                existing.average_rating = data.get('average_rating')
                existing.average_difficulty = data.get('average_difficulty')
            else:
                existing = RMPCache(
                    professor_name=professor_name,
                    average_rating=data.get('average_rating'),
                    average_difficulty=data.get('average_difficulty'),
                )
                db.session.add(existing)

            db.session.commit()
            logger.info(f"Cached RMP: {professor_name}")
            return True

        except Exception as e:
            logger.error(f"RMP cache error: {e}")
            db.session.rollback()
            return False
        
    @staticmethod
    def get_reddit(course_id: str) -> dict:
        """Get Reddit cache data if valid"""
        try:
            entries = RedditCache.query.filter_by(course_id=course_id).all()

            if not entries:
                return None

            valid = [e for e in entries if not e.is_expired(current_app.config['CACHE_EXPIRY'])]
                
            if not valid:
                for e in entries:
                    db.session.delete(e)
                db.session.commit()
                logger.info(f"Expired Reddit cache: {course_id}")
                return None
            
            return {'titles': [e.reddit_title for e in valid]}
        
        except Exception as e:
            logger.error(f"Reddit cache get error: {str(e)}")
            return None
        
    @staticmethod
    def set_reddit(course_id: str, titles: list) -> bool:
        """Stores Reddit cache data"""
        try:
            for title in titles:
                RedditCache.query.filter_by(course_id=course_id, reddit_title=title).delete()
                entry = RedditCache(course_id=course_id, reddit_title=title)
                db.session.add(entry)
            
            db.session.commit()
            logger.info(f"Cached {len(titles)} Reddit posts: {course_id}")
            return True

        except Exception as e:
            logger.error(f"Reddit cache set error: {str(e)}")
            db.session.rollback()
            return False