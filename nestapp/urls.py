# myapp/urls.py

from django.urls import path
from django.contrib.auth.views import LogoutView  # Import LogoutView from auth.views
from . import views  # Import your own views
from .views import upload_note_view , my_notes , my_orders , order_detail
from django.contrib.auth.views import LoginView

####
from . import views


urlpatterns = [
    path('', views.landingpage, name='landingpage'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='landingpage'), name='logout'),
    path('upload/', views.upload_note_view, name='upload_note'),
    path('success/', views.success_page, name='success_page'),
    path('searchnotes/', views.search_notes_view, name='search_notes'),
    path('note/<int:note_id>/', views.view_note, name='view_note'),
    path('note/<int:note_id>/add/', views.add_to_my_notes, name='add_to_my_notes'),
    path('my_notes/', views.my_notes, name='my_notes'),
    path('note/<int:note_id>/upvote/', views.upvote_note, name='upvote_note'),
    path('order_printout/', views.order_printout, name='order_printout'),
    path('order_success/', views.order_success, name='order_success'),
    path('my_orders/', views.my_orders, name='my_orders'),
    path('order_detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path('profile/', views.profile_view, name='profile'), 
    path('downloaded_notes/', views.downloaded_notes_view, name='downloaded_notes'),
]

