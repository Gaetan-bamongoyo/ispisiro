from django.urls import path
from .views import *

urlpatterns = [
    path('', indexPage, name='home')
]
