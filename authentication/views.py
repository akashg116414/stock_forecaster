# -*- encoding: utf-8 -*-


from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.forms.utils import ErrorList
from django.http import HttpResponse

# Create your views here.
from django.shortcuts import redirect, render

from .forms import LoginForm, SignUpForm


def login_view(request):
    # Check if the user is already authenticated
    if request.user.is_authenticated:
        return redirect("/")

    form = LoginForm(request.POST or None)
    msg = None

    if request.method == "POST":
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                request.session["authenticated"] = True
                return redirect("/")
            else:
                msg = 'Invalid credentials'
        else:
            msg = 'Error validating the form'

    return render(request, "accounts/login.html", {"form": form, "msg": msg})

def register_user(request):
    # Check if the user is already authenticated
    if request.user.is_authenticated:
        return redirect("/")

    msg = None
    success = False

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_password)

            msg = 'User created.'
            success = True

            # return redirect("/login/")

        else:
            msg = 'Form is not valid'
    else:
        form = SignUpForm()

    return render(request, "accounts/register.html", {"form": form, "msg": msg, "success": success})


def logout_view(request):
    logout(request)
    return redirect('login') 
