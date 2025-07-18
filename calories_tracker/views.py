from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Meal
from datetime import date
from CaloriesTracker import settings
from .fatsecret_utils import search_food
from .forms import AddFoodForm, FoodSearchForm
from .models import Food_Eaten
import logging
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

logger = logging.getLogger(__name__)


def home(request):
    if not request.user.is_authenticated:
        messages.warning(request, 'Please log in to track your foods.')

    search_form = FoodSearchForm(request.GET or None)
    add_food_form = AddFoodForm()
    foods_data = None
    error_message = None
    debug_info = None

    if request.method == 'GET' and search_form.is_valid():
        query = search_form.cleaned_data['query']
        try:
            search_results = search_food(query)

            logging.debug(f"FatSecret API Response: {search_results}")

            if isinstance(search_results, dict) and 'error' in search_results:
                error = search_results['error']
                if error.get('code') == 21:
                    error_message = "API access is currently restricted. Please try again later."
                    debug_info = f"IP Address {error['message'].split(':')[1]} needs to be whitelisted in FatSecret dashboard"
                    logging.error(f"FatSecret IP error: {error['message']}")
                else:
                    error_message = "An error occurred while searching. Please try again."
                    logging.error(f"FatSecret API error: {error}")
            elif search_results and 'foods' in search_results:
                food_items = search_results['foods'].get('food', [])
                if food_items:
                    foods_data = [food_items] if isinstance(food_items, dict) else food_items
                    logging.info(f"Found {len(foods_data)} food items for query: {query}")
                else:
                    foods_data = []
                    if query:
                        error_message = f"No results found for '{query}'."
            else:
                foods_data = []
                if query:
                    error_message = f"No results found for '{query}'."

        except Exception as e:
            logging.error(f"Error during food search: {str(e)}")
            error_message = "An error occurred while searching. Please try again."
            foods_data = None

    context = {
        'form': search_form,
        'add_food_form': add_food_form,
        'foods': foods_data,
        'error_message': error_message,
        'query': request.GET.get('query', ''),
        'debug_info': debug_info if settings.DEBUG else None
    }
    return render(request, "home.html", context)


@login_required
def add_food(request):
    food_data = None

    if request.method == 'GET':
        # Get food details from query parameters (from search results)
        food_name = request.GET.get('food_name')
        food_description = request.GET.get('food_description')

        if food_name and food_description:
            food_data = {
                'food_name': food_name,
                'food_description': food_description
            }

    elif request.method == 'POST':
        try:
            # Process the form submission to add the food
            food_name = request.POST.get('food_name')
            food_description = request.POST.get('food_description')
            quantity = float(request.POST.get('quantity', 1))
            measurement_type = request.POST.get('measurement_type')
            unit_label = request.POST.get('unit_label')

            # Parse base nutrition info
            base_nutrition = Food_Eaten.parse_nutrition(food_description)

            # Calculate nutrition for the specified quantity
            nutrition = Food_Eaten.calculate_nutrition_for_quantity(base_nutrition, quantity)

            # Get the selected meal type from the form
            meal_type = request.POST.get('meal')


            # Get or create the Meal instance for this user, date, and meal type
            meal_obj, created = Meal.objects.get_or_create(
                user=request.user,
                name=meal_type,
                date=date.today()
            )

            # Create new Food_Eaten entry
            food_entry = Food_Eaten.objects.create(
                user=request.user,
                food_name=food_name,
                quantity=quantity,
                measurement_type=measurement_type or base_nutrition['measurement_type'],
                unit_label=unit_label or base_nutrition['unit_label'],
                calories=nutrition['calories'],
                fat=nutrition['fat'],
                carbs=nutrition['carbs'],
                protein=nutrition['protein']
            )

            # Associate the food entry with the meal
            meal_obj.meals.add(food_entry)

            quantity_str = f"{quantity}g" if measurement_type == 'g' else f"{quantity} {unit_label}{'s' if quantity > 1 else ''}"
            messages.success(request, f'Added {quantity_str} of {food_name} to your {meal_type}!')

            return redirect('home')

        except Exception as e:
            messages.error(request, f"Error adding food: {str(e)}")

    return render(request, "calories_tracker/add_food.html", {'food': food_data})



class MyMealsView(LoginRequiredMixin, View):
    def get(self, request):
        meals = Meal.objects.filter(user=request.user).order_by('-date', 'name')
        return render(request, "calories_tracker/my_meals.html", {'meals': meals})


