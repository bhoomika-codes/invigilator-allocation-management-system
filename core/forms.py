from django import forms
from django.contrib.auth.models import User
from .models import Lecturer

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    name = forms.CharField(max_length=100)
    faculty_id = forms.CharField(required=False)
    department = forms.CharField(max_length=100)
    role = forms.ChoiceField(choices=Lecturer.ROLE_CHOICES)

    class Meta:
        model = User
        fields = ['username', 'password']
        help_texts = {
            'username': '',   # ✅ removes that ugly text
        }