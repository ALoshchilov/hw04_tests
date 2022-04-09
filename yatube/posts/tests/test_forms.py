from django import forms
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, Group, User

SLUG = 'TestGroupSlug'
SLUG_1 = 'TestGroupSlug1'
NICK = 'AutoTestUser'
POST_CREATE_URL = reverse('posts:post_create')
PROFILE_URL = reverse('posts:profile', args=[NICK])


class PostCreateFormTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=NICK)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug=SLUG,
            description='Тестовое описание',
        )
        cls.group1 = Group.objects.create(
            title='Тестовая группа 2 ',
            slug=SLUG_1,
            description='Тестовое описание 2',
        )
        cls.ref_post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовый пост, созданный в фикстурах'
        )
        cls.POST_EDIT_URL = reverse(
            'posts:post_edit', args=[cls.ref_post.id]
        )
        cls.POST_DETAIL_URL = reverse(
            'posts:post_detail', args=[cls.ref_post.id]
        )

    def setUp(self):
        self.author = Client()
        self.author.force_login(self.user)

    def test_post_create_form(self):
        """Тест формы создания поста"""
        posts_before = set(Post.objects.all())
        form_data = {
            'text': 'Текст тестового поста',
            'group': self.group.id
        }
        response = self.author.post(
            POST_CREATE_URL,
            data=form_data,
            follow=True
        )
        posts_after = set(Post.objects.all())
        posts = posts_after.difference(posts_before)
        self.assertEqual(len(posts), 1, '0 or 2 and more post created')
        post = posts.pop()
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group.id, form_data['group'])
        self.assertEqual(post.text, form_data['text'])
        self.assertRedirects(response, PROFILE_URL)

    def test_post_edit_form(self):
        """Тест формы редактирования поста"""
        posts_total = Post.objects.count()
        form_data = {
            'text': 'Текст обновленного тестового поста',
            'group': self.group1.id
        }
        response = self.author.post(
            self.POST_EDIT_URL, data=form_data, follow=True
        )
        post = response.context['post']
        self.assertIsInstance(post, Post)
        self.assertEqual(
            Post.objects.count(), posts_total,
            'Number of posts changed after post editing'
        )
        self.assertRedirects(response, self.POST_DETAIL_URL)
        self.assertEqual(post.author, self.ref_post.author)
        self.assertEqual(post.group.id, form_data['group'])
        self.assertEqual(post.text, form_data['text'])

    def test_correct_form_post_create_edit(self):
        """Тест типов полей формы создания/редактирования поста"""
        urls = [
            POST_CREATE_URL,
            self.POST_EDIT_URL,
        ]
        for url in urls:
            form = self.author.get(url).context['form']
            with self.subTest(url=url, form=form):
                self.assertIsInstance(
                    form.fields.get('text'), forms.fields.CharField
                )
                self.assertIsInstance(
                    form.fields.get('group'), forms.fields.ChoiceField
                )
