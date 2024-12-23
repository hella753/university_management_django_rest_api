import os

from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework import serializers
from rest_framework.relations import StringRelatedField
from rest_framework_simplejwt.tokens import RefreshToken
from course.models import Lecture, Course
from course.serilalizers import FacultyDisplaySerializer, \
    DepartmentSerializer, ProfessorSerializer
from user.utils.helpers import validate_passwords, send_reset_email
from user.models import User, Attendance


class CourseSerializer(serializers.ModelSerializer):
    """
    Serializer for the Course model.
    """
    class Meta:
        model = Course
        fields = ["id", "name", "code"]


class LectureSerializer(serializers.ModelSerializer):
    """
    Serializer for the Lecture model.
    """
    professor = ProfessorSerializer()
    course = CourseSerializer()

    class Meta:
        model = Lecture
        fields = "__all__"


class UserDisplaySerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.
    """
    lectures = LectureSerializer(many=True)
    faculty = FacultyDisplaySerializer()
    department = DepartmentSerializer()

    class Meta:
        model = User
        exclude = ["last_login", "groups", "user_permissions", "password"]
        extra_kwargs = {
            "is_superuser": {"read_only": True},
            "date_joined": {"read_only": True},
            "gpa": {"read_only": True},
            "loan": {"read_only": True},
        }


class UserModificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ["last_login", "groups", "user_permissions"]
        extra_kwargs = {
            "password": {'write_only': True, 'required': False},
            'date_joined': {'read_only': True},
            'gpa': {'read_only': True},
            'loan': {'read_only': True},
        }

    def validate(self, data):
        user = self.context.get("request").user
        role = data.get("role")
        faculty = data.get("faculty")
        department = data.get("department")
        is_superuser = data.get("is_superuser")
        scholarship = data.get("government_scholarship")

        if scholarship not in [0.00, 50.00, 70.00, 100.00]:
            raise serializers.ValidationError(
                "Invalid scholarship percentage."
            )

        if faculty and department:
            raise serializers.ValidationError(
                "You can only set either faculty or department."
            )

        if not user.is_superuser:
            if role in [3, 4]:
                raise serializers.ValidationError(
                    "You are not allowed to create this role."
                )
            if role == 2:
                if faculty or department:
                    raise serializers.ValidationError(
                        "You are not allowed to set faculty or "
                        "department for the professor."
                    )
            if is_superuser is True:
                raise serializers.ValidationError(
                    "You are not allowed to create a superuser."
                )
            if faculty and faculty.department != user.department:
                raise serializers.ValidationError(
                    "You are not allowed to create a user in this department."
                )

        password = data.get("password")
        if password:
            validate_password(password)
        return data

    def create(self, validated_data):
        lectures = validated_data.pop("lectures")
        courses = validated_data.pop("courses")
        user = User.objects.create_user(**validated_data)
        if lectures:
            user.lectures.set(lectures)
        if courses:
            user.courses.set(courses)
        return user


class BlacklistTokenSerializer(serializers.Serializer):
    """
    Serializer for blacklisting tokens.
    This serializer is used to validate the data sent to
    the API when a user logs out.
    """
    refresh = serializers.CharField()

    def validate(self, data):
        refresh_token = data.get('refresh')
        if refresh_token:
            refresh_token = RefreshToken(refresh_token)
            refresh_token.blacklist()

        return data

    def create(self, validated_data):
        return validated_data


class ResetPasswordSerializer(serializers.Serializer):
    """
    Serializer for the forgotten password endpoint.
    """
    email = serializers.EmailField(required=True)

    def validate_email(self, email):
        user = User.objects.filter(email=email).first()
        if not user:
            raise serializers.ValidationError("Email does not exist.")
        return email

    def save(self, request):
        email = self.validated_data["email"]
        user = User.objects.get(email=email)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = PasswordResetTokenGenerator().make_token(user)
        url = (f"{request.scheme}://{request.get_host()}/api/user/"
               f"user/reset-password/?uid={uid}&token={token}")
        send_reset_email([email], url)
        return user


class ConfirmResetSerializer(serializers.Serializer):
    """
    Serializer for the password reset endpoint.
    """
    new_password = serializers.CharField(
        style={"input_type": "password"},
        write_only=True,
        required=True,
    )
    confirm_password = serializers.CharField(
        style={"input_type": "password"},
        write_only=True,
        required=True,
    )

    def validate(self, data):
        new_password = data.get("new_password")
        confirm_password = data.get("confirm_password")
        uid = self.context.get("request").query_params.get('uid')
        token = self.context.get("request").query_params.get('token')
        if not uid or not token:
            raise serializers.ValidationError("Missing uid or token.")
        try:
            uid = urlsafe_base64_decode(uid)
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, User.DoesNotExist):
            raise serializers.ValidationError("Invalid user.")
        if not PasswordResetTokenGenerator().check_token(user, token):
            raise serializers.ValidationError("Invalid token.")
        validate_passwords(new_password, confirm_password)
        return data

    def save(self):
        user = User.objects.get(
            pk=urlsafe_base64_decode(
                self.context.get("request").query_params.get("uid")
            )
        )
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user


class AttendanceSerializer(serializers.ModelSerializer):
    """
    Serializer for the Attendance model.
    """
    lecture = StringRelatedField()
    user = StringRelatedField()

    class Meta:
        model = Attendance
        fields = "__all__"
        extra_kwargs = {
            'first_hour': {'required': False},
            'second_hour': {'required': False},
            'third_hour': {'required': False},
        }

    def validate(self, data):
        lecture = data.get("lecture")
        request = self.context.get("request")
        student = data.get("user")
        date = data.get("date")
        if request.user != lecture.professor:
            raise serializers.ValidationError(
                "You are not the professor of this lecture."
            )
        if student not in lecture.users.all():
            raise serializers.ValidationError(
                "This user is not enrolled in this lecture."
            )
        if date.weekday() + 1 != lecture.day:
            raise serializers.ValidationError(
                "The date does not match the lecture day."
            )
        return data
