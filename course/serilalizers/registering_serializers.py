from rest_framework import serializers
from course.models import Lecture, Course, GradeRecord
from payment.models import Payment
from payment.utils import PaymentCalculator


class RegisterCourseSerializer(serializers.Serializer):
    """
    This serializer class is responsible for validating
    the course registration.
    """
    course_id = serializers.IntegerField()

    def validate(self, data):
        request = self.context["request"]
        course_id = data.get("course_id")
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            raise serializers.ValidationError("Course not found")

        if request.user.role != 1:
            raise serializers.ValidationError(
                "Only students are allowed to register the course"
            )

        missing_prerequisites = (
            Course.objects.find_missing_prerequisites(course, request)
        )

        if missing_prerequisites is not None:
            if missing_prerequisites.exists():
                raise serializers.ValidationError(
                    f"You can't register the course because "
                    f"you have not completed the following "
                    f"prerequisites: {", ".join(
                        missing_prerequisites.values_list(
                            "name", flat=True
                        )
                    )}")

        failed_prerequisites = (
            Course.objects.find_failed_prerequisites(course, request)
        )

        if failed_prerequisites is not None:
            if failed_prerequisites is False:
                raise serializers.ValidationError(
                    "You have not received the appropriate grades in "
                    "prerequisites."
                )

            if failed_prerequisites.exists():
                raise serializers.ValidationError(
                    f"You can't register the course because you have failed "
                    f"the following prerequisites: {", ".join(
                        failed_prerequisites.values_list(
                            "assignment__lecture__course__name", flat=True
                        )
                    )}")
        return data

    def create(self, validated_data):
        """
        This method registers the course for the user.
        """
        course_id = validated_data.get("course_id")
        course = Course.objects.get(id=course_id)
        request = self.context["request"]
        if request.user in course.users.all():
            course.users.remove(request.user)
        else:
            course.users.add(request.user)
        course.save()
        PaymentCalculator(request.user).student_payment(
            Payment.objects.filter(user=request.user)
        )
        return validated_data


class RegisterLectureSerializer(serializers.Serializer):
    """
    This serializer class is responsible for
    validating the lecture registration.
    """
    lecture_id = serializers.IntegerField()

    def validate(self, data):
        request = self.context["request"]
        lecture_id = data.get("lecture_id")

        try:
            lecture = Lecture.objects.get(id=lecture_id)
        except Lecture.DoesNotExist:
            raise serializers.ValidationError("Lecture not found")

        if request.user.role != 1:
            raise serializers.ValidationError(
                "Only students are allowed to register the course"
            )

        if lecture.capacity == 0 and request.user not in lecture.users.all():
            raise serializers.ValidationError(
                "You can't register the lecture because it is full"
            )

        print(request.user.loan)
        if request.user.loan > 0:
            print(request.user.loan)
            raise serializers.ValidationError(
                "You can't register the lecture because "
                "you have not payed the fee"
            )

        if request.user not in lecture.course.users.all():
            raise serializers.ValidationError(
                "You can't register the lecture because "
                "you have not registered the course"
            )

        overlapping_lectures = (
            Lecture.objects.get_overlapping_lectures(lecture, request)
        )

        if overlapping_lectures.exists():
            raise serializers.ValidationError(
                "You can't register the lecture because you have overlapping "
                "lectures: " + ", ".join(
                    overlapping_lectures.values_list("name", flat=True)
                )
            )
        return data

    def create(self, validated_data):
        """
        This method registers the lecture for the user.
        """
        lecture_id = validated_data.get("lecture_id")
        lecture = Lecture.objects.get(id=lecture_id)
        request = self.context["request"]
        lectures = request.user.lectures

        if request.user in lecture.users.all():
            # If the user is already registered for the lecture
            grade_record = GradeRecord.objects.filter(
                student=request.user,
                lecture__course=lecture.course,
                is_active=False
            ).order_by("-created_at")
            if grade_record.count() > 0:
                # If the user has already registered for
                # the course in the past
                old_lecture = grade_record.first().lecture
                lectures.add(old_lecture)
                grade = grade_record.first()
                grade.is_active = True
                grade.save()
            lecture.users.remove(request.user)
            lecture.capacity += 1
            lecture.save()
        else:
            # If the user is not registered for the lecture
            duplicate_lecture = lectures.filter(
                course=lecture.course
            ).order_by("-created_at")
            if duplicate_lecture.exists():
                # If the user has already registered
                # for the course in the past
                lectures.remove(duplicate_lecture.first())
                grade = GradeRecord.objects.filter(
                    student=request.user,
                    lecture__course=lecture.course,
                    is_active=True
                ).first()
                grade.is_active = False
                grade.save()
            lecture.users.add(request.user)
            lecture.capacity -= 1
            lecture.save()
        return validated_data
