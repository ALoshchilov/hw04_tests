from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

AUTOTEST_AUTH_USERNAME = 'AutoTestUser'
FIRST_POST_ID = 1
NOT_AUTHOR = 'NotAuthor'
TEST_GROUP_SLUG = 'TestGroupSlug'
TEST_GROUP_SLUG_1 = 'TestGroupSlug1'
UNEXISTING_PAGE_URL = '/ThisPageIsALieAndTheTestAsWell/'
pages = []


class Page:
    """
    Класс для создания объектов, хранящих всю необходимую информацию для тестируемых страниц.
    В случае добавления страниц в проект достаточно создать дополнителньый объект класса Page.
    На основании атрибутов класса будут определены необходимые автотесты за исключением проверки контекста.
    Проверку контекста для новой страницы необходимо добавить в модуле posts.tests.test_views
    Имя функции должно соответствовать паттерну test_correct_context_<адрес_новой_страницы>
    """
    def __init__(self, template, url, address, permissions, paginated, reverse_args=None):
        self.template = template
        self.url = url
        self.address = address
        self.permissions = permissions
        self.paginated = paginated
        self.reverse = reverse(address, kwargs=reverse_args)


index = Page(
    template='posts/index.html',
    url='/',
    address='posts:index',
    permissions=['All', 'Auth'],
    paginated=True,
)
pages.append(index)
group = Page(
    template='posts/group_list.html',
    url=f'/group/{TEST_GROUP_SLUG}/',
    address='posts:group_list',
    permissions=['All', 'Auth'],
    paginated=True,
    reverse_args={'slug': TEST_GROUP_SLUG},
)
pages.append(group)
profile = Page(
    template='posts/profile.html',
    url=f'/profile/{AUTOTEST_AUTH_USERNAME}/',
    address='posts:profile',
    permissions=['All', 'Auth'],
    paginated=True,
    reverse_args={'username': AUTOTEST_AUTH_USERNAME},
)
pages.append(profile)
post = Page(
    template='posts/post_detail.html',
    url=f'/posts/{FIRST_POST_ID}/',
    address='posts:post_detail',
    permissions=['All', 'Auth'],
    paginated=False,
    reverse_args={'post_id': FIRST_POST_ID},
)
pages.append(post)
create = Page(
    template='posts/create_post.html',
    url='/create/',
    address='posts:post_create',
    permissions=['Auth'],
    paginated=False
)
pages.append(create)
edit = Page(
    template='posts/create_post.html',
    url=f'/posts/{FIRST_POST_ID}/edit/',
    address='posts:post_edit',
    permissions=['Author'],
    paginated=False,
    reverse_args={'post_id': FIRST_POST_ID}
)
pages.append(edit)
author = Page(
    template='about/author.html',
    url='/about/author/',
    address='about:author',
    permissions=['All', 'Auth'],
    paginated=False,
)
pages.append(author)
tech = Page(
    template='about/tech.html',
    url='/about/tech/',
    address='about:tech',
    permissions=['All', 'Auth'],
    paginated=False,
)
pages.append(tech)
