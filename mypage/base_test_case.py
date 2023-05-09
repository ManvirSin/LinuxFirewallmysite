from django.test import TestCase
from django.urls import reverse
from httpx import Client
from mypage.models import CustomUser, FirewallRule, User

class BaseTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.test_user = CustomUser.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        self.dashboard_url = reverse('dashboard')
        self.configuration_url = reverse('configuration')

    def _login(self):
        self.client.login(username='testuser', password='testpassword')

    def _create_firewall_rule(self, **kwargs):
        default_data = {
            'name': 'test rule',
            'source_address': '1.2.3.4',
            'destination_address': '5.6.7.8',
            'protocol': 'tcp',
            'action': 'allow'
        }
        default_data.update(kwargs)
        return FirewallRule.objects.create(**default_data)
