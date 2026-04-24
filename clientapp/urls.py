from django.urls import path
from .views import *

urlpatterns = [
    path('', indexPage, name='home'),
    path('bibliotheque/', bibliothequePage, name='bibliotheque'),
    path('bloq/<str:id>/', bloqPage, name='bloq'), 
    path('filiere/<int:id>/', detail_filierePage, name='detail_filiere'),
]
