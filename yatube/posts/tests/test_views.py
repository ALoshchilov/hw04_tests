from http import HTTPStatus

from django import forms
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, Group
from posts.tests.settings import (
    pages, TEST_GROUP_SLUG, TEST_GROUP_SLUG_1, AUTOTEST_AUTH_USERNAME
)

User = get_user_model()


# Проверка Namespace
class PostViewsTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=AUTOTEST_AUTH_USERNAME)
        cls.group = Group.objects.create(
            title='Тестовая группа. Заголовок',
            slug=TEST_GROUP_SLUG,
            description='Тестовая группа. Описание',
        )
        Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Текст. Автотест',
        )

    def setUp(self):
        # Клиент незалогиненного пользователя
        self.guest_client = Client()
        # Клиент залогиненного пользователя
        self.user = PostViewsTest.user
        self.auth_client = Client()
        self.auth_client.force_login(self.user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def test_expected_templates(self):
        for page in pages:
            with self.subTest(page.reverse):
                self.assertTemplateUsed(
                    self.auth_client.get(page.reverse),
                    page.template
                )


class ContextViewsTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=AUTOTEST_AUTH_USERNAME)
        cls.group_1 = Group.objects.create(
            title='Тестовая группа. Заголовок',
            slug=TEST_GROUP_SLUG,
            description='Тестовая группа. Описание',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа. Заголовок',
            slug=TEST_GROUP_SLUG_1,
            description='Тестовая группа. Должна быть пустой',
        )
        # Создание 17 постов с пагинацией по 10 от тестового автора
        # в тестовой группе.
        # Таким образом можно проверить одной функцией пагинацию:
        # на главной странице, странице профиля и странице группы
        for i in range(17):
            Post.objects.create(
                author=cls.user,
                text='Текст. Автотест',
                group=cls.group_1
            )

    def setUp(self):
        # Клиент незалогиненного пользователя
        self.guest_client = Client()
        # Клиент залогиненного пользователя
        self.user = ContextViewsTest.user
        self.auth_client = Client()
        self.auth_client.force_login(self.user)
        self.test_group = ContextViewsTest.group_1

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    # Проверка пагинации
    def test_first_page_contains_ten_records(self):
        for page in [page for page in pages if page.paginated]:
            with self.subTest(page.template):
                response = self.guest_client.get(page.reverse)
                # Проверка: количество постов на первой странице равно 10.
                self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_seven_records(self):
        # Проверка: на второй странице должно быть семь постов.
        for page in [page for page in pages if page.paginated]:
            with self.subTest(page.template):
                response = self.guest_client.get(page.reverse + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 7)

    # Здесь была функция для проверки всех страниц в одном цикле,
    # но она не прошла линтеры из-за сложности. RIP
    # Ниже её потомки для каждой страницы
    def test_correct_context_index(self):
        for page in [page for page in pages if page.address == 'posts:index']:
            for post in self.auth_client.get(page.reverse).context['page_obj']:
                self.assertEqual(post.text, 'Текст. Автотест')
                self.assertEqual(post.author, self.user)
                self.assertEqual(post.group, self.test_group)

    def test_correct_context_group(self):
        for page in (
            [page for page in pages if page.address == 'posts:group_list']
        ):
            for post in self.auth_client.get(page.reverse).context['page_obj']:
                self.assertEqual(post.group, self.test_group)

    def test_correct_context_profile(self):
        reference_obj = Post.objects.filter(author=self.user).first()
        for page in (
            [page for page in pages if page.address == 'posts:profile']
        ):
            for post in self.auth_client.get(page.reverse).context['page_obj']:
                self.assertEqual(post.author, reference_obj.author)

    def test_correct_context_post_detail(self):
        refernce_obj = Post.objects.all().last()
        for page in (
            [page for page in pages if page.address == 'posts:post_detail']
        ):
            self.assertEqual(
                self.auth_client.get(page.reverse).context['post'].id,
                refernce_obj.id
            )

    def test_correct_context_post_create(self):
        for page in (
            [page for page in pages if page.address == 'posts:post_create']
        ):
            form = self.auth_client.get(page.reverse).context['form']
            self.assertIsInstance(
                form.fields.get('text'),
                forms.fields.CharField
            )
            self.assertIsInstance(
                form.fields.get('group'),
                forms.fields.ChoiceField
            )

    def test_correct_context_edit(self):
        for page in (
            [page for page in pages if page.address == 'posts:post_edit']
        ):
            form = self.auth_client.get(page.reverse).context['form']
            self.assertIsInstance(
                form.fields.get('text'),
                forms.fields.CharField
            )
            self.assertIsInstance(
                form.fields.get('group'),
                forms.fields.ChoiceField
            )

    def test_post_correct_group(self):
        response = self.auth_client.get(reverse(
            'posts:group_list', kwargs={'slug': TEST_GROUP_SLUG_1})
        )
        group_posts_obj = response.context['page_obj']
        self.assertEqual(response.status_code, HTTPStatus.OK)
        # При создании 17 постов ни один не попал в группу без постов
        self.assertEqual(len(group_posts_obj), 0)
