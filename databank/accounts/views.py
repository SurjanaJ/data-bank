from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .decorators import unauthenticated_user

from .forms import CreateUserForm
from django.contrib.auth.models import Group


@unauthenticated_user
def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
            
        user = authenticate(request, username= username, password = password)

        if user is not None:
            login(request, user)
            return redirect('display_trade_table')
        else:
            messages.info(request, 'username OR password is incorrect.')

    context = {}
    return render(request,'accounts/login.html', context)
        

@unauthenticated_user
def registerPage(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form  = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()

            group = Group.objects.get(name = 'downloader')
            user.groups.add(group)
            
            messages.success(request, 'Account created successfully.')
            return redirect('login')
    context ={'form':form}
    return render(request,'accounts/register.html', context)   
    

def logoutPage(request):
    logout(request)
    return redirect('login')