from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('about/', include('about.urls', namespace='about')),
    # Встроенная админка Django
    path('admin/', admin.site.urls, name='admin'),
    # urls для кастомного приложения users
    path('auth/', include('users.urls', namespace='users')),
    # urls модуля для управления пользователями
    path('auth/', include('django.contrib.auth.urls')),
    # Главная страница
    path('', include('posts.urls', namespace='posts')),
]
