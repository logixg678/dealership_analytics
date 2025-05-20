# logix_analytics/urls.py
from django.urls import path
from . import views

app_name = 'logix_analytics' # Define an application namespace

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'), # Maps the app's root to dashboard
]