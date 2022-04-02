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
        # Создание 17 постов с пагинацией по 10 от тестового автора в тестовой группе.
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

    def test_correct_context(self):
        for page in pages:
            response = self.auth_client.get(page.reverse)
            # Проверка контекста главной
            if page.address == 'posts:index':
                test_objs = response.context['page_obj']
                for post in test_objs:
                    self.assertEqual(post.text, 'Текст. Автотест')
                    self.assertEqual(post.author, self.user)
                    self.assertEqual(post.group, self.test_group)
                continue
            # Проверка контекста страницы группы
            if page.address == 'posts:group_list':
                group_posts_obj = response.context['page_obj']
                for post in group_posts_obj:
                    self.assertEqual(post.group, self.test_group)
                continue
            # Проверка контекста профиля
            if page.address == 'posts:profile':
                profile_posts_obj = response.context['page_obj']
                reference_obj = Post.objects.filter(author=self.user).first()
                for post in profile_posts_obj:
                    self.assertEqual(post.author, reference_obj.author)
                continue
            # Проверка контекста подробностей о посте
            if page.address == 'posts:post_detail':
                refernce_obj = Post.objects.all().last()
                post = response.context['post']
                self.assertEqual(post.id, refernce_obj.id)
                continue
            # Проверка контекста страницы создания поста
            if page.address == 'posts:post_create':
                form = response.context['form']
                self.assertIsInstance(form.fields.get('text'), forms.fields.CharField)
                self.assertIsInstance(form.fields.get('group'), forms.fields.ChoiceField)
                continue
            # Проверка контекста старницы редактирования поста
            if page.address == 'posts:post_edit':
                refernce_obj = Post.objects.all().last()
                post = response.context['post']
                form = response.context['form']
                self.assertEqual(post.id, refernce_obj.id)
                self.assertIsInstance(form.fields.get('text'), forms.fields.CharField)
                self.assertIsInstance(form.fields.get('group'), forms.fields.ChoiceField)
                continue

    def test_post_correct_group(self):
        response = self.auth_client.get(reverse(
            'posts:group_list', kwargs={'slug': TEST_GROUP_SLUG_1})
        )
        group_posts_obj = response.context['page_obj']
        self.assertEqual(response.status_code, HTTPStatus.OK)
        # При создании 17 постов ни один не попал в группу без постов
        self.assertEqual(len(group_posts_obj), 0)
