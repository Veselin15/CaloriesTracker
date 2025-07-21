from django.db.models import Sum
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Meal, WeightLog
from datetime import date, datetime, timedelta
from CaloriesTracker import settings
from .fatsecret_utils import search_food
from .forms import AddFoodForm, FoodSearchForm, WeightLogForm
from .models import Food_Eaten
import logging
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

logger = logging.getLogger(__name__)

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

    return render(request, "home.html", {})


def search_for_foods(request):
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
    return render(request, "calories_tracker/search_for_foods.html", context)


@login_required
def add_food(request):
    food_data = None
    today = date.today()
    selected_date = today

    if request.method == 'GET':
        # Get food details from query parameters (from search results)
        food_name = request.GET.get('food_name')
        food_description = request.GET.get('food_description')

        if food_name and food_description:
            food_data = {
                'food_name': food_name,
                'food_description': food_description
            }
        date_str = request.GET.get('date')
        if date_str:
            try:
                selected_date = date.fromisoformat(date_str)
            except ValueError:
                selected_date = today
        return render(request, "calories_tracker/add_food.html", {
            'food': food_data,
            'today': today,
            'selected_date': selected_date,
        })

    elif request.method == 'POST':
        today = date.today()
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

            # Get the date from the form, default to today
            date_str = request.POST.get('date')
            if date_str:
                try:
                    selected_date = date.fromisoformat(date_str)
                except ValueError:
                    selected_date = today
            else:
                selected_date = today
            date_eaten = datetime.combine(selected_date, datetime.now().time())
            # Get or create the Meal instance for this user, date, and meal type
            meal_obj, created = Meal.objects.get_or_create(
                user=request.user,
                name=meal_type,
                date=selected_date
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
                protein=nutrition['protein'],
                meal_id=meal_obj.id,
                date_eaten = date_eaten
            )

            # Associate the food entry with the meal

            quantity_str = f"{quantity}g" if measurement_type == 'g' else f"{quantity} {unit_label}{'s' if quantity > 1 else ''}"
            messages.success(request, f'Added {quantity_str} of {food_name} to your {meal_type}!')

            return redirect('home')

        except Exception as e:
            messages.error(request, f"Error adding food: {str(e)}")

    return render(request, "calories_tracker/add_food.html", {
        'food': food_data,
        'today': today,
        'selected_date': selected_date,
    })

from django.utils import timezone
from django.http import HttpResponseRedirect
from django.urls import reverse


class MyMealsView(LoginRequiredMixin, View):
    def get(self, request):
        import datetime
        # Get date from query params, default to today
        date_str = request.GET.get('date')
        if date_str:
            try:
                selected_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                selected_date = timezone.localdate()
        else:
            selected_date = timezone.localdate()
        # Always calculate prev/next based on selected_date
        prev_date = selected_date - datetime.timedelta(days=1)
        next_date = selected_date + datetime.timedelta(days=1)
        meals = Meal.objects.filter(user=request.user, date=selected_date).order_by('name')
        foods = Food_Eaten.objects.filter(user=request.user, date_eaten__date=selected_date).order_by('meal__name')
        context = {
            'meals': meals,
            'foods': foods,
            'selected_date': selected_date,
            'prev_date': prev_date,
            'next_date': next_date,
        }
        return render(request, "calories_tracker/my_meals.html", context)

    def post(self, request):
        # Handle meal deletion
        meal_id = request.POST.get('delete_meal_id')
        food_id = request.POST.get('delete_food_id')
        date_str = request.POST.get('date')
        if meal_id:
            try:
                meal = Meal.objects.get(id=meal_id, user=request.user)
                meal.delete()
            except Meal.DoesNotExist:
                pass
        elif food_id:
            try:
                food = Food_Eaten.objects.get(id=food_id, user=request.user)
                food.delete()
            except Food_Eaten.DoesNotExist:
                pass
        # Redirect back to the same date
        redirect_url = reverse('my_meals')
        if date_str:
            redirect_url += f'?date={date_str}'
        return HttpResponseRedirect(redirect_url)

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import GoalForm
from .models import Goal

@login_required
def set_goals(request):
    goal, created = Goal.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = GoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            return redirect('home')  # or wherever you want to redirect
    else:
        form = GoalForm(instance=goal)
    return render(request, 'calories_tracker/set_goals.html', {'form': form})

@login_required
def track_weight(request):
    today = date.today()
    weight_entries = WeightLog.objects.filter(user=request.user).order_by('-date')
    form = WeightLogForm()

    if request.method == 'POST':
        if 'delete_weight_id' in request.POST:
            # Handle deletion
            entry_id = request.POST.get('delete_weight_id')
            WeightLog.objects.filter(id=entry_id, user=request.user).delete()
            messages.success(request, "Weight entry deleted.")
            return redirect('track_weight')
        else:
            # Handle add/update for today's date only
            form = WeightLogForm(request.POST)
            if form.is_valid():
                weight = form.cleaned_data['weight']
                weight_entry, created = WeightLog.objects.update_or_create(
                    user=request.user,
                    date=today,
                    defaults={'weight': weight}
                )
                if created:
                    messages.success(request, "Weight entry added for today.")
                else:
                    messages.success(request, "Weight entry updated for today.")
                return redirect('track_weight')
            else:
                messages.error(request, "Please correct the errors below.")

    context = {
        'form': form,
        'weight_entries': weight_entries,
        'today': today,
    }
    return render(request, 'calories_tracker/track_weight.html', context)


@login_required
def statistics(request):
    today = timezone.localdate()
    week_ago = today - timedelta(days=6)
    # Weight data for the last 30 days
    weight_logs = WeightLog.objects.filter(user=request.user, date__gte=today - timedelta(days=29)).order_by('date')
    weights = [{'date': wl.date.strftime('%Y-%m-%d'), 'weight': wl.weight} for wl in weight_logs]

    # Calories per day for the last 7 days
    calories_per_day = (
        Food_Eaten.objects.filter(user=request.user, date_eaten__date__gte=week_ago)
        .values('date_eaten__date')
        .annotate(total_calories=Sum('calories'))
        .order_by('date_eaten__date')
    )
    calories = [{'date': c['date_eaten__date'].strftime('%Y-%m-%d'), 'calories': c['total_calories'] or 0} for c in calories_per_day]

    # Macro breakdown for the last 7 days
    macros = (
        Food_Eaten.objects.filter(user=request.user, date_eaten__date__gte=week_ago)
        .aggregate(
            protein=Sum('protein'),
            carbs=Sum('carbs'),
            fat=Sum('fat')
        )
    )

    context = {
        'weights': weights,
        'calories': calories,
        'macros': macros,
    }
    return render(request, 'calories_tracker/statistics.html', context)