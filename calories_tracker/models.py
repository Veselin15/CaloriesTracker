from calories_tracker.choices import MealChoices
from accounts.models import User
from django.db import models
import re


class Food_Eaten(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    food_name = models.CharField(max_length=100)
    quantity = models.FloatField(default=1)
    measurement_type = models.CharField(max_length=10, default='g')  # 'g' or 'unit'
    unit_label = models.CharField(max_length=50, blank=True, null=True)
    calories = models.FloatField()
    fat = models.FloatField()
    carbs = models.FloatField()
    protein = models.FloatField()
    date_eaten = models.DateTimeField(auto_now_add=True)
    food_image = models.URLField(max_length=500, blank=True, null=True)
    meal = models.ForeignKey('Meal', on_delete=models.CASCADE, blank=True, null=True, related_name='foods_eaten')

    def save(self, *args, **kwargs):
        import datetime
        if self.date_eaten:
            self.date_eaten = self.date_eaten.replace(second=0, microsecond=0)
        super().save(*args, **kwargs)

    @staticmethod
    def parse_nutrition(food_description):
        """Parse nutrition information from food description"""
        # First try to match the entire "Per X unit" pattern
        per_pattern = r'Per\s+(?:(\d*\.?\d*)?\s*)?(?:(\d+/\d+)\s+)?([^-]*?)(?=\s*-|Calories|$)'
        per_match = re.search(per_pattern, food_description, re.IGNORECASE)

        if per_match:
            # Extract quantity and unit information
            number = per_match.group(1)
            fraction = per_match.group(2)
            unit_text = per_match.group(3).strip().lower()

            # Calculate base_amount from number or fraction
            if fraction:
                try:
                    num, denom = map(float, fraction.split('/'))
                    base_amount = num / denom
                except ValueError:
                    base_amount = 1.0
            else:
                base_amount = float(number) if number else 1.0
                base_amount = round(base_amount, 2)

            # Check if the unit is a weight measurement
            weight_match = re.search(r'(\d*\.?\d*)\s*(oz|g|ml)$', unit_text)
            if weight_match:
                measurement_type = 'g'
                unit_label = 'g'

                # Handle weight conversions
                if 'oz' in unit_text:
                    base_amount = base_amount * 28.35
                elif 'ml' in unit_text:
                    base_amount = base_amount  # Assuming density of water
            else:
                measurement_type = 'unit'
                # Clean up unit text
                unit_label = re.sub(r'\s+', ' ', unit_text).strip()
                if not unit_label:
                    unit_label = 'piece'

        else:
            # Default to per 100g if no specific unit is found
            base_amount = 100.0
            measurement_type = 'g'
            unit_label = 'g'

        # Extract nutrition values
        calories = re.search(r'Calories:\s*(\d+)kcal', food_description)
        fat = re.search(r'Fat:\s*([\d.]+)g', food_description)
        carbs = re.search(r'Carbs:\s*([\d.]+)g', food_description)
        protein = re.search(r'Protein:\s*([\d.]+)g', food_description)

        return {
            'base_amount': base_amount,
            'measurement_type': measurement_type,
            'unit_label': unit_label,
            'calories': int(calories.group(1)) if calories else 0,
            'fat': float(fat.group(1)) if fat else 0.0,
            'carbs': float(carbs.group(1)) if carbs else 0.0,
            'protein': float(protein.group(1)) if protein else 0.0
        }

    @staticmethod
    def calculate_nutrition_for_quantity(nutrition_data, desired_quantity):
        """Calculate nutrition values for a given quantity"""
        base_amount = nutrition_data['base_amount']

        # Calculate the multiplier based on the ratio of desired quantity to base amount
        multiplier = desired_quantity / base_amount

        # Calculate and round the values
        return {
            'calories': round(nutrition_data['calories'] * multiplier),
            'fat': round(nutrition_data['fat'] * multiplier, 2),
            'carbs': round(nutrition_data['carbs'] * multiplier, 2),
            'protein': round(nutrition_data['protein'] * multiplier, 2)
        }
class Meal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=20, choices=MealChoices)
    date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'name', 'date')

class Goal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    daily_calorie_goal = models.IntegerField(blank=True, null=True)
    daily_fat_goal = models.IntegerField(blank=True, null=True)
    daily_carbs_goal = models.IntegerField(blank=True, null=True)
    daily_protein_goal = models.IntegerField(blank=True, null=True)
    weight_goal = models.IntegerField(blank=True, null=True)

class WeightLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    weight = models.FloatField()
    date = models.DateField(auto_now_add=True)
