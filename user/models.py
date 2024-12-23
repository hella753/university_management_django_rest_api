from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db import models
from versatileimagefield.fields import VersatileImageField
from course.models import Faculty, Grade
from user.choices import ROLES
from user.managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model
    """
    first_name = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        verbose_name=_("სახელი")
    )
    last_name = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        verbose_name=_("გვარი")
    )
    username = models.CharField(
        max_length=30,
        unique=True,
        verbose_name=_("მომხმარებლის სახელი")
    )
    email = models.EmailField(
        unique=True,
        verbose_name=_("ელ. ფოსტა")
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("აქტიურია")
    )
    is_staff = models.BooleanField(
        default=False,
        verbose_name=_("სტაფია")
    )
    is_superuser = models.BooleanField(
        default=False,
        verbose_name=_("სუპერიუზერია")
    )
    date_joined = models.DateTimeField(
        verbose_name=_("რეგისტრაციის თარიღი"),
        default=timezone.now
    )
    image = VersatileImageField(
        upload_to="images/users/",
        blank=True,
        null=True,
        verbose_name=_("ფოტოსურათი")
    )
    identity_number = models.CharField(
        max_length=11,
        blank=True,
        null=True,
        verbose_name=_("პირადი ნომერი")
    )
    enrollment_year = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        verbose_name=_("ჩარიცხვის წელი")
    )
    phone = models.CharField(
        max_length=11,
        blank=True,
        null=True,
        verbose_name=_("ტელეფონის ნომერი")
    )
    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name=_("ფაკულტეტი")
    )
    date_of_birth = models.DateField(
        blank=True,
        null=True,
        verbose_name=_("დაბადების თარიღი")
    )
    lectures = models.ManyToManyField(
        "course.Lecture",
        blank=True,
        verbose_name=_("ლექციები"),
        related_name="users"
    )
    courses = models.ManyToManyField(
        "course.Course",
        blank=True,
        verbose_name=_("კურსები"),
        related_name="users"
    )
    government_scholarship = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name=_("სახელმწიფო გრანტი"),
        validators=[MinValueValidator(0.00), MaxValueValidator(100.00)]
    )
    loan = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_("ვალი"),
    )
    role = models.IntegerField(
        choices=ROLES,
        verbose_name=_("როლი")
    )
    department = models.ForeignKey(
        "course.Department",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name=_("დეპარტამენტი")
    )

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", "first_name", "last_name"]

    @property
    def year(self):
        current_year = timezone.now().year
        year = self.enrollment_year + (current_year - self.enrollment_year)
        return year

    @property
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.username


class Attendance(models.Model):
    """
    Attendance model
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("მომხმარებელი")
    )
    lecture = models.ForeignKey(
        "course.Lecture",
        on_delete=models.CASCADE,
        verbose_name=_("ლექცია")
    )
    date = models.DateField(
        verbose_name=_("თარიღი")
    )
    first_hour = models.BooleanField(
        default=False,
        verbose_name=_("პირველი საათი")
    )
    second_hour = models.BooleanField(
        default=False,
        verbose_name=_("მეორე საათი")
    )
    third_hour = models.BooleanField(
        default=False,
        verbose_name=_("მესამე საათი")
    )

    class Meta:
        unique_together = ["user", "lecture", "date"]

    def __str__(self):
        return f"{self.user} - {self.lecture} - {self.date}"


class GoogleOAuthToken(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="google_oauth_token",
        verbose_name=_("მომხმარებელი")
    )
    access_token = models.TextField(verbose_name=_("წვდომის ტოკენი"))
    refresh_token = models.TextField(verbose_name=_("განახლების ტოკენი"))
    token_expiry = models.DateTimeField(verbose_name=_("ტოკენის ვადა"))
    token_type = models.CharField(max_length=100, default="Bearer", verbose_name=_("ტოკენის ტიპი"))

    def is_valid(self):
        """
        Checks if the access token is still valid.
        """
        return timezone.now() < self.token_expiry
