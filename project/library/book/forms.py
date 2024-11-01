from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class RegisterForm(UserCreationForm):
    name = forms.CharField(max_length=150, required=True, help_text="Enter your full name")

    class Meta:
        model = User
        fields = ['username', 'name', 'password1', 'password2']  # Поля: username, name, password1, password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['name']  # Зберігаємо name у поле first_name
        if commit:
            user.save()
        return user
