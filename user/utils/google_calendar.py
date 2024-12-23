import datetime
import os.path
import pytz
from django.utils import timezone
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from user.models import GoogleOAuthToken
from dotenv import load_dotenv


load_dotenv()


class GoogleCalendar:
    """
    A class for creating events in Google Calendar.
    """
    def __init__(self, user, credentials_path):
        """
        Constructor for the GoogleCalendar class.
        :param user: User
        :param credentials_path: Path to credentials.json file
        """
        self.user = user
        self.credentials_path = credentials_path
        self.service = self._initialize_service()

    def _authorize(self):
        """
        This function is used to authorize the user via Google OAuth.
        :return: Google Calendar service object
        """
        flow = InstalledAppFlow.from_client_secrets_file(
            self.credentials_path,
            scopes=["https://www.googleapis.com/auth/calendar"]
        )
        credentials = flow.run_local_server(port=0)

        # Create token object
        token = GoogleOAuthToken(user=self.user)
        token.access_token = credentials.token
        token.refresh_token = credentials.refresh_token
        # Convert to a timezone-aware datetime in UTC
        token.token_expiry = timezone.now() + (
                credentials.expiry.replace(tzinfo=pytz.UTC) - timezone.now()
        )
        token.save()
        return build("calendar", "v3", credentials=credentials)

    def _initialize_service(self):
        """
        This function is used to initialize the Google Calendar service.
        :return: Google Calendar service object
        """
        try:
            # Try to get the token from the database
            token = GoogleOAuthToken.objects.get(user=self.user)
            # Create credentials object
            credentials = Credentials(
                token.access_token,
                refresh_token=token.refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=os.getenv("GOOGLE_CLIENT_ID"),
                client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
                scopes=["https://www.googleapis.com/auth/calendar"]
            )
            if not credentials.valid:
                if (
                        credentials.expired and
                        credentials.refresh_token
                ):
                    # Refresh the token if it"s expired and
                    # change the token in the database
                    credentials.refresh(Request())
                    token.access_token = credentials.token
                    # Convert to a timezone-aware datetime in UTC
                    token.token_expiry = timezone.now() + (
                            credentials.expiry.replace(tzinfo=pytz.UTC) - timezone.now()
                    )
                    token.save()
                else:
                    return self._authorize()
        except GoogleOAuthToken.DoesNotExist:
            return self._authorize()
        return build("calendar", "v3", credentials=credentials)

    def create_event(self, lecture, start):
        """
        This function is used to create an event dictionary.
        :param start: Start date of the event
        :param lecture: Lecture
        :return: Event dictionary
        """
        start_date_time = datetime.datetime.combine(
            start,
            lecture.start_time
        )
        end_date_time = datetime.datetime.combine(
            start,
            lecture.end_time
        )

        return {
            "summary": lecture.name,
            "location": lecture.location.name,
            'start': {
                'dateTime': start_date_time.isoformat(),
                'timeZone': 'Asia/Tbilisi',
            },
            'end': {
                'dateTime': end_date_time.isoformat(),
                'timeZone': 'Asia/Tbilisi',
            },
            'recurrence': [
                f'RRULE:FREQ=WEEKLY;COUNT=6',
            ],
            'attendees': [
                {'email': self.user.email},
                # {'email': lecture.professor.email},
            ],
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 10},
                ],
            },
        }

    def create_events(self, lectures):
        """
        This function is used to create events in Google Calendar.
        :param lectures: List of lectures.
        :return: List of created events.
        """
        created_events = []

        for lecture in lectures:
            before_midterm_start = lecture.start_day
            before_final_start = lecture.start_day_second
            try:
                before_midterm_event = self.create_event(lecture, before_midterm_start)
                first_created_event = self.service.events().insert(
                    calendarId=self.user.email,
                    body=before_midterm_event
                ).execute()
                before_final_event = self.create_event(lecture, before_final_start)
                second_created_event = self.service.events().insert(
                    calendarId=self.user.email,
                    body=before_final_event
                ).execute()
                created_events.extend([first_created_event, second_created_event])
            except HttpError as e:
                raise Exception(f"Error creating event: {e}")
        return created_events
