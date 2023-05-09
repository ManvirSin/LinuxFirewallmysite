from pstats import Stats
import statistics
from django.test import Client, TestCase
from django.contrib.auth.models import User, AbstractUser
from django.urls import reverse
from mypage.models import MyModel
from django.contrib.auth.models import User, AbstractUser
from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
import unittest


class TestViews(TestCase):

    def setUp(self):
        self.my_model = MyModel.objects.create(name='test name')
        self.client = Client()

    def test_home_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_my_model_str(self):
        self.assertEqual(str(self.my_model), 'test name')

    # more tests ...


class MyModelTests(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.my_model = MyModel.objects.create(name='test name')

    def test_create_my_model(self):
        url = reverse('my-model-list')
        data = {'name': 'new name'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, Stats.HTTP_201_CREATED)
        self.assertEqual(MyModel.objects.count(), 2)
        self.assertEqual(MyModel.objects.last().name, 'new name')

    def test_get_my_model(self):
        url = reverse('my-model-detail', args=[self.my_model.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, statistics.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'test name')

class TestViews(TestCase):
    def setUp(self):
        self.my_model = MyModel.objects.create(name='test name')
    
    def test_home_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        
    def test_my_model_str(self):
        self.assertEqual(str(self.my_model), 'test name')
        
    def test_my_model_name_max_length(self):
        max_length = self.my_model._meta.get_field('name').max_length
        self.assertEqual(max_length, 50)
        
    def test_create_my_model(self):
        response = self.client.post(reverse('create'), {'name': 'new name'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(MyModel.objects.count(), 2)
        
    def test_update_my_model(self):
        url = reverse('update', args=[self.my_model.id])
        response = self.client.post(url, {'name': 'updated name'})
        self.assertEqual(response.status_code, 302)
        self.my_model.refresh_from_db()
        self.assertEqual(self.my_model.name, 'updated name')
        
    def test_delete_my_model(self):
        url = reverse('delete', args=[self.my_model.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(MyModel.objects.count(), 0)
        
    def test_my_model_list_view(self):
        response = self.client.get(reverse('list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'list.html')
        self.assertContains(response, 'test name')
        
    def test_my_model_detail_view(self):
        url = reverse('detail', args=[self.my_model.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'detail.html')
        self.assertContains(response, 'test name')
        
    def test_my_model_create_view(self):
        response = self.client.get(reverse('create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create.html')
        self.assertContains(response, '<input type="text" name="name"')
