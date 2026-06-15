from django.urls import path
from .views import *

urlpatterns = [
    path('', indexPage, name='home'),
    path('bibliotheque/', bibliothequePage, name='bibliotheque'),
    path('articles/<uuid:id>/', articleDetailPage, name='article_detail'),
    path('bloq/<str:id>/', bloqPage, name='bloq'), 
    path('filiere/<int:id>/', detail_filierePage, name='detail_filiere'),
]
