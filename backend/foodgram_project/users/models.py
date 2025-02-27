from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models


class User(AbstractUser):
    """Модель пользователя."""

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name',
                       'last_name')

    email = models.EmailField(
        verbose_name='Электронная почта',
        unique=True,
        max_length=settings.EMAIL_MAX_LENGTH
    )
    username = models.CharField(
        verbose_name='Имя пользователя',
        unique=True,
        validators=[UnicodeUsernameValidator()],
        max_length=settings.FIELD_MAX_LENGTH,
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=settings.FIELD_MAX_LENGTH
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=settings.FIELD_MAX_LENGTH
    )
    avatar = models.ImageField(
        verbose_name='Аватар',
        null=True,
        default=None,
        blank=True,
        upload_to='avatars'
    )

    class Meta:
        ordering = 'username',
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """Модель подписок."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Автор',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        unique_together = ('user', 'author')
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_subscriptions_model'
            )
        ]

    def __str__(self):
        return f'Подписка {self.user.username} на {self.author.username}'
