from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Модель пользователя."""

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name',
                       'last_name', 'password']

    EMAIL_MAX_LENGTH = 254
    FIELD_MAX_LENGTH = 150

    email = models.EmailField(
        _('Электронная почта'),
        unique=True,
        max_length=EMAIL_MAX_LENGTH
    )
    username = models.CharField(
        _('Юзернейм'),
        max_length=FIELD_MAX_LENGTH,
    )
    first_name = models.CharField(
        _('Имя'),
        max_length=FIELD_MAX_LENGTH
    )
    last_name = models.CharField(
        _('Фамилия'),
        max_length=FIELD_MAX_LENGTH
    )
    avatar = models.ImageField(
        _('Аватар'),
        null=True,
        upload_to='avatars'
    )

    class Meta:
        ordering = ('username',)
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """Модель подписок."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name=_('Подписчик')
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name=_('Автор')
    )

    class Meta:
        verbose_name = _('Подписка')
        verbose_name_plural = _('Подписки')
        unique_together = ('user', 'author')

    def __str__(self):
        return f"Подписка {self.user.username} на {self.author.username}"
