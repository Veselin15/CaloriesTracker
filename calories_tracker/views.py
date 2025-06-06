from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from CaloriesTracker import settings
from .fatsecret_utils import search_food
from .forms import AddFoodForm, FoodSearchForm
from .models import Food_Eaten
import logging

logger = logging.getLogger(__name__)


@login_required
def add_food(request):
    if request.method == 'POST':
        try:
            # Log the POST data for debugging
            logger.debug(f"POST data received: {request.POST}")

            food_name = request.POST.get('food_name')
            food_description = request.POST.get('food_description')
            quantity = float(request.POST.get('quantity', 1))

            # Parse base nutrition info
            base_nutrition = Food_Eaten.parse_nutrition(food_description)
            logger.debug(f"Base nutrition parsed: {base_nutrition}")

            # Calculate nutrition for the specified quantity
            nutrition = Food_Eaten.calculate_nutrition_for_quantity(base_nutrition, quantity)
            logger.debug(f"Calculated nutrition: {nutrition}")

            # Create new Food_Eaten entry
            food_entry = Food_Eaten.objects.create(
                user=request.user,
                food_name=food_name,
                quantity=quantity,
                measurement_type=base_nutrition['measurement_type'],
                unit_label=base_nutrition['unit_label'],
                calories=nutrition['calories'],
                fat=nutrition['fat'],
                carbs=nutrition['carbs'],
                protein=nutrition['protein']
            )

            # Log successful creation
            logger.debug(f"Food entry created: {food_entry.id}")

            quantity_str = f"{quantity}g" if base_nutrition[
                                                 'measurement_type'] == 'g' else f"{quantity} {base_nutrition['unit_label']}{'s' if quantity > 1 else ''}"
            messages.success(request, f'Added {quantity_str} of {food_name} to your food log!')

        except Exception as e:
            # Log any errors that occur
            logger.error(f"Error adding food: {str(e)}")
            messages.error(request, "An error occurred while adding the food. Please try again.")

    return redirect('home')

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
