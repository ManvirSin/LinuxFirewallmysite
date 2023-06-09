from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.shortcuts import render, redirect
from Firewallsite import settings

PROTOCOL_CHOICES = (
    ('TCP', 'TCP'),
    ('UDP', 'UDP'),
    ('ICMP', 'ICMP'),
    ('ANY', 'ANY'),
)

PROTOCOL_CHOICES = [    ('TCP', 'TCP'),    ('UDP', 'UDP'),    ('ICMP', 'ICMP')]

ACTION_CHOICES = (
        ('ACCEPT', 'ACCEPT'),
        ('DROP', 'DROP'),
        ('REJECT', 'REJECT'),
    )

class CustomUser(AbstractUser):
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)

class FirewallRule(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rule_name = models.CharField(max_length=100)
    chain = models.CharField(max_length=255, default='INPUT')
    source_ip = models.GenericIPAddressField(protocol='both', unpack_ipv4=True)
    destination_ip = models.GenericIPAddressField(protocol='both', unpack_ipv4=True, default='0.0.0.0')
    protocol = models.CharField(max_length=10, choices=PROTOCOL_CHOICES, default='TCP')
    source_port = models.PositiveIntegerField(blank=True, null=True)
    destination_port = models.PositiveIntegerField(blank=True, null=True)
    action = models.CharField(max_length=255, default='ACCEPT')
    log_traffic = models.BooleanField(default=False)
    alert_user = models.BooleanField(default=False)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES, default='ACCEPT')

    def __str__(self):
        return self.rule_name

class NAT(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rule_name = models.CharField(max_length=100)
    direction = models.CharField(max_length=10)
    protocol = models.CharField(max_length=10, choices=PROTOCOL_CHOICES, default='TCP')
    source_port = models.PositiveIntegerField(blank=True, null=True)
    destination_ip = models.GenericIPAddressField(protocol='both', unpack_ipv4=True, default='0.0.0.0')
    destination_port = models.PositiveIntegerField(blank=True, null=True)
    target_ip = models.GenericIPAddressField()
    target_port = models.PositiveIntegerField(blank=True, null=True)
