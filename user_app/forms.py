from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

# from .models import User


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=100, required=True)

    class Meta:
        User = get_user_model()
        model = User
        fields = ('username', 'password1', 'password2', 'email')

    def clean_email(self):
        User = get_user_model()
        if User.objects.filter(email=self.cleaned_data.get("email")).exists():
            raise forms.ValidationError("A user with that email already exists.")


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.PasswordInput()

    class Meta:
        fields = ('password', 'email')
