from http import HTTPStatus

from django import forms
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Post, Group, User

TEST_GROUP_SLUG = 'TestGroupSlug'
TEST_GROUP_SLUG_1 = 'TestGroupSlug1'
AUTOTEST_AUTH_USERNAME = 'AutoTestUser'

CONST_URLS = {
    'posts:post_create': reverse('posts:post_create'),
    'posts:profile': reverse('posts:profile', args=[AUTOTEST_AUTH_USERNAME]),

}


class PostCreateFormTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # клиент с правом создания записи
        cls.user = User.objects.create_user(username=AUTOTEST_AUTH_USERNAME)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug=TEST_GROUP_SLUG,
            description='Тестовое описание',
        )
        cls.group1 = Group.objects.create(
            title='Тестовая группа 2 ',
            slug=TEST_GROUP_SLUG_1,
            description='Тестовое описание 2',
        )
        cls.first_post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовый пост, созданный в фикстурах'
        )
        cls.form = PostForm()
        cls.CALC_RELATIVE_URLS = {
            'posts:post_edit': reverse(
                'posts:post_edit', args=[cls.first_post.id]
            ),
            'posts:post_detail': reverse(
                'posts:post_detail', args=[cls.first_post.id]
            )
        }
        cls.routes = {**cls.CALC_RELATIVE_URLS, **CONST_URLS}

    def setUp(self):
        self.user = PostCreateFormTest.user
        self.auth_client = Client()
        self.auth_client.force_login(self.user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def test_post_create(self):
        posts_before = set(Post.objects.all())
        form_data = {
            'text': 'Текст тестового поста',
            'group': PostCreateFormTest.group.id
        }
        response = self.auth_client.post(
            PostCreateFormTest.routes['posts:post_create'],
            data=form_data,
            follow=True
        )
        posts_after = set(Post.objects.all())
        # созданный пост как разница двух кверисетов
        new_posts = list(posts_after.difference(posts_before))
        self.assertEqual(len(new_posts), 1, '0 or 2 and more post created')
        new_post = new_posts[0]
        self.assertEqual(
            new_post.author, PostCreateFormTest.user,
            'Created post has a wrong author'
        )
        self.assertEqual(
            new_post.group.id, form_data['group'],
            'Created post has a wrong group'
        )
        self.assertEqual(
            new_post.text, form_data['text'],
            'Created post has a wrong text'
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(
            response,
            PostCreateFormTest.routes['posts:profile'],
        )

    def test_post_edit(self):
        posts_total = Post.objects.count()
        form_data = {
            'text': 'Текст обновленного тестового поста',
            'group': PostCreateFormTest.group1.id
        }
        response = self.auth_client.post(
            PostCreateFormTest.routes['posts:post_edit'],
            data=form_data,
            follow=True
        )
        self.assertEqual(
            Post.objects.count(), posts_total,
            'Number of posts changed after post editing'
        )
        edited_post = Post.objects.filter(
            id=PostCreateFormTest.first_post.id
        ).first()
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(
            response,
            PostCreateFormTest.routes['posts:post_detail'],
        )
        self.assertEqual(
            edited_post.author, PostCreateFormTest.user,
            'Edited post has a wrong author'
        )
        self.assertEqual(
            edited_post.group.id, form_data['group'],
            'Edited post has a wrong group'
        )
        self.assertEqual(
            edited_post.text, form_data['text'],
            'Edited post has a wrong text'
        )

    def test_correct_form_create_edit(self):
        urls = [
            'posts:post_create',
            'posts:post_edit',
        ]
        for url in urls:
            form = self.auth_client.get(
                PostCreateFormTest.routes[url]
            ).context['form']
            with self.subTest(url[0]):
                self.assertIsInstance(
                    form.fields.get('text'),
                    forms.fields.CharField
                )
                self.assertIsInstance(
                    form.fields.get('group'),
                    forms.fields.ChoiceField
                )
