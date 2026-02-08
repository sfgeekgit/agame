from django.urls import path
from . import views

urlpatterns = [
    path('user/me/', views.get_or_create_user, name='get_or_create_user'),
    path('user/me/points/', views.add_points, name='add_points'),
]
