# University Management System API (RESTful)

A backend API for a university management system that allows students to enroll in courses and lectures,
view grades, attendances, timetable and complete payments.
The API is built using Django and Django REST Framework.

## Table of Contents

- [Features](#features)
- [Requirements](#main-requirements)
- [Installation](#installation)
- [Environment Variables](#environment-variables)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
    - [Authentication](#authentication)
    - [Course](#course)
    - [User](#user)
    - [Payment](#payment)
- [Database Schema](#database-schema)
- [Components](#components)
    - [ViewSets](#viewsets)
    - [API Views](#api-views)
    - [Serializers](#serializers)
    - [Permissions](#permissions)
    - [Celery and Celery Beat Tasks](#celery-and-celery-beat-tasks)
    - [Utils](#utils)
- [Contributing](#contributing)

---

#### P.S.
Every Account except admin has a default password of `pass123!` for testing purposes. Admin's password is `admin`.

## Features
- User registration and authentication (JWT-based)
- User roles for students, professors, managers, graduates, and admins. 
  They all can access different data and perform different actions.
- User profile with necessary information about Faculty, Department, Role, Loan, etc.
- Password reset via email
- Custom managers for handling the data of the lecture and course. 
- Celery tasks for adding grade records every time a final assignment grade is added.
- Celery beat tasks for making the student a graduate after graduation or deactivating
  the student after a certain period of not paying the tuition fee.
- Caching for frequently accessed data. Uses Low Level Cache as well as Django Cache.
- Admin panel for content moderation
- PayPal API for payment processing
- Google Calendar API for creating events
- Swagger documentation for API endpoints
- Filtering and pagination for large datasets
- Custom permissions.
- Syllabus Generator with the help of PDFkit and django templates.
- Model Translation for courses and lectures for Georgian and Foreign Students. Rosetta for translation management.

### Student Side
- Students can see their profile with GPA, lectures and courses they are enrolled in as well as the 
  lectures and courses in their department.
  It Can be filtered by semester.
- Students can see their grades and attendance for each lecture.
- Students can create the Google Calendar events for the semester timetable with the help of
  the Google Calendar API.
- Students can enroll in courses only after they successfully complete the prerequisites.
- Students can enroll in lectures only if they are enrolled in the course and have paid the tuition fee.
- Students can pay the tuition fee via the PayPal API.
- Students can see the current semester fee and the payment history.
- Students can see their final grade for each lecture.
- Students can see their attendance history for each lecture.
- Students can submit the assignments for the lectures.

### Professor Side
- Professors can see their profile with the lectures they are teaching.
- Professors can see the students enrolled in their lectures.
- Professors can see the grades and attendance of the students in their lectures.
  and can add grades and attendance.
- Professors can see and add the resources and syllabus for their lectures.
- Professors can generate the syllabus by simply filling the form and downloading the PDF.
- Professors can create and update the assignments for their lectures.
- Professors can see the submitted assignments of their students.

### Manager Side
- Managers can see the profile of the users in their department.
- Managers can see and add the grades and attendance of the students in their department.
- Managers can see and add the assignments.
- Managers can see and add the lectures and courses.
- Managers can register the students and professors.
- Managers can see the payments and the payment history of the students in their department.
- Managers can enroll and remove the students in the courses and lectures.
- Managers can see the timetable of the lectures in their department.
- Managers can create and access the auditoriums.
- Managers can see the submitted assignments of the students in their department.


### Admin Side
- Admins can do everything that managers can do but with the ability to access all departments.
- Admins can filter the large dataset to find the necessary information.
- Admins can create the semesters, faculties, departments, manager roles, superuser roles, etc.


### Graduates Side
- Graduates can access their data like the students.
- Graduates cannot enroll in courses or lectures.
- Graduates cannot pay the tuition fee.

---

## Main Requirements

- Python 3.8+
- Django 4.0+
- Django REST Framework 3.13+
- Celery 5.2+
- Redis 6.0+

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/hella753/university_management_django_rest_api/
   cd university_management_django_rest_api
   ```
2. Create a virtual environment:
   ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the development server:
   ```bash
    python manage.py runserver
    ```

## Environment Variables

Create a `.env` file in the root directory and add the following environment variables:

```env
SECRET_KEY=your_secret_key
DEBUG=True

GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_CREDENTIALS_PATH="user/credentials.json"

WKHTMLTOPDF_PATH=

PAYPAL_ID=
PAYPAL_SECRET=
PAYPAL_BASE_URL=https://api-m.sandbox.paypal.com

EMAIL_HOST=
EMAIL_PORT=
EMAIL_BACKEND=
EMAIL_HOST_USER=
CONTACT_EMAIL=
EMAIL_HOST_PASSWORD=
```

---

## Usage

Start the server and access the API at http://127.0.0.1:8000/api/{app}.
You can use Swagger documentation to view and test the API endpoints at http://127.0.0.1:8000/swagger/.
An admin panel is available at http://127.0.0.1:8000/admin/.
Use an API client like Postman or cURL for testing.

---

## API Endpoints

### Authentication

| Method | Endpoint                | Description                 |
|--------|-------------------------|-----------------------------|
| POST   | `/api/token/`           | Obtain a JWT token          |
| POST   | `/api/token/refresh`    | Obtain a new access token   |
| POST   | `/api/token/blacklist/` | Blacklist the refresh token |


### Course

#### Assignments

| Method | Endpoint                       | Description                    |
|--------|--------------------------------|--------------------------------|
| GET    | `/api/course/assignment/`      | List assignments               |
| POST   | `/api/course/assignment/`      | Create a new assignment        |
| GET    | `/api/course/assignment/{id}/` | Retrieve a specific assignment |
| PUT    | `/api/course/assignment/{id}/` | Update an assignment           |
| DELETE | `/api/course/assignment/{id}/` | Delete an assignment           |
| PATCH  | `/api/course/assignment/{id}/` | Partial update an assignment   |


#### Auditorium

| Method | Endpoint                       | Description                    |
|--------|--------------------------------|--------------------------------|
| GET    | `/api/course/auditorium/`      | List auditoriums               |
| POST   | `/api/course/auditorium/`      | Create a new auditorium        |
| GET    | `/api/course/auditorium/{id}/` | Retrieve a specific auditorium |
| PUT    | `/api/course/auditorium/{id}/` | Update an auditorium           |
| DELETE | `/api/course/auditorium/{id}/` | Delete an auditorium           |
| PATCH  | `/api/course/auditorium/{id}/` | Partial update an auditorium   |

#### Course

| Method | Endpoint                                  | Description                |
|--------|-------------------------------------------|----------------------------|
| GET    | `/api/course/course/`                     | List courses               |
| POST   | `/api/course/course/`                     | Create a new course        |
| GET    | `/api/course/course/{id}/`                | Retrieve a specific course |
| PUT    | `/api/course/course/{id}/`                | Update a course            |
| DELETE | `/api/course/course/{id}/`                | Delete a course            |
| PATCH  | `/api/course/course/{id}/`                | Partial update a course    |
| POST   | `/api/course/course/{id}/register_course` | Enroll/Remove the course   |


#### Department

| Method | Endpoint                                  | Description                    |
|--------|-------------------------------------------|--------------------------------|
| GET    | `/api/course/department/`                 | List departments               |
| POST   | `/api/course/department/`                 | Create a new department        |
| GET    | `/api/course/department/{id}/`            | Retrieve a specific department |
| PUT    | `/api/course/department/{id}/`            | Update a department            |
| DELETE | `/api/course/department/{id}/`            | Delete a department            |
| PATCH  | `/api/course/department/{id}/`            | Partial update a department    |


#### Faculty

| Method | Endpoint                      | Description                 |
|--------|-------------------------------|-----------------------------|
| GET    | `/api/course/faculty/`        | List faculties              |
| POST   | `/api/course/faculty/`        | Create a new faculty        |
| GET    | `/api/course/faculty/{id}/`   | Retrieve a specific faculty |
| PUT    | `/api/course/faculty/{id}/`   | Update a faculty            |
| DELETE | `/api/course/faculty/{id}/`   | Delete a faculty            |
| PATCH  | `/api/course/faculty/{id}/`   | Partial update a faculty    |


#### Grade

| Method | Endpoint                  | Description               |
|--------|---------------------------|---------------------------|
| GET    | `/api/course/grade/`      | List grades               |
| POST   | `/api/course/grade/`      | Create a new grade        |
| GET    | `/api/course/grade/{id}/` | Retrieve a specific grade |
| PUT    | `/api/course/grade/{id}/` | Update a grade            |
| DELETE | `/api/course/grade/{id}/` | Delete a grade            |
| PATCH  | `/api/course/grade/{id}/` | Partial update a grade    |


#### Lecture
| Method | Endpoint                                    | Description                     |
|--------|---------------------------------------------|---------------------------------|
| GET    | `/api/course/lecture/`                      | List lectures                   |
| POST   | `/api/course/lecture/`                      | Create a new lecture            |
| GET    | `/api/course/lecture/{id}/`                 | Retrieve a specific lecture     |
| PUT    | `/api/course/lecture/{id}/`                 | Update a lecture                |
| DELETE | `/api/course/lecture/{id}/`                 | Delete a lecture                |
| PATCH  | `/api/course/lecture/{id}/`                 | Partial update a lecture        |
| POST   | `/api/course/lecture/{id}/register_lecture` | Enroll/Remove the lecture       |
| GET    | `/api/course/lecture/{id}/final_grade`      | Get final grade of the lecture  |


#### Resource
| Method | Endpoint                       | Description                  |
|--------|--------------------------------|------------------------------|
| GET    | `/api/course/resource/`        | List resources               |
| POST   | `/api/course/resource/`        | Create a new resource        |
| GET    | `/api/course/resource/{id}/`   | Retrieve a specific resource |
| PUT    | `/api/course/resource/{id}/`   | Update a resource            |
| DELETE | `/api/course/resource/{id}/`   | Delete a resource            |
| PATCH  | `/api/course/resource/{id}/`   | Partial update a resource    |


#### Semester
| Method | Endpoint                       | Description                  |
|--------|--------------------------------|------------------------------|
| GET    | `/api/course/semester/`        | List semesters               |
| POST   | `/api/course/semester/`        | Create a new semester        |
| GET    | `/api/course/semester/{id}/`   | Retrieve a specific semester |
| PUT    | `/api/course/semester/{id}/`   | Update a semester            |
| DELETE | `/api/course/semester/{id}/`   | Delete a semester            |
| PATCH  | `/api/course/semester/{id}/`   | Partial update a semester    |


#### Syllabus
| Method | Endpoint                       | Description         |
|--------|--------------------------------|---------------------|
| POST   | `/api/course/syllabus/`        | Generate a syllabus |


#### GradeRecord
| Method | Endpoint                           | Description                 |
|--------|------------------------------------|-----------------------------|
| GET    | `/api/course/grade_record/`        | List grade records          |


#### AssignmentSubmission
| Method | Endpoint                                  | Description                    |
|--------|-------------------------------------------|--------------------------------|
| GET    | `/api/course/assignment_submission/`      | List assignment submissions    |
| POST   | `/api/course/assignment_submission/`      | Create a new assignment        |
| GET    | `/api/course/assignment_submission/{id}/` | Retrieve a specific assignment |
| PUT    | `/api/course/assignment_submission/{id}/` | Update an assignment           |
| DELETE | `/api/course/assignment_submission/{id}/` | Delete an assignment           |
| PATCH  | `/api/course/assignment_submission/{id}/` | Partial update an assignment   |


### Payment

| Method | Endpoint                               | Description                       |
|--------|----------------------------------------|-----------------------------------|
| GET    | `/api/payment/payment/`                | List payments                     |
| GET    | `/api/payment/payment/current_fee/`    | Get the current fee               |
| GET    | `/api/payment/payment_failed/`         | Return url for failed payment     |
| GET    | `/api/payment/payment_success/`        | Return url for successful payment |
| POST   | `/api/payment/paypal/create-order/`    | Create a new PayPal order         |
| POST   | `/api/payment/paypal/capture-order/`   | Capture a PayPal order            |


### User

#### User

| Method | Endpoint                          | Description                   |
|--------|-----------------------------------|-------------------------------|
| POST   | `/api/user/user/`                 | Register a new user           |
| GET    | `/api/user/user/`                 | List all users                |
| GET    | `/api/user/user/{username}/`      | Retrieve a specific user      |
| PUT    | `/api/user/user/{username}/`      | Update a user                 |
| DELETE | `/api/user/user/{username}/`      | Delete a user                 |
| PATCH  | `/api/user/user/{username}/`      | Partial update a user         |
| POST   | `/api/user/user/forget-password/` | Reset password via email      |
| POST   | `/api/user/user/reset-pssword/`   | Confirm password reset        |
| POST   | `/api/user/create-event/`         | Create Google Calendar events |


#### Attendance

| Method | Endpoint                           | Description                |
|--------|------------------------------------|----------------------------|
| GET    | `/api/user/attendance/`            | List attendance            |
| POST   | `/api/user/attendance/`            | Create a new attendance    |
| GET    | `/api/user/attendance/{id}/`       | Retrieve a specific record |
| PUT    | `/api/user/attendance/{id}/`       | Update a record            |
| DELETE | `/api/user/attendance/{id}/`       | Delete a record            |
| PATCH  | `/api/user/attendance/{id}/`       | Partial update a record    |

---

## Database Schema

The database includes the following models:

https://drawsql.app/teams/university-management-backend/diagrams/university-management-backend

![Models](static/models.png)


---

## Components

### ViewSets

Every model has a corresponding ViewSet that handles CRUD operations for the model.
Some of them do not have all the CRUD operations, depending on the requirements.
ViewSets have extra actions for custom operations.

- **CourseViewSet**: Handles CRUD operations for Course model.
  - extra actions: register_course
- **LectureViewSet**: Handles CRUD operations for Lecture model.
  - extra actions: register_lecture, final_grade
- **AssignmentViewSet**: Handles CRUD operations for Assignment model.
- **GradeViewSet**: Handles CRUD operations for Grade model.
- **FacultyViewSet**: Handles CRUD operations for Faculty model.
- **DepartmentViewSet**: Handles CRUD operations for Department model.
- **ResourceViewSet**: Handles CRUD operations for Resource model.
- **SemesterViewSet**: Handles CRUD operations for Semester model.
- **AuditoriumViewSet**: Handles CRUD operations for Auditorium model.
- **GradeRecordViewSet**: Handles Listing and Retrieving for GradeRecord model.
- **AssignmentSubmissionViewSet**: Handles CRUD operations for AssignmentSubmission model.
- **UserViewSet**: Handles CRUD operations for User model.
  - extra actions: forget_password, reset_password, create_event
- **AttendanceViewSet**: Handles CRUD operations for Attendance model.
- **PaymentViewSet**: Handles payment history listings.
  - extra actions: current_fee,

### API Views
- **BlacklistTokenView**: Blacklists the refresh token.
- **PayPalCreateOrderView**: Creates a new PayPal order.
- **PayPalCaptureOrderView**: Captures a PayPal order.
- **payment_failed**: Redirects to the failed payment URL.
- **payment_success**: Redirects to the successful payment URL.
- **CreateSyllabusView**: Generates a syllabus PDF.

### Serializers
- **CourseSerializer**: Serializes the Course model.
- **CourseModificationSerializer**: Serializes the Course model.
- **PrerequisiteSerializer**: Serializes the Course model.
- **LectureModificationSerializer**: Serializes the Lecture model.
- **LectureDisplaySerializer**: Serializes the Lecture model for display.
- **RegisterLectureSerializer**: Validates the data for enrollment.
- **RegisterCourseSerializer**: Validates the data for enrollment.
- **AssignmentDisplaySerializer**: Serializes the Assignment model for display.
- **AssignmentModificationSerializer**: Serializes the Assignment model.
- **ProfessorSerializer**: Serializes the User model.
- **LectureProfessorSerializer**: Serializes the User model.
- **FacultyModificationSerializer**: Serializes the Faculty model.
- **FacultyDisplaySerializer**: Serializes the Faculty model for display.
- **StudentSerializer**: Serializes the User model.
- **GradeDisplaySerializer**: Serializes the Grade model for display.
- **GradeModificationSerializer**: Serializes the Grade model.
- **AuditoriumSerializer**: Serializes the Auditorium model.
- **SemesterSerializer**: Serializes the Semester model.
- **DepartmentSerializer**: Serializes the Department model.
- **ResourceSerializer**: Serializes the Resource model.
- **SyllabusSerializer**: Serializes the Syllabus details with nested serializers.
  - **AssignmentDetailSerializer**
  - **LectureDetailSerializer**
- **GradeRecordSerializer**: Serializes the GradeRecord model.
- **AssignmentSubmissionSerializer**: Serializes the AssignmentSubmission model.
- **PaymentSerializer**: Serializes the Payment model.
- **AttendanceSerializer**: Serializes the Attendance model.
- **UserDisplaySerializer**: Serializes the User model for display.
- **UserModificationSerializer**: Serializes the User model.
- **BlacklistTokenSerializer**: Serializes the data for blacklisting the token.
- **ResetPasswordSerializer**: Serializes the data for resetting the password.
- **ConfirmResetSerializer**: Serializes the data for forgetting the password.

### Permissions
- **IsCreatorOfAssignmentOrManagement**: Allows the creator of the assignment or the management to edit the assignment.
- **IsCreatorOfAssignmentSubmissionOrManagement**: Allows the creator of the assignment submission or the management to edit the submission.
- **IsCreatorOfGradeOrManagement**: Allows the creator of the grade or the management to edit the grade.
- **IsProfessorOrManagement**: Allows the professor or the management to edit the lecture.
- **IsManagement**: Allows the management to edit the course, faculty, department, etc.
- **IsThisLecturesProfessor**L Allows the professor of the lecture to edit the lecture.
- **RestrictAfterTwoWeeks**: Restricts the user from changing enrollment in the lecture after two weeks of the semester start.
- **IsStudentOrManagement**: Allows the student or the management to access the data.
- **IsOwnProfessor**: Allows the professor to access the data.
- **IsOwnStudentOrProfessor**: Allows the student or professor of a lecture to view data.
- **IsOwnerOrManagement**: Allows the owner of the data or the management to edit the data.

### Celery and Celery Beat Tasks
- `add_grade_record()`: Adds a grade record for the student after the final assignment grade is added.
- `make_graduate()`: Makes the student a graduate after graduation.
- `deactivate_student()`: Deactivates the student after a certain period of not paying the tuition fee.

### Utils
- **grade_calculator**: includes `GradeCalculator` class with methods for calculating the final grade.
  - `calculate_final_grade()`: Calculates the final grade for the lecture.
  - `calculate_gpa()`: Calculates the GPA for the student.
  - `calculate_subject_grade_point()`: Calculates the grade point for the subject.
- **syllabus_generator**: includes `SyllabusGenerator` class with methods for generating the syllabus.
  - `generate_syllabus()`: Generates the syllabus PDF.
  - `_generate_context()`: Generates the context for the syllabus.
- **payment_calculator**: includes `PaymentCalculator` class with methods for calculating the payment.
  - `calculate_fee()` and `student_payment()`: Calculate the fee and the payment for the student.
- **paypal_operations**: includes `PayPalOperationsManager` class with methods for creating and capturing the PayPal order.
  - `create_paypal_order()`: Creates a new PayPal order.
  - `capture_paypal_order()`: Captures the PayPal order.
  - `_get_paypal_access_token()`: Gets the PayPal access token.
- **google_calendar**: includes `GoogleCalendar` class with methods for creating Google Calendar events.
  - `create_event()`: Creates a new Google Calendar event.
  - `create_events()`: Inserts multiple Google Calendar events.
  - `_initialize_service()`: Initializes the Google Calendar service.
  - `_authorize()`: Authorizes the Google Calendar service.
- **helpers**:
  - `send_reset_email()`: Sends the password reset email.
  - `get_semester()`: Gets the current semester.
  - `validate_passwords()`: Validates the passwords.

---

## Contributing

Contributions are welcome! Please follow the steps below to contribute to this project:

1. Fork the repository
2. Create a new branch (`git checkout -b feature`)
3. Make changes
4. Commit your changes (`git commit -am 'Add new feature'`)
5. Push to the branch (`git push origin feature`)
6. Create a new Pull Request
7. Wait for your PR review and merge approval
8. Star this repository if you find it helpful
9. Share it with others
10. Happy coding!

---