"""
URL configuration for uni_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from debug_toolbar.toolbar import debug_toolbar_urls
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from uni_backend.swagger import schema_view
from user.views import BlacklistTokenView
from django.conf.urls.i18n import i18n_patterns

urlpatterns = i18n_patterns(
       path('admin/', admin.site.urls),
       path('api/user/', include('user.urls', namespace='user')),
       path('api/course/', include('course.urls', namespace='course')),
       path('api/payment/', include('payment.urls', namespace='payment')),
       path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
       path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
       path('api/token/blacklist/', BlacklistTokenView.as_view(), name='token-blacklist'),
       path('api-auth/', include('rest_framework.urls')),
) + [
    path('swagger/', schema_view.with_ui('swagger',cache_timeout=0), name='schema-swagger-ui')
]

if settings.DEBUG:
    urlpatterns += debug_toolbar_urls()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += [
        re_path(r'^rosetta/', include('rosetta.urls'))
    ]