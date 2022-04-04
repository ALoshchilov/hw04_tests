from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, Group, User
from posts.settings import POSTS_ON_PAGE

TEST_GROUP_SLUG = 'TestGroupSlug'
TEST_GROUP_SLUG_1 = 'TestGroupSlug1'
AUTOTEST_AUTH_USERNAME = 'AutoTestUser'

CONST_URLS = {
    'posts:index': reverse('posts:index'),
    'posts:post_create': reverse('posts:post_create'),
    'posts:group_list': reverse(
        'posts:group_list', args=[TEST_GROUP_SLUG]
    ),
    'posts:profile': reverse(
        'posts:profile', args=[AUTOTEST_AUTH_USERNAME]
    )
}

# Константы и переменные для проверки пагинатора
TEST_POSTS_COUNT = 56
posts_on_last_page = TEST_POSTS_COUNT % POSTS_ON_PAGE
if TEST_POSTS_COUNT <= POSTS_ON_PAGE:
    posts_on_first_page = TEST_POSTS_COUNT
    total_pages = 1
else:
    if TEST_POSTS_COUNT % POSTS_ON_PAGE == 0:
        posts_on_last_page = POSTS_ON_PAGE
        total_pages = TEST_POSTS_COUNT // POSTS_ON_PAGE
    else:
        total_pages = TEST_POSTS_COUNT // POSTS_ON_PAGE + 1
    posts_on_first_page = POSTS_ON_PAGE


class ContextViewsTest(TestCase):

    @classmethod
    def setUpClass(cls):

        super().setUpClass()
        cls.user = User.objects.create_user(username=AUTOTEST_AUTH_USERNAME)
        cls.group_1 = Group.objects.create(
            title='Тестовая группа 1. Заголовок',
            slug=TEST_GROUP_SLUG,
            description='Тестовая группа 1. Описание',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа 2. Заголовок',
            slug=TEST_GROUP_SLUG_1,
            description='Тестовая группа 2. Проверка ',
        )
        Post.objects.bulk_create([
            Post(
                author=cls.user,
                text='Текст. Автотест.',
                group=cls.group_1
            ) for i in range(TEST_POSTS_COUNT)
        ])
        cls.first_post = Post.objects.all().first()
        cls.CALC_URLS = {
            'posts:post_edit': reverse(
                'posts:post_edit', args=[cls.first_post.id]
            ),
            'posts:post_detail': reverse(
                'posts:post_detail', args=[cls.first_post.id]
            )
        }
        cls.routes = {**cls.CALC_URLS, **CONST_URLS}

    def setUp(self):
        # Клиент незалогиненного пользователя
        self.guest_client = Client()
        # Клиент залогиненного пользователя
        self.auth_client = Client()
        self.auth_client.force_login(ContextViewsTest.user)
        self.test_group = ContextViewsTest.group_1

    def test_paginator(self):
        urls = [
            # Первая страница
            (ContextViewsTest.routes['posts:index'], posts_on_first_page),
            (ContextViewsTest.routes['posts:group_list'], posts_on_first_page),
            (ContextViewsTest.routes['posts:profile'], posts_on_first_page),
            # Последняя страница
            (
                ContextViewsTest.routes['posts:index']
                + f"?page={total_pages}",
                posts_on_last_page
            ),
            (
                ContextViewsTest.routes['posts:group_list']
                + f"?page={total_pages}",
                posts_on_last_page
            ),
            (
                ContextViewsTest.routes['posts:profile']
                + f"?page={total_pages}",
                posts_on_last_page
            ),

        ]
        for url in urls:
            with self.subTest(url[0]):
                response = self.guest_client.get(url[0])
                self.assertEqual(
                    len(response.context['page_obj']), url[1],
                    (
                        f'Wrong posts number on <{url[0]}> '
                        f'Expected: {url[1]} '
                        f'Got: {len(response.context["page_obj"])}'
                    )
                )

    def test_correct_context_post_lists(self):
        urls = [
            ('posts:index', 'page_obj'),
            ('posts:group_list', 'page_obj'),
            ('posts:profile', 'page_obj'),
            ('posts:post_detail', 'post'),
        ]
        for url in urls:
            with self.subTest(url[0]):
                response = self.auth_client.get(
                    ContextViewsTest.routes[url[0]]
                ).context[url[1]]
                if isinstance(response, Post):
                    response = [response]
                for post in response:
                    self.assertEqual(
                        post.text, ContextViewsTest.first_post.text,
                        (
                            f'<{url[0]}>. Wrong post text '
                            f'Expected: "{ContextViewsTest.first_post.text}" '
                            f'Got: "{post.text}"'
                        )
                    )
                    self.assertEqual(
                        post.author, ContextViewsTest.first_post.author,
                        (
                            f'<{url[0]}>. Wrong post author '
                            f'Expected: {ContextViewsTest.first_post.author} '
                            f'Got: {post.author}'
                        )
                    )
                    self.assertEqual(
                        post.group, ContextViewsTest.first_post.group,
                        (
                            f'<{url[0]}>. Wrong post group '
                            f'Expected: {ContextViewsTest.first_post.group} '
                            f'Got: {post.group}'
                        )
                    )

    def test_post_correct_group(self):
        wrong_group_post = Post.objects.create(
            author=ContextViewsTest.user,
            text='Автотест. Проверка отсутствия не в своей группе',
            group=ContextViewsTest.group_2
        )
        response = self.guest_client.get(
            ContextViewsTest.routes['posts:group_list']
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertNotIn(
            wrong_group_post,
            response.context['page_obj'],
            (
                'Wrong post on group page! '
                f'In group list {ContextViewsTest.group_1} '
                f'found post of {ContextViewsTest.group_2}'
            )
        )

    def test_context_post_create_edit(self):
        urls = [
            ('posts:post_create', ['form']),
            ('posts:post_edit', ['form', 'post']),
        ]
        for url in urls:
            response = self.auth_client.get(
                ContextViewsTest.routes[url[0]]
            )
            for context_item in url[1]:
                with self.subTest(url[0]):
                    self.assertIn(
                        context_item,
                        response.context,
                        f'{context_item} not found in {url[0]} context'
                    )
