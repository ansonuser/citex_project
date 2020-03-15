from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('select_data/', include('select_data.urls')),
    path('admin/', admin.site.urls)
]