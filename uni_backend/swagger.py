import os
from dotenv import load_dotenv
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt.authentication import JWTAuthentication

load_dotenv()

schema_view = get_schema_view(
    openapi.Info(
        title="University Management System API",
        default_version='v1',
        description="University Management API Documentation. "
                    "This API makes students, professors and managers life easier =).",
        contact=openapi.Contact(email=os.getenv('CONTACT_EMAIL')),
        license=openapi.License(name="All rights reserved"),
    ),
    public=True,
    authentication_classes=[JWTAuthentication],
)
