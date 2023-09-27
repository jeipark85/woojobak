from django import forms
from .models import BlogPost
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth.forms import AuthenticationForm


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Username or Email", "class": "login-input"}),
        label="",
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Password", "class": "login-input"}),
        label="",
    )


class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        exclude = ["created_at"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["topic"].required = False
        self.fields["publish"].required = False
        self.fields["views"].required = False


# 회원가입 0927
class SignupForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        label="",
        widget=forms.TextInput(attrs={"placeholder": "Username"}),
    )
    email = forms.EmailField(
        label="",
        widget=forms.EmailInput(attrs={"placeholder": "Email"}),
    )
    password = forms.CharField(
        label="",
        widget=forms.PasswordInput(attrs={"placeholder": "Password"}),
    )
    re_password = forms.CharField(
        label="",
        widget=forms.PasswordInput(attrs={"placeholder": "Confirm Password"}),
    )

    def save(self):
        username = self.cleaned_data["username"]
        email = self.cleaned_data["email"]
        password = self.cleaned_data["password"]

        user = User.objects.create_user(
            username=username, email=email, password=make_password(password)
        )
        return user
