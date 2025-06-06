from django import template
from calories_tracker.models import Food_Eaten

register = template.Library()

@register.filter(name='parse_nutrition')
def parse_nutrition(food_description):
    """Parse nutrition information from food description"""
    if isinstance(food_description, dict):
        food_description = food_description.get('food_description', '')
    return Food_Eaten.parse_nutrition(food_description)