from django.db import models
from .models import NAT, FirewallRule
from django.contrib import admin
from .models import User

admin.site.register(User)

admin.site.register(NAT)
admin.site.register(FirewallRule)

class User(models.Model):
    name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=50)

