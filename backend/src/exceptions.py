from file_utils import append_to_log_file

class DepartmentDoesNotExist(Exception):
    """
    Exception raised when the department doesn't exist on the UG Bulletin webpage
    """
    def __init__(self, department):
        self.department = department
        super().__init__(str(self))

    def __str__(self):
        return f"{self.department} doesn't exist"

    def log(self):
        append_to_log_file("department-exceptions.txt", self.department)

class UnknownRequisite(Exception):
    """
    Exception raised when some requisite text is not matched
    """
    def __init__(self, text, course_number):
        self.text = text
        self.course_number = course_number
        super().__init__(str(self))

    def __str__(self):
        return f"{self.course_number}: {self.text}"

    def log(self):
        append_to_log_file("unknown-requisites.txt", str(self))

class UnmatchedCourseLine(Exception):
    """
    Exception raised some text is not matched by the course parser
    """
    def __init__(self, text, course_number):
        self.text = text
        self.course_number = course_number
        super().__init__(str(self))

    def __str__(self):
        return f"{self.course_number}: {self.text}"

    def log(self):
        append_to_log_file("unmatched-lines.txt", str(self))
