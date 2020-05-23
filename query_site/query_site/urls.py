from django.contrib import admin
from django.urls import include, path
from django.views.static import serve 

urlpatterns = [
    path('select_data/', include('select_data.urls')),
    path('admin/', admin.site.urls)
]