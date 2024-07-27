from django import forms
from .models import UserDetails

class UserDetailsForm(forms.ModelForm):
    class Meta:
        model = UserDetails
        fields = ['name', 'age', 'gender', 'occupation']

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = UserDetails
        fields = ['feedback']
