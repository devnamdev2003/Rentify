from django.contrib import admin
from django.views.generic import RedirectView
from django.urls import path, re_path, include

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('dev/', admin.site.urls),
    path('', include('home.urls')),
    re_path(r"^.*/$", RedirectView.as_view(pattern_name="home_index", permanent=False)),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
