from http import HTTPStatus
from urllib import response

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

User = get_user_model()

class StaticUrlTest(TestCase):
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        # Клиент незалогиненного пользователя
        self.guest_client = Client()        

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def test_task_list_url_redirect_anonymous(self):
        """Страница /task/ перенаправляет анонимного пользователя."""
        response = self.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, 200)


    def test_about_correct_template(self):
        pages = {
            'about:author': 'about/author.html',
            'about:tech': 'about/tech.html',
        }
        for address, template in pages.items():
            with self.subTest(address=address):
                self.assertTemplateUsed(
                    self.guest_client.get(reverse(address)),
                    template
                )
