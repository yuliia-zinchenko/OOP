from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from .validators import validate_username, validate_no_spaces
from django.core.exceptions import ValidationError


class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput())


# class RegisterForm(UserCreationForm):

#     email = forms.EmailField(required=True)
#     username = forms.CharField(
#     max_length=30,
#     validators=[validate_username],  
#     widget=forms.TextInput(attrs={'placeholder': 'Username'}),
#     )

#     first_name = forms.CharField(
#     max_length=20,  
#     validators=[validate_no_spaces], 
#     widget=forms.TextInput(attrs={'placeholder': 'First Name'})
#     )
#     last_name = forms.CharField(
#     max_length=20,
#     validators=[validate_no_spaces],  
#     widget=forms.TextInput(attrs={'placeholder': 'Last Name'})
#     )

#     class Meta:
#         model = get_user_model()
#         fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2'] 

#     def save(self, commit=True):
#         user = super(RegisterForm, self).save(commit=False)
#         user.email = self.cleaned_data['email']
#         user.first_name = self.cleaned_data['first_name']
#         user.last_name = self.cleaned_data['last_name'] 
#         if commit:
#             user.save()
#         return user
    
class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    username = forms.CharField(
        max_length=30,
        validators=[validate_username],
        widget=forms.TextInput(attrs={'placeholder': 'Username'}),
    )
    first_name = forms.CharField(
        max_length=20,
        validators=[validate_no_spaces],
        widget=forms.TextInput(attrs={'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=20,
        validators=[validate_no_spaces],
        widget=forms.TextInput(attrs={'placeholder': 'Last Name'})
    )

    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2'] 

    def clean_email(self):
        # Перевірка на унікальність email
        email = self.cleaned_data.get('email')
        if get_user_model().objects.filter(email=email).exists():
            raise ValidationError("An account with this email already exists.")
        return email

    def save(self, commit=True):
        # Використовуємо суперклас для збереження користувача
        user = super(RegisterForm, self).save(commit=False)
        
        # Оновлюємо додаткові поля
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        # Збереження користувача, якщо commit = True
        if commit:
            user.save()
        return user


class ProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(
    max_length=20,  
    validators=[validate_no_spaces], 
    widget=forms.TextInput(attrs={'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
    max_length=20,
    validators=[validate_no_spaces],  
    widget=forms.TextInput(attrs={'placeholder': 'Last Name'})
    )
    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name']

class PasswordResetForm(PasswordResetForm):
    class Meta:
        model = get_user_model()
        fields = ['new_password1', 'new_password2']

class SetPasswordForm(SetPasswordForm):
    class Meta:
        model = get_user_model()
        fields = ['new_password1', 'new_password2'] 