from rest_framework import serializers
from course.models import *
from user.models import User
from utils.helpers import get_semester
from user.tasks import add_grade_record


class LectureModificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lecture
        fields = "__all__"
        extra_kwargs = {
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True}
        }

        def validate(self, data):
            auditorium = data["location"]
            start_time = data["start_time"]
            end_time = data["end_time"]
            capacity = data["capacity"]
            professor = data["professor"]
            day = data["day"]
            semester = get_semester()

            if Lecture.objects.filter(
                    location=auditorium,
                    start_time__lt=end_time,
                    end_time__gt=start_time,
                    day=day,
                    semester=semester
            ).exists():
                raise serializers.ValidationError(
                    "This auditorium is already reserved."
                )

            if start_time >= end_time:
                raise serializers.ValidationError(
                    "Start time must be before the end time."
                )

            if auditorium.capacity < capacity:
                raise serializers.ValidationError(
                    "Auditorium capacity is not enough."
                )

            if not professor.role == 2:
                raise serializers.ValidationError(
                    "This user is not a professor."
                )

            if professor.lectures.filter(
                    semester=semester,
                    start_time__lt=end_time,
                    end_time__gt=start_time,
                    day=day
            ).exists():
                raise serializers.ValidationError(
                    "This professor already has a lecture."
                )

            return data


class DepartmentSerializer(serializers.ModelSerializer):
    """
    This class is used to serialize the Department model.
    """
    class Meta:
        model = Department
        fields = ["id", "name", "code"]


class PrerequisiteSerializer(serializers.ModelSerializer):
    """
    This class is used to serialize the Course model for prerequisites.
    """
    class Meta:
        model = Course
        fields = "__all__"


class CourseModificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = "__all__"
        extra_kwargs = {
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True}
        }


class CourseDisplaySerializer(serializers.ModelSerializer):
    """
    This class is used to serialize the Course model.
    """
    prerequisites = PrerequisiteSerializer(many=True)
    department = DepartmentSerializer()

    class Meta:
        model = Course
        fields = "__all__"


class ProfessorSerializer(serializers.ModelSerializer):
    """
    This class is used to serialize the Professor model.
    """
    class Meta:
        model = User
        exclude = [
            "last_login",
            "groups",
            "user_permissions",
            "is_superuser",
            "is_staff",
            "is_active",
            "password",
            "date_joined",
            "loan",
            "role",
            "faculty",
            "department",
            "lectures",
            "courses"
        ]


class LectureDisplaySerializer(serializers.ModelSerializer):
    """
    This class is used to serialize the Lecture model.
    """
    professor = ProfessorSerializer()
    course = CourseDisplaySerializer()

    class Meta:
        model = Lecture
        fields = "__all__"


class LectureProfessorSerializer(serializers.ModelSerializer):
    """
    This class is used to serialize the Lecture model for the professor
    For update actions.
    """
    class Meta:
        model = Lecture
        fields = ["syllabus", "resources"]


class FacultyModificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty
        fields = "__all__"
        extra_kwargs = {
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True}
        }


class FacultyDisplaySerializer(serializers.ModelSerializer):
    """
    This class is used to serialize the Faculty model.
    """
    department = DepartmentSerializer()

    class Meta:
        model = Faculty
        fields = "__all__"


class AssignmentModificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = "__all__"
        extra_kwargs = {
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True}
        }

    def validate(self, data):
        lecture = data["lecture"]
        name = data["name"]
        max_points = data["max_points"]

        if lecture not in Lecture.objects.filter(
                professor=self.context["request"].user
        ) and not self.context["request"].user.role == 3:
            raise serializers.ValidationError("This is not your lecture.")

        if name == "":
            raise serializers.ValidationError("Name cannot be empty.")

        if max_points < 0:
            raise serializers.ValidationError("Max points cannot be negative.")
        assignment_sum = (
            Assignment.objects.filter(
                lecture=lecture
            ).aggregate(
                models.Sum("max_points"))
        )["max_points__sum"]

        if self.context.get("view").action == "update":
            assignment_sum -= self.instance.max_points

        if assignment_sum is not None and assignment_sum + max_points > 100:
            raise serializers.ValidationError(
                "Total max points cannot be more than 100."
            )
        return data


class AssignmentDisplaySerializer(serializers.ModelSerializer):
    """
    This class is used to serialize the Assignment model.
    """
    lecture = LectureDisplaySerializer()

    class Meta:
        model = Assignment
        fields = "__all__"


class StudentSerializer(serializers.ModelSerializer):
    """
    This class is used to serialize the Professor model.
    """
    class Meta:
        model = User
        exclude = [
            "last_login",
            "groups",
            "user_permissions",
            "is_superuser",
            "is_staff",
            "is_active",
            "password",
            "loan",
            "role",
            "department",
            "lectures",
            "courses"
        ]


class GradeDisplaySerializer(serializers.ModelSerializer):
    student = StudentSerializer()
    assignment = AssignmentDisplaySerializer()

    class Meta:
        model = Grade
        fields = "__all__"


class GradeModificationSerializer(serializers.ModelSerializer):
    """
    This class is used to serialize the Grade model.
    """
    class Meta:
        model = Grade
        fields = "__all__"
        extra_kwargs = {
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True}
        }

    def validate(self, data):
        assignment = data["assignment"]
        student = data["student"]

        if Grade.objects.filter(
            assignment=assignment,
            student=data["student"],
            grade=data["grade"]
        ).exists():
            raise serializers.ValidationError("This grade already exists.")

        if not student.role == 1:
            raise serializers.ValidationError("This user is not a student.")

        if student not in assignment.lecture.users.all():
            raise serializers.ValidationError(
                "This student is not in this lecture."
            )

        if data['grade'] > assignment.max_points:
            raise serializers.ValidationError(
                "Grade cannot be higher than the max points."
            )

        return data

    def create(self, validated_data):
        """
        If the assignment is a final exam or a bachelor's thesis, then
        the grade record will be added to the queue.
        """
        assignment = validated_data.get("assignment")
        student = validated_data.get("student")
        created = super().create(validated_data)
        if assignment.name in [
            "დასკვნითი გამოცდა",
            "საბაკალავრო ნაშრომი",
            "სამაგისტრო ნაშრომი",
            "Final Exam",
            "Bachelor Thesis",
            "Master Thesis"
        ]:
            add_grade_record.delay(student.pk, assignment.lecture.pk)
        return created

    def update(self, instance, validated_data):
        """
        If the assignment is a final exam or a bachelor's thesis, then
        the grade record will be added to the queue.
        """
        updated = super().update(instance, validated_data)
        assignment = validated_data.get("assignment")
        student = validated_data.get("student")
        if assignment.name in [
            "დასკვნითი გამოცდა",
            "საბაკალავრო ნაშრომი",
            "სამაგისტრო ნაშრომი",
            "Final Exam",
            "Bachelor Thesis",
            "Master Thesis"
        ]:
            add_grade_record.delay(student.pk, assignment.lecture.pk)
        return updated


class AuditoriumSerializer(serializers.ModelSerializer):
    """
    This class is used to serialize the Auditorium model.
    """
    class Meta:
        model = Auditorium
        fields = ["id", "name", "capacity", "has_computers"]
        extra_kwargs = {
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True}
        }


class SemesterSerializer(serializers.ModelSerializer):
    """
    This class is used to serialize the Semester model.
    """
    class Meta:
        model = Semester
        fields = "__all__"
        extra_kwargs = {
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True}
        }


##########################################################
# Syllabus Serializers
class LectureDetailSerializer(serializers.Serializer):
    """
    This class is used to serialize the lecture details
    for the syllabus.
    """
    info = serializers.CharField()
    detail = serializers.CharField()


class AssignmentDetailSerializer(serializers.Serializer):
    """
    This class is used to serialize the assignment details
    for the syllabus.
    """
    info = serializers.CharField()
    amount = serializers.CharField()
    grade = serializers.CharField()
    total = serializers.CharField()


class SyllabusSerializer(serializers.Serializer):
    """
    This class is used to serialize the syllabus details
    """
    course_name = serializers.CharField()
    course_code = serializers.CharField()
    course_annotation = serializers.CharField()
    course_status = serializers.CharField()
    ECTS = serializers.IntegerField()
    course_level = serializers.CharField()
    semester = serializers.IntegerField()
    lecturer = serializers.CharField()
    lecturer_eng = serializers.CharField()
    lecturer_education = serializers.CharField()
    lecturer_work = serializers.CharField()
    lecturer_email = serializers.EmailField()
    purpose = serializers.CharField()
    results = serializers.CharField()
    literature = serializers.CharField()
    assignments = AssignmentDetailSerializer(many=True)
    lecture_plans = LectureDetailSerializer(many=True)


class ResourceSerializer(serializers.ModelSerializer):
    """
    This class is used to serialize the Resource model.
    """
    class Meta:
        model = Resource
        fields = "__all__"
        extra_kwargs = {
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True}
        }


class GradeRecordSerializer(serializers.ModelSerializer):
    """
    This class is used to serialize the GradeRecord model.
    """
    lecture = LectureDisplaySerializer()
    student = StudentSerializer()

    class Meta:
        model = GradeRecord
        fields = "__all__"


class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    """
    This class is used to serialize the AssignmentSubmission model.
    """
    class Meta:
        model = AssignmentSubmission
        fields = "__all__"
        extra_kwargs = {
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True},
            "student": {"read_only": True}
        }

    def validate(self, data):
        assignment = data["assignment"]
        student = self.context.get("request").user

        if student not in assignment.lecture.users.all():
            raise serializers.ValidationError(
                "This student is not in this lecture."
            )

        if datetime.datetime.now().replace(
                tzinfo=None
        ) > assignment.due_date.replace(
            tzinfo=None
        ):
            raise serializers.ValidationError("Deadline has passed.")

        if self.context.get("view").action == "create":
            if AssignmentSubmission.objects.filter(
                assignment=assignment,
                student=student
            ).exists():
                raise serializers.ValidationError(
                    "This student has already submitted this assignment."
                )
        return data
