from django import forms
from datetime import date
from django import forms
from .models import Goal, WeightLog


class FoodSearchForm(forms.Form):
    query = forms.CharField(
        label='Search for food',
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'e.g., apple or banana'})
    )

class AddFoodForm(forms.Form):
    UNIT_CHOICES = [
        ('g', 'grams'),
        ('unit', 'pieces')
    ]

    food_name = forms.CharField(widget=forms.HiddenInput())
    food_description = forms.CharField(widget=forms.HiddenInput())
    measurement_type = forms.CharField(widget=forms.HiddenInput())
    unit_label = forms.CharField(widget=forms.HiddenInput(), required=False)
    quantity = forms.FloatField(
        min_value=0.1,
        initial=1,
        label='Quantity',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.1',
        })
    )
    date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=date.today
    )


class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = [
            'daily_calorie_goal',
            'daily_fat_goal',
            'daily_carbs_goal',
            'daily_protein_goal',
            'weight_goal'
        ]
        widgets = {
            'daily_calorie_goal': forms.NumberInput(attrs={'placeholder': 'Calories'}),
            'daily_fat_goal': forms.NumberInput(attrs={'placeholder': 'Fat (g)'}),
            'daily_carbs_goal': forms.NumberInput(attrs={'placeholder': 'Carbs (g)'}),
            'daily_protein_goal': forms.NumberInput(attrs={'placeholder': 'Protein (g)'}),
            'weight_goal': forms.NumberInput(attrs={'placeholder': 'Target Weight (kg)'}),
        }

class WeightLogForm(forms.ModelForm):
    class Meta:
        model = WeightLog
        fields = ['weight']  # Only allow user to set weight
        widgets = {
            'weight': forms.NumberInput(attrs={
                'class': 'form-control form-control-lg',
                'step': '0.1',
                'min': '0',
                'placeholder': 'e.g. 70.5'
            }),
        }