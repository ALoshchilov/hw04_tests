from django.test import TestCase

from posts.models import Group, Post, User


class PostModelTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост_1234567890',
        )

    def test_models_have_correct_object_names(self):
        """Тест корректной работы метода __str__ у моделей."""
        self.assertEqual(
            str(self.post),
            self.post.text[:15]
        )

    def test_models_have_correct_helptext(self):
        """Тест наличия подсказок"""
        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Post._meta.get_field(field).help_text, expected_value)

    def test_models_have_correct_verbosename(self):
        """Тест наличия удобочитаемых имен"""
        field_verbose_names = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for field, expected_value in field_verbose_names.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Post._meta.get_field(field).verbose_name,
                    expected_value
                )
