
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def utc_now() -> datetime:
    """Get current UTC time (timezone-aware)"""
    return datetime.now(timezone.utc)



class RMPCache(db.Model):
    """Cache for Rate My Professor data"""

    __tablename__ = 'rmp_cache'

    id = db.Column(db.Integer, primary_key=True)
    professor_name = db.Column(db.String(255), unique=True, nullable=False, index=True)
    average_rating = db.Column(db.Float)
    average_difficulty = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    __table_args__ = (
        db.Index('idx_professor_updated', 'professor_name', 'updated_at'),
    )
    
    def is_expired(self, expiry_delta) -> bool:
        """
        Checks if cache entry is expired
        @args: expiry_delta: the ttl for cached data is 7 days
        @return: True if expired
        """
        return utc_now() - self.updated_at > expiry_delta
    
    def to_dict(self) -> dict:
        """convert to dictionary"""
        return {
            'id': self.id,
            'professor_name': self.professor_name,
            'average_rating': self.average_rating,
            'average_difficulty': self.average_difficulty,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }
    
    def __repr__(self) -> str:
        return f"<RMPCache {self.professor_name}>"
    
class RedditCache(db.Model):
    """Cache for Reddit disscussion posts"""

    __tablename__ = 'reddit_cache'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.String(50), nullable=False, index=True)
    reddit_title = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    __table_args__ = (
        db.Index('idx_course_updated', 'course_id', 'updated_at'),
    )

    def is_expired(self, expiry_delta) -> bool:
        """
        Checks if cache entry is expired
        @args: expiry_delta: the ttl for cached data is 7 days
        @return: True if expired
        """
        return utc_now() - self.updated_at > expiry_delta
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'course_id': self.course_id,
            'reddit_title': self.reddit_title,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }
    
    def __repr__(self) -> str:
        return f'<RedditCache {self.course_id}>'