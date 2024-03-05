from django.shortcuts import render

# Create your views here.
def loginPage(request):
    context = {}
    return render(request,'accounts/login.html', context)

def registerPage(request):
    context ={}
    return render(request,'accounts/register.html', context)
