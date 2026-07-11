"""
Input Validation
Validates and parses user input
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class InputValidator:
    """Validates and parses course search input"""
    
    @staticmethod
    def validate_and_parse(
        professor: str = None,
        department: str = None,
        course_id: str = None,
        query: str = None
    ) -> Optional[dict]:
        """
        Validate and parse user input
        
        Args:
            professor: Professor name
            department: Department code
            course_id: Course ID
            query: Full query string "First Last DEPT 1234"
        
        Returns:
            Dict with validated data or None if invalid
        """
        # Try parsing full query first
        if query:
            parts = query.strip().split()
            if len(parts) >= 4:
                # Assume format: First Last DEPT XXXX
                dept = parts[-2].upper()
                course = parts[-1]
                prof = ' '.join(parts[:-2]).lower()
                
                # Basic validation
                if len(dept) >= 2 and len(dept) <= 5 and course.isdigit() and len(course) == 4:
                    return {
                        'professor': prof,
                        'department': dept.lower(),
                        'course_id': course,
                    }
            return None
        
        # Validate individual parameters
        if not all([professor, department, course_id]):
            logger.warning("Missing required parameters")
            return None
        
        professor = professor.strip().lower()
        department = department.strip().upper()
        course_id = course_id.strip()
        
        # Basic validation
        if not professor or len(department) < 2 or not course_id.isdigit() or len(course_id) != 4:
            return None
        
        return {
            'professor': professor,
            'department': department.lower(),
            'course_id': course_id,
        }