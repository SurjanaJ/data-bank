from django.urls import include, path

from accounts import views

urlpatterns=[
    path('login/', views.loginPage, name='login'),
    path('register/', views.registerPage, name='register'),
    path('logout/', views.logoutPage, name='logout'),


]