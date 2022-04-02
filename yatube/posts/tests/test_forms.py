from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Post, Group
from posts.tests.settings import TEST_GROUP_SLUG, AUTOTEST_AUTH_USERNAME

User = get_user_model()


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
        Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовый пост, созданный в фикстурах'
        )        
        cls.form = PostForm()

    def setUp(self):
        self.user = PostCreateFormTest.user
        self.auth_client = Client()
        self.auth_client.force_login(self.user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def test_post_create(self):
        posts_total = Post.objects.count()
        post = Post.objects.all().first()
        form_data = {
            'text': 'Текст тестового поста',
        }
        response = self.auth_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(
            response, 
            reverse('posts:profile', kwargs={'username': AUTOTEST_AUTH_USERNAME}),
        )
        self.assertEqual(Post.objects.count(), posts_total+1)
        self.assertTrue(
            Post.objects.filter(
                id=post.id + 1,
                text='Текст тестового поста',
            )
        )
    
    def test_post_edit(self):
        posts_total = Post.objects.count()
        post = Post.objects.all().first()    
        form_data = {
            'text': 'Обновленный текст тестового поста',
        }
        response = self.auth_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(
            response, 
            reverse('posts:post_detail', kwargs={'post_id': post.id}),
        )
        self.assertEqual(Post.objects.count(), posts_total)
        self.assertTrue(
            Post.objects.filter(
                id=1,
                text='Обновленный текст тестового поста',
            )
        )
