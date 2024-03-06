from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm

from .forms import CreateUserForm
# Create your views here.
def loginPage(request):
    context = {}
    return render(request,'accounts/login.html', context)

def registerPage(request):
    form = CreateUserForm()

    if request.method == 'POST':
        form  = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()

    context ={'form':form}
    return render(request,'accounts/register.html', context)
