from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from posts.models import Post, Group
from posts.tests.settings import (
    pages, UNEXISTING_PAGE_URL, NOT_AUTHOR,
    TEST_GROUP_SLUG, AUTOTEST_AUTH_USERNAME
)

User = get_user_model()


class StaticUrlTest(TestCase):

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
        self.user = StaticUrlTest.user
        self.auth_client = Client()
        self.auth_client.force_login(self.user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    # Проверяет прямой доступ по ссылке к урл с разрешением для всех
    def test_guest_user_direct_access(self):
        for page in [page for page in pages if 'All' in page.permissions]:
            with self.subTest(page.url):
                self.assertEqual(
                    self.guest_client.get(page.url).status_code,
                    HTTPStatus.OK,
                    f'{page.template} is not accessible for guest user'
                )

    # Проверяет редиректы по ссылкам с урл, доступ к которым не разрешен всем
    def test_guest_user_redirect(self):
        for page in [page for page in pages if 'All' not in page.permissions]:
            with self.subTest(page.url):
                self.assertRedirects(
                    self.guest_client.get(page.url, follow=True),
                    f'/auth/login/?next={page.url}',
                    msg_prefix=(
                        f'Expected redirect ({page.url})'
                        ' ---> (/auth/login/?next={page.url})'
                    )
                )

    # Проверяет прямой доступ ко всем ссылкам для авторизованного пользователя
    def test_auth_user_direct_access(self):
        for page in [page for page in pages if 'Auth' in page.permissions]:
            with self.subTest(page.url):
                self.assertEqual(
                    self.auth_client.get(page.url).status_code,
                    HTTPStatus.OK,
                    f'{page.template} does not accessible for authorized user'
                )

    # Тест доступа к несуществующей странице
    def test_unexisting_page(self):
        self.assertEqual(
            self.guest_client.get(UNEXISTING_PAGE_URL).status_code,
            HTTPStatus.NOT_FOUND,
            f'Unexisting page {UNEXISTING_PAGE_URL} does not return 404'
        )

    # Тест доступа "не автора" к редактированию
    def test_auth_not_author_direct_access(self):
        self.not_author = User.objects.create_user(username=NOT_AUTHOR)
        self.not_author_client = Client()
        self.not_author_client.force_login(self.not_author)

        for page in [page for page in pages if 'Author' in page.permissions]:
            with self.subTest(page.url):
                self.assertNotEqual(
                    self.not_author_client.get(page.url).status_code,
                    HTTPStatus.OK,
                    f'Not author has access by {page.template}'
                )

    def test_correct_template(self):
        for page in [page for page in pages if 'Auth' in page.permissions]:
            with self.subTest(page.url):
                self.assertTemplateUsed(
                    self.auth_client.get(page.url),
                    page.template
                )
