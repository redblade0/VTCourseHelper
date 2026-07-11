"""
Cache Model
Single combined cache table per search query (professor + course).
"""

import json
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def utc_now() -> datetime:
    """Get current UTC time"""
    return datetime.now(timezone.utc)


class CourseCache(db.Model):
    """
    Combines cache into single search: one row per professor, course pair
    """

    __tablename__ = 'course_cache'

    id = db.Column(db.Integer, primary_key=True)

    professor_name = db.Column(db.String(255), nullable=False, index=True)
    course_id = db.Column(db.String(50), nullable=False, index=True)

    # RMP data
    average_rating = db.Column(db.Float, nullable=True)
    average_difficulty = db.Column(db.Float, nullable=True)

    # Reddit data
    reddit_posts = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('professor_name', 'course_id', name='uq_professor_course'),
        db.Index('idx_professor_course_updated', 'professor_name', 'course_id', 'updated_at'),
    )

    def is_expired(self, expiry_delta) -> bool:
        return utc_now() - self.updated_at > expiry_delta

    def get_reddit_posts(self) -> list:
        """Deserialize reddit_posts JSON column"""
        if not self.reddit_posts:
            return []
        try:
            return json.loads(self.reddit_posts)
        except Exception:
            return []

    def set_reddit_posts(self, posts: list) -> None:
        """Serialize reddit_posts to JSON column"""
        self.reddit_posts = json.dumps(posts) if posts else None

    def to_dict(self) -> dict:
        return {
            'professor_name': self.professor_name,
            'course_id': self.course_id,
            'average_rating': self.average_rating,
            'average_difficulty': self.average_difficulty,
            'reddit_posts': self.get_reddit_posts(),
            'updated_at': self.updated_at.isoformat(),
        }

    def __repr__(self) -> str:
        return f'<CourseCache {self.professor_name} / {self.course_id}>'