from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect


def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('user_app:login')
    else:
        form = UserCreationForm()
    return render(request, 'user_app/signup.html', {'form': form})


def testing_redirect(request):
    return redirect('user_app:login')
