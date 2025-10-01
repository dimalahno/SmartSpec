from django.urls import path
from . import views

app_name = 'specs'
urlpatterns = [
    path('', views.index, name='index'),
]
