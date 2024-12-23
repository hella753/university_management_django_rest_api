import datetime
from django.db import models
from django.utils.translation import gettext_lazy as _
from course.choices import DAYS_OF_WEEK
from course.managers import CourseManager, LectureManager


class TimestampedModel(models.Model):
    """
    Abstract model that includes created_at and updated_at fields
    """
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("შეიქმნა")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("განახლდა")
    )

    class Meta:
        abstract = True


class Department(TimestampedModel):
    """
    Department model which includes name and code
    """
    name = models.CharField(
        max_length=50,
        verbose_name=_("დეპარტამენტის სახელი")
    )
    code = models.CharField(
        max_length=10,
        verbose_name=_("დეპარტამენტის კოდი")
    )

    def __str__(self):
        return self.name


class Faculty(TimestampedModel):
    """
    Faculty model connecting to Department
    """
    name = models.CharField(
        max_length=50,
        verbose_name=_("ფაკულტეტის სახელი")
    )
    code = models.CharField(
        max_length=10,
        verbose_name=_("ფაკულტეტის კოდი")
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        verbose_name=_("დეპარტამენტი")
    )

    def __str__(self):
        return self.name


class Course(TimestampedModel):
    """
    Course model with prerequisites
    """
    name = models.CharField(
        max_length=50,
        verbose_name=_("კურსის სახელი")
    )
    code = models.CharField(
        max_length=10,
        verbose_name=_("კურსის კოდი")
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        verbose_name=_("დეპარტამენტი")
    )
    credits = models.PositiveSmallIntegerField(
        verbose_name=_("კრედიტები"),
        default=5
    )
    prerequisites = models.ManyToManyField(
        "self",
        verbose_name=_("პრერეკვიზიტები",),
        blank=True,
        symmetrical=False
    )

    objects = CourseManager()

    def __str__(self):
        return self.name


class Lecture(TimestampedModel):
    """
    Lecture model with every attribute needed for a lecture
    """
    name = models.CharField(
        max_length=50,
        verbose_name=_("ლექციის სახელი")
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        verbose_name=_("კურსი")
    )
    day = models.IntegerField(
        verbose_name=_("დღე"),
        choices=DAYS_OF_WEEK,
        null=True,
        blank=True
    )
    start_time = models.TimeField(
        verbose_name=_("დაწყების დრო"),
        null=True,
        blank=True
    )
    end_time = models.TimeField(
        verbose_name=_("დასრულების დრო"),
        default=datetime.time(0, 0, 0),
        null=True,
        blank=True
    )
    location = models.ForeignKey(
        "course.Auditorium",
        verbose_name=_("აუდიტორია"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    professor = models.ForeignKey(
        "user.User",
        on_delete=models.CASCADE,
        verbose_name=_("ლექტორი"),
        related_name="prof_lectures",
        null=True,
        blank=True
    )
    uni_year = models.PositiveSmallIntegerField(
        verbose_name=_("სასწავლო წელი"),
    )
    capacity = models.PositiveIntegerField(
        default=30,
        verbose_name=_("სტუდენტების დასაშვები რაოდენობა"),
        null=True,
        blank=True
    )
    syllabus = models.FileField(
        upload_to="uploaded_syllabus/",
        verbose_name=_("სილაბუსი"),
        blank=True,
        null=True,
    )
    resources = models.ManyToManyField(
        "course.Resource",
        verbose_name=_("რესურსები"),
        blank=True
    )
    semester = models.ForeignKey(
        "course.Semester",
        verbose_name=_("სემესტრი"),
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    # Start day is for the first day of the lecture
    # It is used for the Google Calendar API
    start_day = models.DateField(
        verbose_name=_("ლექციის პირველი დღე"),
        default=datetime.date.today,
        null=True,
        blank=True
    )
    start_day_second = models.DateField(
        verbose_name=_("ლექციის პირველი დღე შუალედურების შემდეგ"),
        default=datetime.date.today,
        null=True,
        blank=True
    )

    objects = LectureManager()

    def __str__(self):
        return self.name


class Grade(TimestampedModel):
    """
    Grade model for professors to grade students
    """
    student = models.ForeignKey(
        "user.User",
        on_delete=models.CASCADE,
        verbose_name=_("სტუდენტი")
    )
    grade = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name=_("ქულა")
    )
    assignment = models.ForeignKey(
        "course.Assignment",
        on_delete=models.CASCADE,
        verbose_name=_("დავალება"),
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.grade}"


class Assignment(TimestampedModel):
    """
    Assignment model for professors to create assignments
    """
    name = models.CharField(
        max_length=50,
        verbose_name=_("დავალების სახელი")
    )
    description = models.TextField(
        verbose_name=_("აღწერა"),
        blank=True,
        null=True
    )
    lecture = models.ForeignKey(
        "course.Lecture",
        on_delete=models.CASCADE,
        verbose_name=_("ლექცია")
    )
    due_date = models.DateTimeField(
        verbose_name=_("დედლაინი")
    )
    max_points = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name=_("მაქსიმალური ქულათა რაოდენობა")
    )

    def __str__(self):
        return self.name


class Resource(TimestampedModel):
    """
    Resource model for lectures pdfs, slides, etc.
    """
    name = models.CharField(
        max_length=50,
        verbose_name=_("რესურსის სახელი")
    )
    url = models.URLField(
        verbose_name=_("ბმული"),
        blank=True,
        null=True
    )
    file = models.FileField(
        upload_to="resources/",
        verbose_name=_("ფაილი"),
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name


class Auditorium(TimestampedModel):
    """
    Auditorium model for managing auditoriums
    and validating lecture locations.
    """
    name = models.CharField(
        max_length=50,
        verbose_name=_("აუდიტორიის სახელი")
    )
    capacity = models.PositiveIntegerField(
        verbose_name=_("ტევადობა"),
        default=30
    )
    has_computers = models.BooleanField(
        verbose_name=_("კომპიუტერებით"),
        default=False
    )

    def __str__(self):
        return self.name


class GradeRecord(TimestampedModel):
    """
    GradeRecord model for storing total grades
    of students in lectures.
    Has a failed field and is_active Field.
    Is_active is for the lectures that student
    took but then retook the different lecture
    of that same course.
    """
    student = models.ForeignKey(
        "user.User",
        on_delete=models.CASCADE,
        verbose_name=_("სტუდენტი")
    )
    lecture = models.ForeignKey(
        "course.Lecture",
        on_delete=models.CASCADE,
        verbose_name=_("ლექცია")
    )
    grade = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name=_("ქულა")
    )
    failed = models.BooleanField(
        verbose_name=_("ჩაიჭრა"),
        default=False
    )
    is_active = models.BooleanField(
        verbose_name=_("აქტიურია"),
        default=True
    )

    def __str__(self):
        return f"{self.student} - {self.lecture} - {self.grade}"


class Semester(TimestampedModel):
    """
    Semester model for managing semesters
    to dynamically create semesters for each year.
    """
    year = models.CharField(
        verbose_name=_("წელი"),
        max_length=150,
        help_text=_("Example: 2020-2021")
    )
    semester = models.PositiveSmallIntegerField(
        verbose_name=_("სემესტრი"),
        choices=(
            (1, _("შემოდგომა")),
            (2, _("გაზაფხული")))
    )
    start_date = models.DateField(
        verbose_name=_("დაწყების თარიღი")
    )
    end_date = models.DateField(
        verbose_name=_("დასრულების თარიღი")
    )
    midterm_start = models.DateField(
        verbose_name=_("შუალედური გამოცდების დაწყების თარიღი")
    )
    final_start = models.DateField(
        verbose_name=_("დასკვნითი გამოცდების დაწყების თარიღი")
    )

    def __str__(self):
        return f"{self.year} - {self.semester}"


class AssignmentSubmission(TimestampedModel):
    """
    AssignmentSubmission model for students to submit
    their assignments.
    """
    student = models.ForeignKey(
        "user.User",
        on_delete=models.CASCADE,
        verbose_name=_("სტუდენტი")
    )
    assignment = models.ForeignKey(
        "course.Assignment",
        on_delete=models.CASCADE,
        verbose_name=_("დავალება")
    )
    file = models.FileField(
        upload_to="assignment_submissions/",
        verbose_name=_("ფაილი")
    )
