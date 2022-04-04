from django.test import TestCase
from django.urls import reverse


class RoutesTest(TestCase):

    @classmethod
    def setUp(self):
        super().setUpClass()
        self.PAGE_NUMBER = 1
        self.USER = 'User'
        self.GROUP = 'Group'

    def test_correct_routes(self):
        print(self.GROUP)
        routes = {
            reverse('posts:index'): '/',
            reverse(
                'posts:group_list', args=[self.GROUP]
            ): f'/group/{self.GROUP}/',
            reverse(
                'posts:profile', args=[self.USER]
            ): f'/profile/{self.USER}/',
            reverse('posts:post_create'): '/create/',
            reverse(
                'posts:post_edit', args=[self.PAGE_NUMBER]
            ): f'/posts/{self.PAGE_NUMBER}/edit/',
            reverse(
                'posts:post_detail', args=[self.PAGE_NUMBER]
            ): f'/posts/{self.PAGE_NUMBER}/',
        }
        for route, expected_route in routes.items():
            with self.subTest(route=route):
                self.assertEqual(
                    route, expected_route,
                    (
                        f'Wrong route. Got: {route}'
                        f'Expected: {expected_route}'
                    )
                )
