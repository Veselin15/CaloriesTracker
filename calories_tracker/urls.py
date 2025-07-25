
from django.urls import path
from . import views
from .views import MyMealsView

urlpatterns = [
    path('', views.statistics, name='home'),
    path('add-food/', views.add_food, name='add_food'),
    path('my-meals/', MyMealsView.as_view(), name='my_meals'),
    path('search-for-foods/', views.search_for_foods, name='search_for_foods'),
    path('set-goals/', views.set_goals, name='set_goals'),
    path('track-weight/', views.track_weight, name='track_weight'),

]