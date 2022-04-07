from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, Group, User
from posts.settings import POSTS_ON_PAGE

SLUG = 'TestGroupSlug'
SLUG_1 = 'TestGroupSlug1'
NICK = 'AutoTestUser'
INDEX_URL = reverse('posts:index')
POST_CREATE_URL = reverse('posts:post_create')
USER_LOGIN_URL = reverse('users:login')
PROFILE_URL = reverse('posts:profile', args=[NICK])
GROUP_URL = reverse('posts:group_list', args=[SLUG])
GROUP_URL_1 = reverse('posts:group_list', args=[SLUG_1])
TEST_POSTS_COUNT = POSTS_ON_PAGE + 1


class ContextViewsTest(TestCase):

    @classmethod
    def setUpClass(cls):

        super().setUpClass()
        cls.user = User.objects.create_user(username=NICK)
        cls.group_1 = Group.objects.create(
            title='Тестовая группа 1. Заголовок',
            slug=SLUG,
            description='Тестовая группа 1. Описание',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа 2. Заголовок',
            slug=SLUG_1,
            description='Тестовая группа 2. Проверка ',
        )
        Post.objects.bulk_create(
            Post(
                author=cls.user,
                text=f'Текст. Автотест. Пост № {i}',
                group=cls.group_1
            ) for i in range(TEST_POSTS_COUNT)
        )
        cls.ref_post = Post.objects.all().first()
        cls.POST_EDIT_URL = reverse('posts:post_edit', args=[cls.ref_post.id])
        cls.POST_DETAIL_URL = reverse(
            'posts:post_detail', args=[cls.ref_post.id]
        )

    def setUp(self):
        # Клиент незалогиненного пользователя
        self.guest = Client()
        # Клиент залогиненного пользователя
        self.author = Client()
        self.author.force_login(self.user)

    def test_paginator(self):
        CASES = [
            # Первая страница
            (INDEX_URL, POSTS_ON_PAGE),
            (GROUP_URL, POSTS_ON_PAGE),
            (PROFILE_URL, POSTS_ON_PAGE),
            # Последняя страница
            (f'{INDEX_URL}?page=2', 1),
            (f'{GROUP_URL}?page=2', 1),
            (f'{PROFILE_URL}?page=2', 1),

        ]
        for url, posts_count in CASES:
            with self.subTest(url=url, posts_count=posts_count):
                self.assertEqual(
                    len(self.guest.get(url).context['page_obj']),
                    posts_count
                )

    def test_correct_post_in_lists(self):
        CASES = [
            (INDEX_URL, 'page_obj'),
            (GROUP_URL, 'page_obj'),
            (PROFILE_URL, 'page_obj'),
            (self.POST_DETAIL_URL, 'post'),
        ]
        for url, obj in CASES:
            response = self.author.get(url).context[obj]
            with self.subTest(url=url, posts_obj=obj):
                if isinstance(response, Post):
                    post = response
                else:
                    self.assertIn(self.ref_post, response)
                    post = response.object_list[
                        response.object_list.index(self.ref_post)
                    ]
                self.assertEqual(post.author, self.ref_post.author)
                self.assertEqual(post.pub_date, self.ref_post.pub_date)
                self.assertEqual(post.group, self.ref_post.group)
                self.assertEqual(post.text, self.ref_post.text)

    def test_post_correct_group(self):
        self.assertNotIn(
            self.ref_post,
            self.guest.get(GROUP_URL_1).context['page_obj']
        )

    def test_context_post_create_edit(self):
        CASES = [
            (POST_CREATE_URL, ['form']),
            (self.POST_EDIT_URL, ['form', 'post']),
            (PROFILE_URL, ['author']),
            (GROUP_URL, ['group']),
        ]
        for url, context in CASES:
            response = self.author.get(url)
            for context_item in context:
                with self.subTest(url=url, context=context):
                    self.assertIn(context_item, response.context)
