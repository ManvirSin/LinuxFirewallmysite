"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from mypage import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),  # Home page
    path('configuration/', views.configuration_view, name='configuration'),  # Configuration page
    path('dashboard/', views.dashboard_view, name='dashboard'),  # Dashboard page
    path('login/', views.login_view, name='login'),  # Login page
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),  # logout
    path('create_account/', views.AccountView.as_view(), name='create_account'),  # Page to create user account
    path('natconfig/', views.natconfig_view, name='natconfig'),  # NAT configuration page
]



