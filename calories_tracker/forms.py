from django import forms

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