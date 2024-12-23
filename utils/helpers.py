import datetime
from course.models import Semester


def get_semester():
    """
    This function returns the current semester.
    :return: Semester object
    """
    now = datetime.datetime.now()
    semester = Semester.objects.filter(
        start_date__lte=now,
        end_date__gte=now
    ).first()
    return semester
