from django.urls import path
from .views import *

urlpatterns = [
    path('', login, name='login'),
    path('register/', register, name='register'),
    path('logout/', logout, name='logout'),
    path('dashboard/', dashboardPage, name='dash_home'),
    path('dashboard/ouvrages/', dashboardOuvragesPage, name='dash_ouvrages'),
    path('dashboard/affectations/', dashboardAffectationsPage, name='dash_affectations'),
    path('dashboard/cours/', dashboardCoursPage, name='dash_cours'),
    path('dashboard/etudiants/', dashboardEtudiantsPage, name='dash_etudiants'),
    path('dashboard/settings/', dashboardSettingsPage, name='dash_settings'),
]
