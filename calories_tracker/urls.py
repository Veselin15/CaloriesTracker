
from django.urls import path
from . import views
from .views import MyMealsView

urlpatterns = [
    path('', views.home, name='home'),
    path('add-food/', views.add_food, name='add_food'),
    path('my-meals/', MyMealsView.as_view(), name='my_meals'),

]