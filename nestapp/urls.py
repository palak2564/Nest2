# myapp/urls.py

from django.urls import path
from django.contrib.auth.views import LogoutView  # Import LogoutView from auth.views
from . import views  # Import your own views
from .views import upload_note_view
from django.contrib.auth.views import LoginView

urlpatterns = [
    path('', views.landingpage, name='landingpage'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='landingpage'), name='logout'),
    path('upload/', upload_note_view, name='upload_note'),
    path('success/', views.success_page, name='success_page'),
    path('searchnotes/', views.search_notes_view, name='search_notes'),
]
