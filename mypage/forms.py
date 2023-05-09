import subprocess
from subprocess import run, PIPE
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.shortcuts import render

from Firewallsite.settings import FIREWALL_IP
from .models import NAT, CustomUser, FirewallRule
from django.core.exceptions import ValidationError

class FirewallRuleForm(forms.ModelForm):
    ip_address = forms.GenericIPAddressField()
    class Meta:
        model = FirewallRule
        fields = [
            'user', 'rule_name', 'chain', 'source_ip', 'destination_ip',
            'protocol', 'source_port', 'destination_port', 'action',
            'log_traffic', 'alert_user'
        ]

    def __init__(self, *args, **kwargs):
        firewall_ip = kwargs.pop('firewall_ip', None)
        user = kwargs.pop('user', None)
        super(FirewallRuleForm, self).__init__(*args, **kwargs)
        self.fields['source_ip'].initial = FIREWALL_IP
        self.fields['ip_address'].initial = firewall_ip
        self.fields['ip_address'].widget.attrs['readonly'] = True
        self.user = user

    def save(self, commit=True):
        instance = super(FirewallRuleForm, self).save(commit=False)
        instance.source_ip = FIREWALL_IP  # Set the source_ip to the value of FIREWALL_IP
        if commit:
            instance.save()
        return instance
    
    def clean(self):
        cleaned_data = super().clean()
        source_port = cleaned_data.get('source_port')
        destination_port = cleaned_data.get('destination_port')

        if source_port and destination_port and source_port == destination_port:
            raise ValidationError("Source port and destination port cannot be the same.")
        return cleaned_data

class UserCreateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['name', 'surname', 'email', 'username', 'password']
        widgets = {
            'password': forms.PasswordInput(),
        }
        
    def save(self, commit=True):
        user = super(UserCreateForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user
    
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super(CustomUserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
        

class NatRuleForm(forms.ModelForm):
    source_ip = forms.GenericIPAddressField()
    class Meta:
        model = NAT
        fields = [
            'user', 'rule_name', 'direction', 'protocol', 'source_port',
            'destination_ip', 'destination_port', 'target_port'
        ]
        
        
    def clean(self):
        cleaned_data = super().clean()
        source_port = cleaned_data.get('source_port')
        destination_port = cleaned_data.get('destination_port')

        if source_port and destination_port and source_port == destination_port:
            raise ValidationError("Source port and destination port cannot be the same.")
        return cleaned_data
    
    def __init__(self, *args, **kwargs):
        firewall_ip = kwargs.pop('firewall_ip', None)
        super(NatRuleForm, self).__init__(*args, **kwargs)
        self.fields['source_ip'].initial = FIREWALL_IP
        self.fields['source_ip'].widget.attrs['readonly'] = True
