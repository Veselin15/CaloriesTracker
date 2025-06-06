
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('add-food/', views.add_food, name='add_food'),
]