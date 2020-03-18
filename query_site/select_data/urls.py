from django.urls import path

from . import views

app_name = 'select_data'
urlpatterns = [
    path('', views.index, name = 'index'),
    path('insert/', views.insert, name = 'insert'),
    path('record/', views.record, name = 'record'),
    path('select/', views.select, name = 'select')
]