from django.contrib.auth.models import AbstractUser
from django.db import models as dbmodels


class User(AbstractUser):

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name',
                       'last_name', 'password']
    email = dbmodels.EmailField(unique=True)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
