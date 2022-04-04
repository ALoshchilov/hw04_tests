from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, Group, User

AUTOTEST_AUTH_USERNAME = 'AutoTestUser'
NOT_AUTHOR = 'NotAuthor'
TEST_GROUP_SLUG = 'TestGroupSlug'
UNEXISTING_PAGE_URL = '/ThisPageIsALieAndTheTestAsWell/'


class StaticUrlTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=AUTOTEST_AUTH_USERNAME)
        cls.not_author = User.objects.create_user(username=NOT_AUTHOR)
        cls.group = Group.objects.create(
            title='Тестовая группа. Заголовок',
            slug=TEST_GROUP_SLUG,
            description='Тестовая группа. Описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Текст. Автотест',
        )
        cls.routes = {
            'users:login': reverse('users:login'),
            'posts:post_create': reverse('posts:post_create'),
            'posts:post_edit': reverse('posts:post_edit', args=[cls.post.id]),
            'posts:post_detail': reverse(
                'posts:post_detail', args=[cls.post.id]
            )
        }

    def setUp(self):
        # Клиент незалогиненного пользователя
        self.guest_client = Client()
        # Клиент залогиненного пользователя
        self.auth_client = Client()
        self.auth_client.force_login(StaticUrlTest.user)

        self.not_author_client = Client()
        self.not_author_client.force_login(StaticUrlTest.not_author)

    def test_user_direct_access(self):
        urls = [
            ('/', self.guest_client, HTTPStatus.OK),
            ('/', self.auth_client, HTTPStatus.OK),
            (f'/group/{TEST_GROUP_SLUG}/', self.guest_client, HTTPStatus.OK),
            (f'/group/{TEST_GROUP_SLUG}/', self.auth_client, HTTPStatus.OK),
            (
                f'/profile/{AUTOTEST_AUTH_USERNAME}/',
                self.guest_client, HTTPStatus.OK
            ),
            (
                f'/profile/{AUTOTEST_AUTH_USERNAME}/',
                self.auth_client, HTTPStatus.OK
            ),
            (
                f'/posts/{StaticUrlTest.post.id}/', self.guest_client,
                HTTPStatus.OK
            ),
            (
                f'/posts/{StaticUrlTest.post.id}/', self.auth_client,
                HTTPStatus.OK
            ),
            ('/create/', self.guest_client, HTTPStatus.FOUND),
            ('/create/', self.auth_client, HTTPStatus.OK),
            (
                f'/posts/{StaticUrlTest.post.id}/edit/',
                self.auth_client, HTTPStatus.OK
            ),
            (
                f'/posts/{StaticUrlTest.post.id}/edit/',
                self.guest_client, HTTPStatus.FOUND
            ),
            (
                f'/posts/{StaticUrlTest.post.id}/edit/',
                self.not_author_client, HTTPStatus.FOUND
            ),
            (UNEXISTING_PAGE_URL, self.guest_client, HTTPStatus.NOT_FOUND),
            (UNEXISTING_PAGE_URL, self.auth_client, HTTPStatus.NOT_FOUND),
        ]
        for url in urls:
            with self.subTest(url[0]):
                self.assertEqual(
                    url[1].get(url[0]).status_code,
                    url[2],
                    f'{url[0]} returned wrong status code for client {url[1]}'
                )

    def test_guest_user_redirect(self):
        urls = [
            (
                '/create/', self.guest_client,
                StaticUrlTest.routes['users:login'] + '?next='
                + StaticUrlTest.routes['posts:post_create']
            ),
            (
                f'/posts/{StaticUrlTest.post.id}/edit/',
                self.guest_client,
                StaticUrlTest.routes['users:login'] + '?next='
                + StaticUrlTest.routes['posts:post_edit']
            ),
            (
                f'/posts/{StaticUrlTest.post.id}/edit/',
                self.not_author_client,
                StaticUrlTest.routes['posts:post_detail']
            ),
        ]
        for url in urls:
            with self.subTest(url[0]):
                self.assertRedirects(
                    url[1].get(url[0], follow=True),
                    url[2],
                    msg_prefix=(
                        f'Expected redirect ({url[0]})'
                        f' ---> {url[2]}'
                    )
                )

    def test_correct_template(self):
        urls = [
            ('/', self.auth_client, 'posts/index.html'),
            (
                f'/group/{TEST_GROUP_SLUG}/', self.auth_client,
                'posts/group_list.html'
            ),
            (
                f'/profile/{AUTOTEST_AUTH_USERNAME}/', self.auth_client,
                'posts/profile.html'
            ),
            (
                f'/posts/{StaticUrlTest.post.id}/', self.auth_client,
                'posts/post_detail.html'),
            ('/create/', self.auth_client, 'posts/create_post.html'),
            (
                f'/posts/{StaticUrlTest.post.id}/edit/', self.auth_client,
                'posts/create_post.html'
            ),
        ]
        for url in urls:
            with self.subTest(url[0]):
                self.assertTemplateUsed(
                    url[1].get(url[0]),
                    url[2],
                    f'Wrong template for {url[0]} found. Expected: {url[2]}'
                )
