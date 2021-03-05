from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model, authenticate


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=100, required=True)

    class Meta:
        User = get_user_model()
        model = User
        fields = ('username', 'password1', 'password2', 'email')

    def clean_email(self):
        User = get_user_model()
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with that email already exists.")
        return email


class AuthenticationForm(forms.ModelForm):

    password = forms.PasswordInput()

    class Meta:
        User = get_user_model()
        model = User
        fields = ('username', 'password')

    def clean(self):
        if self.is_valid():
            username = self.cleaned_data['username']
            password = self.cleaned_data['password']
            if not authenticate(username=username, password=password):
                raise forms.ValidationError("Invalid login")


class EditProfileForm(forms.Form):
    bio = forms.CharField(widget=forms.Textarea, required=False)

    def clean_bio(self):
        bio = self.cleaned_data.get('bio')
        bio_len = len(bio)
        if bio_len > 500:
            raise forms.ValidationError("Max length for bio is 500 chars. Current len is {} chars".format(bio_len))
        return bio
