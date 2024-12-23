import datetime
import os
import pdfkit
from django.template.loader import get_template
from dotenv import load_dotenv

load_dotenv()


class SyllabusGenerator:
    def __init__(self, data):
        """
        This class is responsible for generating the syllabus of the course.
        :param data: Course Data
        """
        self.data = data
        self.assignments = data.get("assignments", [])
        self.lecture_plans = data.get("lecture_plans", [])
        self.context = self._generate_context()

    def _generate_context(self):
        """
        This method generates the context for the syllabus.
        :return: The context for the syllabus.
        """
        context = {
            "course_name": self.data.get("course_name", ""),
            "course_code": self.data.get("course_code", ""),
            "course_annotation": self.data.get("course_annotation", ""),
            "course_status": self.data.get("course_status", ""),
            "ECTS": self.data.get("ECTS", ""),
            "course_level": self.data.get("course_level", ""),
            "semester": self.data.get("semester", ""),
            "lecturer": self.data.get("lecturer", ""),
            "lecturer_education": self.data.get("lecturer_education", ""),
            "lecturer_work": self.data.get("lecturer_work", ""),
            "lecturer_emai": self.data.get("lecturer_email", ""),
            "purpose": self.data.get("purpose", ""),
            "results": self.data.get("results", ""),
            "literature": self.data.get("literature", ""),
            "assignments": [{
                "info": self.assignments[i].get("info", ""),
                "amount": self.assignments[i].get("amount", ""),
                "grade": self.assignments[i].get("grade", ""),
                "total": self.assignments[i].get("total", "")
            } for i in range(len(self.assignments))],
            "lecture_plans": [{
                "info": self.lecture_plans[i].get("info", ""),
                "detail": self.lecture_plans[i].get("detail", "")
            } for i in range(len(self.lecture_plans))],
        }
        return context

    def generate_syllabus(self):
        """
        This method generates the syllabus.
        :return: output_path: The path of the generated syllabus.
        """
        template = get_template("syllabus_template.html")
        output_text = template.render(self.context)

        config_path = os.getenv("WKHTMLTOPDF_PATH")
        config = pdfkit.configuration(wkhtmltopdf=config_path)

        course_code = self.data.get("course_code", "")
        lecturer_first_name = self.data.get("lecturer_eng", "").split(" ")[0]
        lecturer_last_name = self.data.get("lecturer_eng", "").split(" ")[1]
        cur_year = datetime.datetime.now().year
        output_path = (f"media/generated_syllabus/syllabus"
                       f"-{course_code}-{lecturer_first_name}"
                       f"-{lecturer_last_name}-{cur_year}.pdf")

        try:
            pdfkit.from_string(output_text, output_path, configuration=config)
        except Exception as e:
            return {"error": str(e)}
        return output_path
