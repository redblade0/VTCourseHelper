
import re
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

class InputValidator:
    """Validates and parses course search input"""

    PROFESSOR_PATTERN = re.compile(r"^([A-Za-z\-']+)\s+([A-Za-z\-'\s]+)$") # First last name
    DEPARTMENT_PATTERN = re.compile(r"^[A-Z]{2,5}$") # 2-5 uppcase letters
    COURSE_ID_PATTERN = re.compile(r"^\d{4}$") # 4 digits

    FULL_QUERY_PATTERN = re.compile(
        r"^([A-Za-z\-']+)\s+([A-Za-z\-'\s]+?)\s+([A-Z]{2,5})\s+(\d{4})$"
    )

    @staticmethod
    def validate_professor_name(name: str) -> Tuple[bool, Optional[str]]:
        """
        Validates the professor name format
        @args: name: Professor name (ex. Arthur Ball)
        @return: Tuple of valid_name, name in lower case
        """

        if not name or not isinstance(name, str):
            return False, None
        
        name = name.strip()

        if not InputValidator.PROFESSOR_PATTERN.match(name):
            logger.warning(f"Invalid professor format: {name}")
            return False, None
        
        return True, name.lower()
    
    @staticmethod
    def validate_department(dept: str) -> Tuple[bool, Optional[str]]:
        """
        Validates a department name format
        @args: dept: Department name (ex. MATH, ECE)
        @return: Tuple of valid_department, department in lower case
        """
        if not dept or not isinstance(dept, str):
            return False, None
        
        dept = dept.strip().upper()

        if not InputValidator.DEPARTMENT_PATTERN.match(dept):
            logger.warning(f"Invalid department format: {dept}")
            return False, None
        
        return True, dept.lower()
    
    @staticmethod
    def validate_course_id(course_id: str) -> Tuple[bool, Optional[str]]:
        """
        Validates a course id format
        @args: course_id: Course ID (ex. 1004, 4425)
        @return: tuple of valid course id, course id in lower
        """
    
        if not course_id or not isinstance(course_id, str):
            return False, None
        
        course_id = course_id.strip()

        if not InputValidator.COURSE_ID_PATTERN.match(course_id):
            logger.warning(f"Invalid course id format: {course_id}")
            return False, None
        
        return True, course_id.lower()
    

    